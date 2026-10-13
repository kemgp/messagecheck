"""Prepare source-labeled candidates; never train or read final-test partitions."""
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

from text_v3 import normalize_v3

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    inputs = {}

    def read(path):
        raw = (ROOT / path).read_bytes()
        inputs[path] = sha(raw)
        return raw

    review = json.loads(read('reports/super-sms-notification-review.json'))
    raw = read('data/raw/super_sms_dataset.csv')
    assert sha(raw) == review['source_sha256'], 'Re-review changed source first'
    reviewed = {r['csv_record_including_header'] for r in review['records']}
    source = list(csv.DictReader(io.StringIO(raw.decode('latin-1'), newline='')))
    assert set(source[0]) == {'SMSes', 'Labels'}
    nodes, lookup = [], {}

    def add(text, protected=False):
        norm = normalize_v3(text)
        if norm not in lookup:
            lookup[norm] = len(nodes)
            nodes.append({'norm': norm, 'protected': False, 'records': [], 'reasons': set()})
        node = nodes[lookup[norm]]
        node['protected'] |= protected
        return node

    # Entire previously used corpora are protected, including reserved rows.
    # Only source corpora and ID manifests are read, never final-test partitions.
    for corpus, manifest in [
        ('data/processed/messages.jsonl', 'data/splits/manifest.jsonl'),
        ('data/staging/external-candidates.jsonl', 'data/revision-v3/manifest.jsonl'),
    ]:
        rows = [json.loads(line) for line in read(corpus).decode().splitlines()]
        ids = {r['id'] for r in rows}
        assignments = [json.loads(line) for line in read(manifest).decode().splitlines()]
        assert {r['id'] for r in assignments} <= ids, 'Protected manifest not covered'
        for row in rows:
            add(row['text'], protected=True)
    for row in json.loads(read('data/diagnostics/user-examples.json')):
        add(row['text'], protected=True)
    # Financial Scams was inspected but not adopted; exclude overlaps as well.
    financial = read('data/raw/Financial scams detection dataset.csv').decode('utf-8-sig')
    for row in csv.DictReader(io.StringIO(financial, newline='')):
        add(row['message'], protected=True)

    direct = Counter()
    for number, row in enumerate(source, 2):
        text = row.get('SMSes') or ''
        label = row.get('Labels')
        reasons = set()
        if None in row or label not in ('0', '1'):
            reasons.add('malformed_or_missing_label')
        if not normalize_v3(text):
            reasons.add('empty_normalized_text')
        if any(0x80 <= ord(c) <= 0x9f or ord(c) == 0xfffd for c in text):
            reasons.add('unresolved_encoding_artifacts')
        if number in reviewed:
            reasons.add('previously_reviewed_case')
        direct.update(reasons)
        node = add(text)
        node['reasons'].update(reasons)
        node['records'].append({'csv_record_including_header': number, 'text': text,
                                'source_label': label, 'message_sha256': sha(text.encode())})

    parent = list(range(len(nodes)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a, b):
        a, b = root(a), root(b)
        parent[max(a, b)] = min(a, b)

    inverted = defaultdict(list)
    sizes = []
    edges = []
    for i, node in enumerate(nodes):
        words = node['norm'].split()
        shingles = set(zip(words, words[1:], words[2:]))
        sizes.append(len(shingles))
        if not shingles:
            continue
        overlaps = Counter()
        for shingle in shingles:
            for j in inverted[shingle]:
                if min(sizes[j], len(shingles)) >= .8 * max(sizes[j], len(shingles)):
                    overlaps[j] += 1
        for j, common in overlaps.items():
            if common / (len(shingles) + sizes[j] - common) >= .8:
                union(i, j)
                edges.append((i, j))
        for shingle in shingles:
            inverted[shingle].append(i)
    components = defaultdict(list)
    for i in range(len(nodes)):
        components[root(i)].append(i)
    candidates, audit = [], []
    excluded = Counter()
    retained_nodes = set()
    collapsed = 0
    for members in components.values():
        records = [r for i in members for r in nodes[i]['records']]
        if not records:
            continue
        reasons = set().union(*(nodes[i]['reasons'] for i in members))
        if any(nodes[i]['protected'] for i in members):
            reasons.add('overlap_with_protected_corpus_or_diagnostic')
        if len({r['source_label'] for r in records if r['source_label'] in ('0', '1')}) > 1:
            reasons.add('conflicting_labels_in_template_group')
        group = sha('\n'.join(sorted(nodes[i]['norm'] for i in members)).encode())
        if reasons:
            for reason in reasons:
                excluded[reason] += len(records)
        else:
            for i in members:
                if not nodes[i]['records']:
                    continue
                retained_nodes.add(i)
                originals = nodes[i]['records']
                first = originals[0]
                collapsed += len(originals) - 1
                candidates.append({'id': sha(nodes[i]['norm'].encode()), 'text': first['text'],
                    'label': {'0': 'ham', '1': 'spam'}[first['source_label']],
                    'source_label': first['source_label'], 'group_id': group,
                    'split': 'unassigned', 'label_basis': 'source_label_not_independently_verified',
                    'source_records': [{k: v for k, v in r.items() if k != 'text'} for r in originals]})
        audit.append({'group_id': group, 'source_records': sorted(r['csv_record_including_header'] for r in records),
                      'status': 'excluded' if reasons else 'candidate', 'reasons': sorted(reasons)})
    assert all(root(a) == root(b) for a, b in edges)
    assert len({r['id'] for r in candidates}) == len(candidates)
    assert all(not nodes[i]['protected'] and not nodes[i]['reasons'] for i in retained_nodes)
    assert len({r['csv_record_including_header'] for row in candidates for r in row['source_records']} & reviewed) == 0
    excluded_rows = sum(len(g['source_records']) for g in audit if g['status'] == 'excluded')
    assert excluded_rows + len(candidates) + collapsed == len(source)
    for path, digest in inputs.items():
        assert sha((ROOT / path).read_bytes()) == digest, 'Input changed during preparation'
    out = ROOT / 'data/super-sms-prepared'
    out.mkdir(exist_ok=True)
    for name, rows in [('candidates', sorted(candidates, key=lambda r: r['id'])),
                       ('group-audit', sorted(audit, key=lambda r: r['group_id']))]:
        (out / f'{name}.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
    report = {'source_rows': len(source), 'candidate_rows': len(candidates),
        'candidate_labels': dict(Counter(r['label'] for r in candidates)),
        'candidate_groups': len({r['group_id'] for r in candidates}),
        'excluded_source_rows': excluded_rows, 'normalized_duplicates_collapsed': collapsed,
        'direct_exclusion_flags': dict(direct), 'excluded_rows_by_reason_nonexclusive': dict(excluded),
        'input_sha256': inputs,
        'output_sha256': {p.name: sha(p.read_bytes()) for p in sorted(out.glob('*.jsonl'))},
        'method': 'Equal normalize_v3 text collapsed; connected components of word-trigram set Jaccard >= 0.8, including short texts with at least one trigram. Entire components quarantined on protection, conflict, or exclusion flags.',
        'limitations': ['Source labels preserved, not independently verified.',
            'Latin-1 inspection decoding; C1/replacement characters quarantined, other mojibake may remain.',
            'No English-language guarantee or complete paraphrase detection.',
            'Groups remain unassigned; future splitting must use group_id, never individual rows.',
            'No training, model scoring, final-test partition reading, or changes to existing data.']}
    (ROOT / 'reports/super-sms-preparation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('input_sha256', 'output_sha256')}, indent=2))


if __name__ == '__main__':
    main()
