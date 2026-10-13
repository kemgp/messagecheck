"""Freeze served revision 2 before loading held-out rows; evaluate without fitting."""
import hashlib
import json
import platform
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import sklearn

from train_models import metrics

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ('naive_bayes', 'logistic_regression')
DATASETS = {'uci': 'data/splits', 'external': 'data/revision-v3', 'super_sms': 'data/super-sms-v1'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def main():
    freeze_path = ROOT / 'reports/final-model-freeze.json'
    assert not freeze_path.exists(), 'Freeze already exists; do not overwrite final evaluation history'
    protected = [ROOT / f'models/{f}.{ext}' for f in FAMILIES for ext in ('json', 'joblib')]
    protected += [ROOT / 'src/inference.js']
    frozen = {str(p.relative_to(ROOT)): sha(p) for p in protected}
    test_hashes = {name: sha(ROOT / directory / 'test.jsonl') for name, directory in DATASETS.items()}
    freeze = {'revision': 2, 'date': '2026-10-14', 'timezone': 'Asia/Manila',
        'model_and_inference_sha256': frozen, 'test_sha256': test_hashes,
        'primary_dataset': 'uci', 'supplemental_datasets': ['external', 'super_sms'],
        'selection': 'Retain served revision 2 after rejection of all external-data candidates. No further model or threshold tuning against final results.',
        'decision_rule': 'Positive spam-minus-ham score predicts spam; ties ham. No calibration or threshold search.',
        'ui_policy': 'Zero known terms shows insufficient evidence; abs(score)<0.5 with known terms shows borderline notice. All underlying binary outputs still count in metrics.',
        'metrics': ['accuracy', 'spam_precision', 'spam_recall', 'spam_f1', 'macro_f1', 'class_support', 'confusion_matrix'],
        'baseline': 'Always ham, majority class determined from original training data',
        'parity': 'Python/JavaScript labels, sparse TF-IDF, scores and explanation sums; tolerance 1e-10. No performance-driven fixes.',
        'limitations': ['Known hacking/payment false negative remains.', 'Older English-focused training corpus; no authenticity or modern-scam reliability claim.', 'Source labels and heuristic grouping have limitations.', 'Supplemental sets have different class balances and are not pooled with primary results.', 'Source texts were processed in earlier automated overlap audits, not scored for model selection.']}
    # Persist decision/protocol before parsing held-out content or scoring any test row.
    freeze_path.write_text(json.dumps(freeze, indent=2) + '\n')
    pipes = {f: joblib.load(ROOT / f'models/{f}.joblib') for f in FAMILIES}
    training = rows(ROOT / 'data/splits/train.jsonl')
    assert Counter(r['label'] for r in training).most_common(1)[0][0] == 'ham'
    result = {'revision': 2, 'evaluation_date': freeze['date'], 'freeze_sha256': sha(freeze_path),
              'model_sha256': frozen, 'primary_dataset': 'uci', 'datasets': {},
              'environment': {'python': platform.python_version(), 'sklearn': sklearn.__version__},
              'status': 'Python evaluation complete; browser parity pending'}
    cases = []
    for name, directory in DATASETS.items():
        path = ROOT / directory / 'test.jsonl'
        assert sha(path) == test_hashes[name]
        test = rows(path)
        manifest = rows(ROOT / directory / 'manifest.jsonl')
        expected = {r['id']: r['group_id'] for r in manifest if r['split'] == 'test'}
        assert {r['id']: r['group_id'] for r in test} == expected
        assert len(test) == len(expected)
        test_groups = {r['group_id'] for r in test}
        assert not test_groups & {r['group_id'] for r in manifest if r['split'] != 'test'}
        x, y = [r['text'] for r in test], [r['label'] for r in test]
        block = {'rows': len(test), 'class_support': dict(Counter(y)), 'test_sha256': test_hashes[name],
                 'majority_baseline': metrics(y, ['ham'] * len(y)), 'models': {}}
        fixtures = [{'text': t, 'expected': {}} for t in x]
        predictions = [{'id': r['id'], 'group_id': r['group_id'], 'expected': r['label'], 'models': {}} for r in test]
        for family, pipe in pipes.items():
            features = pipe['tfidf'].transform(x)
            predicted = pipe.predict(x)
            if family == 'logistic_regression':
                scores = pipe['classifier'].decision_function(features)
            else:
                logs = pipe.predict_log_proba(x)
                scores = logs[:, 1] - logs[:, 0]
            known = np.asarray(features.getnnz(axis=1))
            block['models'][family] = {**metrics(y, predicted),
                'zero_known_terms': int((known == 0).sum()),
                'borderline_notices': int(((known > 0) & (np.abs(scores) < .5)).sum())}
            for i in range(len(test)):
                feature_row = features.getrow(i)
                predictions[i]['models'][family] = {'predicted': str(predicted[i]), 'score': float(scores[i]), 'known_terms': int(known[i])}
                fixtures[i]['expected'][family] = {'label': str(predicted[i]), 'score': float(scores[i]),
                    'features': {str(k): float(v) for k, v in zip(feature_row.indices, feature_row.data)}}
        # No raw messages in repository prediction artifacts.
        (ROOT / f'reports/final-{name}-predictions.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in predictions))
        result['datasets'][name] = block
        cases.extend(fixtures)
        print(name, json.dumps(block), flush=True)
    for path, expected in frozen.items():
        assert sha(ROOT / path) == expected
    for name, directory in DATASETS.items():
        assert sha(ROOT / directory / 'test.jsonl') == test_hashes[name]
    Path('/tmp/messagecheck-final-parity.json').write_text(json.dumps(cases, ensure_ascii=False) + '\n')
    result['parity_cases_per_model'] = len(cases)
    (ROOT / 'reports/final-test-report.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
