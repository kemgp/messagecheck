"""Check preparation invariants without reading final-test message contents."""
import hashlib
import json
from collections import Counter
from pathlib import Path
from prepare_v3 import read_jsonl
from text_v3 import normalize_v3

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = read_jsonl(ROOT / 'data/revision-v3/manifest.jsonl')
    assert len({r['id'] for r in manifest}) == len(manifest)
    groups = {}
    for row in manifest:
        assert groups.setdefault(row['group_id'], row['split']) == row['split']
    report = json.loads((ROOT / 'reports/v3-data-preparation.json').read_text())
    counts = Counter(r['split'] for r in manifest)
    assert all(counts[p] == details['rows'] for p, details in report['partitions'].items())
    original = {normalize_v3(r['text']) for r in read_jsonl(ROOT / 'data/processed/messages.jsonl')}
    seen = set()
    for part in ('train', 'validation'):
        path = ROOT / f'data/revision-v3/{part}.jsonl'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == report['sha256'][part]
        for row in read_jsonl(path):
            text = normalize_v3(row['text'])
            assert text and text not in original and text not in seen
            assert row['label'] in ('ham', 'spam')
            assert row['provenance']
            if 'hacked' in text.split():
                assert part == 'train' and row['development_only_group']
            seen.add(text)
    assert normalize_v3('Pay at <URL> within <DATE_TIME> [REDACTED]') == normalize_v3('Pay at https://example.com within 12')
    print('Passed: unique IDs, partition-group separation, counts, hashes, normalized exclusions, provenance, development-only threat groups, placeholder equivalence.')


if __name__ == '__main__':
    main()
