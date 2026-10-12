"""Audit supplied CSVs and stage novel candidates; never change models or splits."""
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from split_data import template_key

ROOT = Path(__file__).resolve().parents[1]


def normalized(text):
    return ' '.join(text.lower().split())


def main():
    original = [json.loads(line) for line in
                (ROOT / 'data/processed/messages.jsonl').read_text().splitlines()]
    original_keys = {normalized(row['text']) for row in original}
    original_templates = {template_key(row['text']) for row in original}
    diagnostics = json.loads((ROOT / 'data/diagnostics/user-examples.json').read_text())
    diagnostic_templates = {template_key(row['text']) for row in diagnostics}
    sources = {
        'mendeley': ('Dataset_5971.csv', 'https://data.mendeley.com/datasets/f45bkkt8pr/1'),
        'imc2025': ('final_dataset_output.csv', 'https://github.com/reportsmishing/Smishing-Dataset-IMC25'),
    }
    report = {'sources': {}, 'policy': {
        'existing_corpus': 'Exclude matches against the entire original cleaned corpus, including held-out messages, without computing test predictions or metrics.',
        'labels': 'Mendeley ham maps to ham; spam and smishing map to spam. IMC scam categories provisionally map to spam and need label review.',
        'language': 'Use original English-labeled IMC text only; do not substitute translations. Mendeley has no language field.',
        'duplicates': 'Collapse lowercase/whitespace duplicates; exclude conflicting binary labels. Stage template groups together for future splitting.',
        'status': 'Staging only. No training, new split creation, or final-test evaluation.',
    }}
    candidates = []
    for source, (filename, url) in sources.items():
        path = ROOT / 'data/raw' / filename
        with path.open(encoding='utf-8-sig', newline='') as handle:
            rows = list(csv.DictReader(handle))
        stats = {'file': str(path.relative_to(ROOT)), 'url': url,
                 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                 'rows': len(rows), 'columns': list(rows[0]),
                 'source_labels': dict(Counter(r['LABEL'].lower().strip() if source == 'mendeley'
                                             else r['scam_type'].strip() for r in rows))}
        if source == 'imc2025':
            stats['languages'] = dict(Counter(r['language'] for r in rows))
        counts = Counter()
        for index, row in enumerate(rows, 1):
            if None in row or any(value is None for value in row.values()):
                counts['malformed_rows'] += 1
                continue
            text = row['TEXT' if source == 'mendeley' else 'text'].strip()
            raw_label = row['LABEL' if source == 'mendeley' else 'scam_type'].strip().lower()
            if not text:
                counts['empty_text'] += 1
                continue
            if source == 'imc2025' and row['language'].strip().lower() != 'english':
                counts['excluded_non_english_or_missing_language'] += 1
                continue
            allowed = {'ham', 'spam', 'smishing'} if source == 'mendeley' else {
                'banking', 'others', 'delivery', 'government', 'telecom', 'spam', 'wrong number', 'hey mum/dad'}
            if raw_label not in allowed:
                counts['excluded_unknown_label'] += 1
                continue
            counts['eligible_rows'] += 1
            key = normalized(text)
            template = template_key(text)
            if key in original_keys:
                counts['excluded_original_exact_overlap'] += 1
                continue
            if template in original_templates:
                counts['excluded_original_template_overlap'] += 1
                continue
            if template in diagnostic_templates:
                counts['excluded_user_diagnostic_overlap'] += 1
                continue
            candidates.append({'source': source, 'source_record': index, 'source_label': raw_label,
                               'label': 'ham' if raw_label == 'ham' else 'spam', 'text': text,
                               'group_id': hashlib.sha256(template.encode()).hexdigest()})
            counts['novel_rows_before_deduplication'] += 1
        stats['filter_counts'] = dict(counts)
        report['sources'][source] = stats
    grouped = defaultdict(list)
    for row in candidates:
        grouped[normalized(row['text'])].append(row)
    staged = []
    conflicts = []
    for key, members in sorted(grouped.items()):
        if len({row['label'] for row in members}) > 1:
            conflicts.append(members)
            continue
        first = members[0]
        staged.append({'id': hashlib.sha256(key.encode()).hexdigest(),
                       'text': first['text'], 'label': first['label'], 'group_id': first['group_id'],
                       'provenance': [{k: r[k] for k in ('source', 'source_record', 'source_label')}
                                      for r in members]})
    report['staging'] = {'unique_messages': len(staged),
                         'class_counts': dict(Counter(r['label'] for r in staged)),
                         'duplicate_rows_collapsed': sum(len(v) - 1 for v in grouped.values()
                                                         if len({r['label'] for r in v}) == 1),
                         'conflicting_text_groups_excluded': len(conflicts),
                         'cross_source_duplicate_groups': sum(len({r['source'] for r in v}) > 1 for v in grouped.values()),
                         'template_groups': len({r['group_id'] for r in staged})}
    probes = {'hacked': r'\bhacked\b', 'blackmail_or_extortion': r'\b(?:blackmail\w*|extort\w*)\b',
              'bitcoin': r'\bbitcoin\b', 'pay': r'\bpay\b'}
    report['keyword_coverage_not_verified_scam_categories'] = {
        name: dict(Counter(r['label'] for r in staged if re.search(pattern, r['text'], re.I)))
        for name, pattern in probes.items()}
    assert all(normalized(r['text']) not in original_keys and template_key(r['text']) not in original_templates
               and template_key(r['text']) not in diagnostic_templates for r in staged)
    assert len({r['id'] for r in staged}) == len(staged)
    out = ROOT / 'data/staging'
    out.mkdir(exist_ok=True)
    (out / 'external-candidates.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in staged))
    (out / 'external-label-conflicts.json').write_text(json.dumps(conflicts, indent=2, ensure_ascii=False) + '\n')
    (ROOT / 'reports/external-data-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
