"""Generate development-only reference cases; never reads the final test set."""
import json
import argparse
from pathlib import Path
import joblib

ROOT = Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser()
parser.add_argument('output')
parser.add_argument('--model-dir', type=Path, default=ROOT / 'models')
parser.add_argument('--external', action='store_true')
args = parser.parse_args()
texts = [json.loads(line)['text'] for line in
         (ROOT / 'data/splits/validation.jsonl').read_text().splitlines()]
texts += ['', '   ', '!!!', 'FREE free Free 123', 'https://example.com/a?b=42',
          'zzzzunseenwordxyz', 'Résumé İSTANBUL 中文', 'Hello\nworld\tHELLO']
texts += ['Pay <DATE_TIME> at <URL> [REDACTED]', 'Pay 123 at https://example.com/42 now!',
          'mail name@example.com; visit portal.lto.gov.ph today', 'hi 😃 friend',
          'éexample.com résumé@test.com 你好example.com', 'a a a a a',
          '[https://example.com](https://example.com) <url> <email>']
if args.external:
    texts += [json.loads(line)['text'] for line in (ROOT / 'data/revision-v3/validation.jsonl').read_text().splitlines()]
diagnostics = ROOT / 'data/diagnostics/user-examples.json'
if diagnostics.exists():
    texts += [r['text'] for r in json.loads(diagnostics.read_text())]
cases = [{'text': text, 'expected': {}} for text in texts]
for family in ('naive_bayes', 'logistic_regression'):
    model_path = args.model_dir / f'{family}.joblib'
    if not model_path.exists():
        model_path = ROOT / 'models' / f'{family}.joblib'
    pipeline = joblib.load(model_path)
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
out = Path(args.output)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(cases, ensure_ascii=False) + '\n')
print(f'Wrote {len(cases)} validation and edge cases to {out}')
