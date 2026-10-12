"""Prepare external grouped partitions without changing legacy splits."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from text_v3 import normalize_v3

ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def main():
    original = read_jsonl(ROOT / 'data/processed/messages.jsonl')
    external = read_jsonl(ROOT / 'data/staging/external-candidates.jsonl')
    counts = Counter()
    eligible = []
    for row in external:
        imc = any(p['source'] == 'imc2025' for p in row['provenance'])
        categories = {p['source_label'] for p in row['provenance']}
        if imc and (categories & {'wrong number', 'hey mum/dad'} or len(normalize_v3(row['text']).split()) < 8):
            counts['excluded_context_dependent_or_short_imc'] += 1
        elif not normalize_v3(row['text']):
            counts['excluded_empty_after_normalization'] += 1
        else:
            eligible.append(row)
    rows = original + eligible
    parent = list(range(len(rows)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a, b):
        a, b = root(a), root(b)
        parent[max(a, b)] = min(a, b)

    exact, inverted, sets = {}, defaultdict(list), []
    for i, row in enumerate(rows):
        text = normalize_v3(row['text'])
        if text in exact:
            union(i, exact[text])
        else:
            exact[text] = i
        words = text.split()
        shingles = {' '.join(words[j:j+3]) for j in range(len(words)-2)}
        sets.append(shingles)
        if len(shingles) < 5:
            continue
        overlap = Counter(j for shingle in shingles for j in inverted[shingle])
        for j, n in overlap.items():
            if n / (len(shingles) + len(sets[j]) - n) >= 0.80:
                union(i, j)
        for shingle in shingles:
            inverted[shingle].append(i)
    components = defaultdict(list)
    for i in range(len(rows)):
        components[root(i)].append(i)
    partitions = {k: [] for k in ('train', 'validation', 'test')}
    manifest = []
    for indices in components.values():
        additions = [i for i in indices if i >= len(original)]
        if not additions:
            continue
        if any(i < len(original) for i in indices):
            counts['excluded_new_normalized_or_near_overlap_with_legacy'] += len(additions)
            continue
        if len({rows[i]['label'] for i in additions}) > 1:
            counts['excluded_mixed_label_component_rows'] += len(additions)
            continue
        by_text = {}
        for i in additions:
            by_text.setdefault(normalize_v3(rows[i]['text']), rows[i])
        counts['normalized_duplicates_collapsed'] += len(additions) - len(by_text)
        group = hashlib.sha256('\n'.join(sorted(by_text)).encode()).hexdigest()
        # Audited hacking examples are already development material; reserve their entire group for training.
        development = any('hacked' in text.split() for text in by_text)
        bucket = int(group[:8], 16) % 100
        part = 'train' if development or bucket < 60 else 'validation' if bucket < 80 else 'test'
        for row in by_text.values():
            entry = {**row, 'group_id': group, 'development_only_group': development}
            partitions[part].append(entry)
            manifest.append({'id': row['id'], 'group_id': group, 'split': part})
    out = ROOT / 'data/revision-v3'
    out.mkdir(exist_ok=True)
    for part, members in partitions.items():
        members.sort(key=lambda r: r['id'])
        (out / f'{part}.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in members))
    (out / 'manifest.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in manifest))
    groups = {part: {r['group_id'] for r in members} for part, members in partitions.items()}
    assert not (groups['train'] & groups['validation'] or groups['train'] & groups['test'] or groups['validation'] & groups['test'])
    report = {'normalization': 'text_v3.normalize_v3; ASCII words, remove bracket artifacts, URLs, emails, digits',
              'grouping': 'Connected components of equal normalized text or word-trigram Jaccard >= 0.80. Not proof against all paraphrases.',
              'split': 'Group SHA-256 bucket: 60/20/20. Already inspected hacking groups assigned to training before evaluation.',
              'excluded': dict(counts), 'partitions': {p: {'rows': len(r), 'labels': dict(Counter(x['label'] for x in r)), 'groups': len(groups[p])} for p, r in partitions.items()},
              'sha256': {p: hashlib.sha256((out / f'{p}.jsonl').read_bytes()).hexdigest() for p in partitions},
              'limitations': 'IMC labels are report-derived, not independently verified. Ambiguous conversation/short-message categories excluded by fixed rule. Source and geographic differences remain.'}
    (ROOT / 'reports/v3-data-preparation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
