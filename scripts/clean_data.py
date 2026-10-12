"""Validate and conservatively deduplicate the SMS corpus using only stdlib."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def clean(raw):
    groups = defaultdict(list)
    invalid = []
    rows = []
    lines = raw.decode('utf-8-sig').splitlines()
    for line_number, line in enumerate(lines, 1):
        parts = line.split('\t', 1)
        if len(parts) != 2:
            invalid.append({'source_line': line_number, 'reason': 'missing tab separator'})
            continue
        label, message = parts
        if label not in ('ham', 'spam') or not message.strip():
            invalid.append({'source_line': line_number, 'reason': 'invalid label or empty message'})
            continue
        # This key is for duplicate detection only. Preserve the original text.
        key = ' '.join(message.lower().split())
        row = {'label': label, 'text': message, 'source_line': line_number}
        rows.append(row)
        groups[key].append(row)

    cleaned, conflicts = [], []
    duplicate_rows_removed = 0
    for key, members in groups.items():
        source_lines = [m['source_line'] for m in members]
        if len({m['label'] for m in members}) != 1:
            conflicts.append({'source_lines': source_lines, 'labels': sorted({m['label'] for m in members})})
            continue
        first = members[0]
        cleaned.append({
            'id': hashlib.sha256(key.encode('utf-8')).hexdigest(),
            'label': first['label'],
            'text': first['text'],
            'source_lines': source_lines,
        })
        duplicate_rows_removed += len(members) - 1

    exact_duplicates = len(rows) - len({(r['label'], r['text']) for r in rows})
    report = {
        'source': 'UCI SMS Spam Collection',
        'source_url': 'https://archive.ics.uci.edu/dataset/228/sms+spam+collection',
        'raw_sha256': hashlib.sha256(raw).hexdigest(),
        'input_lines': len(lines),
        'valid_rows': len(rows),
        'raw_class_counts': dict(sorted(Counter(r['label'] for r in rows).items())),
        'invalid_rows': invalid,
        'exact_duplicate_rows': exact_duplicates,
        'duplicate_rows_removed': duplicate_rows_removed,
        'conflicting_groups': conflicts,
        'conflicting_rows_excluded': sum(len(c['source_lines']) for c in conflicts),
        'clean_rows': len(cleaned),
        'clean_class_counts': dict(sorted(Counter(r['label'] for r in cleaned).items())),
        'policy': 'Group by lowercase text with whitespace collapsed; keep first original text for same-label groups; exclude all conflicting-label groups for review.',
        'limitations': 'This does not remove paraphrases or templates with changed numbers or URLs. Review near-duplicate grouping before dataset splitting.',
    }
    assert len(lines) == len(invalid) + len(cleaned) + duplicate_rows_removed + report['conflicting_rows_excluded']
    return cleaned, report


def main():
    raw = (ROOT / 'data/raw/SMSSpamCollection').read_bytes()
    cleaned, report = clean(raw)
    destination = ROOT / 'data/processed'
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'messages.jsonl').write_text(
        ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in cleaned), encoding='utf-8')
    (destination / 'cleaning-report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
