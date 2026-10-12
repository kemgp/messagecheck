"""Generate development-only reference cases; never reads the final test set."""
import json
import sys
from pathlib import Path
import joblib

ROOT = Path(__file__).resolve().parents[1]

if len(sys.argv) != 2:
    raise SystemExit('Usage: python scripts/make_parity_fixtures.py OUTPUT.json')
texts = [json.loads(line)['text'] for line in
         (ROOT / 'data/splits/validation.jsonl').read_text().splitlines()]
texts += ['', '   ', '!!!', 'FREE free Free 123', 'https://example.com/a?b=42',
          'zzzzunseenwordxyz', 'Résumé İSTANBUL 中文', 'Hello\nworld\tHELLO']
diagnostics = ROOT / 'data/diagnostics/user-examples.json'
if diagnostics.exists():
    texts += [r['text'] for r in json.loads(diagnostics.read_text())]
cases = [{'text': text, 'expected': {}} for text in texts]
for family in ('naive_bayes', 'logistic_regression'):
    pipeline = joblib.load(ROOT / 'models' / f'{family}.joblib')
    features = pipeline['tfidf'].transform(texts)
    labels = pipeline.predict(texts)
    if family == 'logistic_regression':
        scores = pipeline['classifier'].decision_function(features)
    else:
        logs = pipeline.predict_log_proba(texts)
        scores = logs[:, 1] - logs[:, 0]
    for i, case in enumerate(cases):
        row = features.getrow(i)
        case['expected'][family] = {
            'label': str(labels[i]), 'score': float(scores[i]),
            'features': {str(index): float(value) for index, value in zip(row.indices, row.data)},
        }
out = Path(sys.argv[1])
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(cases, ensure_ascii=False) + '\n')
print(f'Wrote {len(cases)} validation and edge cases to {out}')
