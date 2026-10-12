"""Group simple message templates and create deterministic approximate 70/15/15 splits."""
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 42
RATIOS = {'train': 0.70, 'validation': 0.15, 'test': 0.15}


def template_key(text):
    text = text.lower()
    text = re.sub(r'(?:https?://|www\.)\S+', ' urltoken ', text)
    text = re.sub(r'\b[^\s@]+@[^\s@]+\.[^\s@]+\b', ' emailtoken ', text)
    text = re.sub(r'\d+', ' numbertoken ', text)
    tokens = re.findall(r'\w+', text, flags=re.UNICODE)
    # Keep punctuation-only messages distinct instead of collapsing to an empty key.
    return ' '.join(tokens) if tokens else ' '.join(text.split())


def split_rows(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[template_key(row['text'])].append(row)
    rng = random.Random(SEED)
    ordered = sorted(groups.items())
    rng.shuffle(ordered)
    ordered.sort(key=lambda entry: len(entry[1]), reverse=True)
    total = Counter(row['label'] for row in rows)
    counts = {name: Counter() for name in RATIOS}
    result = {name: [] for name in RATIOS}
    manifest = []
    for key, members in ordered:
        gc = Counter(row['label'] for row in members)
        # Minimize the increase in class-count squared error, normalized by
        # each partition's target. Never break groups to force exact ratios.
        def cost(name):
            return sum(
                ((counts[name][label] + gc[label] - total[label] * RATIOS[name]) ** 2
                 - (counts[name][label] - total[label] * RATIOS[name]) ** 2)
                / max(total[label] * RATIOS[name], 1)
                for label in total
            )
        name = min(RATIOS, key=lambda part: (cost(part), list(RATIOS).index(part)))
        gid = hashlib.sha256(key.encode()).hexdigest()
        for row in members:
            result[name].append({**row, 'group_id': gid})
            manifest.append({'id': row['id'], 'group_id': gid, 'split': name})
        counts[name].update(gc)
    for part in result.values():
        part.sort(key=lambda row: row['id'])
    manifest.sort(key=lambda row: row['id'])
    report = {
        'seed': SEED,
        'target_ratios': RATIOS,
        'messages': len(rows),
        'template_groups': len(groups),
        'multi_message_groups': sum(len(g) > 1 for g in groups.values()),
        'messages_in_multi_message_groups': sum(len(g) for g in groups.values() if len(g) > 1),
        'largest_group': max(map(len, groups.values()), default=0),
        'mixed_label_groups': sum(len({r['label'] for r in g}) > 1 for g in groups.values()),
        'splits': {
            name: {'messages': len(part), 'class_counts': dict(sorted(counts[name].items())),
                   'fraction': len(part) / len(rows) if rows else 0}
            for name, part in result.items()
        },
        'policy': 'Lowercase; replace explicit URLs, emails, and digit runs with placeholders; compare word-token sequences ignoring punctuation; keep each template group in one partition. Preserve all original message text and labels.',
        'limitations': 'Heuristic template grouping can overgroup and does not detect all paraphrases, unprefixed domains, or changed phone-number formatting. It is not proof of zero semantic overlap.',
    }
    return result, manifest, report


def main():
    source = ROOT / 'data/processed/messages.jsonl'
    raw = source.read_bytes()
    rows = [json.loads(line) for line in raw.decode('utf-8').splitlines()]
    assert len({r['id'] for r in rows}) == len(rows), 'Duplicate input IDs'
    splits, manifest, report = split_rows(rows)
    report['input_sha256'] = hashlib.sha256(raw).hexdigest()
    all_ids = [r['id'] for part in splits.values() for r in part]
    assert len(all_ids) == len(set(all_ids)) == len(rows)
    group_sets = {name: {r['group_id'] for r in part} for name, part in splits.items()}
    for i, name in enumerate(RATIOS):
        for other in list(RATIOS)[i + 1:]:
            assert not group_sets[name] & group_sets[other], 'Template crosses partitions'
    report['verified_id_overlap'] = 0
    report['verified_template_overlap'] = 0
    out = ROOT / 'data/splits'
    out.mkdir(parents=True, exist_ok=True)
    for name, part in {**splits, 'manifest': manifest}.items():
        (out / f'{name}.jsonl').write_text(
            ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in part), encoding='utf-8')
    report['split_sha256'] = {
        name: hashlib.sha256((out / f'{name}.jsonl').read_bytes()).hexdigest() for name in splits
    }
    (out / 'split-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
