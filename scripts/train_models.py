"""Train on train.jsonl and select candidates on validation.jsonl only."""
import hashlib
import json
import platform
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import scipy
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
LABELS = ['ham', 'spam']
# Fixed before observing validation scores. All candidates use default decision thresholds.
CANDIDATES = [('naive_bayes', {'alpha': a}) for a in (0.1, 0.5, 1.0)] + [
    ('logistic_regression', {'C': c}) for c in (1.0, 3.0, 10.0)]


def metrics(y, predicted):
    return {
        'accuracy': accuracy_score(y, predicted),
        'spam_precision': precision_score(y, predicted, pos_label='spam', zero_division=0),
        'spam_recall': recall_score(y, predicted, pos_label='spam', zero_division=0),
        'spam_f1': f1_score(y, predicted, pos_label='spam', zero_division=0),
        'macro_f1': f1_score(y, predicted, average='macro', zero_division=0),
        'confusion_matrix': confusion_matrix(y, predicted, labels=LABELS).tolist(),
    }


def ranking(entry):
    m = entry['metrics']
    return (m['spam_f1'], m['spam_precision'], m['spam_recall'], -entry['order'])


def export_model(pipeline, family, path):
    v, model = pipeline['tfidf'], pipeline['classifier']
    payload = {
        'format_version': 1, 'family': family, 'classes': model.classes_.tolist(),
        'vectorizer': {
            'token_pattern': '[a-z0-9]+', 'lowercase': True, 'ngram_range': [1, 1],
            'vocabulary': {k: int(i) for k, i in v.vocabulary_.items()},
            'idf': v.idf_.tolist(), 'norm': 'l2', 'sublinear_tf': False,
            'smooth_idf': True, 'use_idf': True,
        },
        'prediction_policy': 'Choose highest class score; ties choose first class (ham). Scores are uncalibrated.',
    }
    if family == 'logistic_regression':
        payload.update(coefficients=model.coef_[0].tolist(), intercept=float(model.intercept_[0]))
    else:
        payload.update(feature_log_prob=model.feature_log_prob_.tolist(), class_log_prior=model.class_log_prior_.tolist())
    path.write_text(json.dumps(payload, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


def main():
    data, checksums = {}, {}
    # Deliberately no test-set loader.
    for split in ('train', 'validation'):
        raw = (ROOT / 'data/splits' / f'{split}.jsonl').read_bytes()
        checksums[split] = hashlib.sha256(raw).hexdigest()
        data[split] = [json.loads(line) for line in raw.decode().splitlines()]
    for key in ('id', 'group_id'):
        assert not {r[key] for r in data['train']} & {r[key] for r in data['validation']}
    train_x = [r['text'] for r in data['train']]
    train_y = [r['label'] for r in data['train']]
    val_x = [r['text'] for r in data['validation']]
    val_y = [r['label'] for r in data['validation']]
    models = ROOT / 'models'
    reports = ROOT / 'reports'
    models.mkdir(exist_ok=True)
    reports.mkdir(exist_ok=True)
    baseline = DummyClassifier(strategy='most_frequent').fit(np.zeros((len(train_y), 1)), train_y)
    baseline_metrics = metrics(val_y, baseline.predict(np.zeros((len(val_y), 1))))
    entries, fitted = [], {}
    for order, (family, params) in enumerate(CANDIDATES):
        estimator = MultinomialNB(**params) if family == 'naive_bayes' else LogisticRegression(
            **params, solver='liblinear', max_iter=2000, random_state=42)
        pipe = Pipeline([
            ('tfidf', TfidfVectorizer(token_pattern=r'[a-z0-9]+', lowercase=True, norm='l2')),
            ('classifier', estimator),
        ])
        pipe.fit(train_x, train_y)
        if family == 'logistic_regression':
            assert int(pipe['classifier'].n_iter_.max()) < 2000, 'Model did not converge'
        entry = {'family': family, 'parameters': params, 'order': order, 'metrics': metrics(val_y, pipe.predict(val_x))}
        entries.append(entry)
        fitted[order] = pipe
    selected = {}
    artifacts = {}
    for family in ('naive_bayes', 'logistic_regression'):
        best = max((e for e in entries if e['family'] == family), key=ranking)
        selected[family] = best
        pipe = fitted[best['order']]
        joblib.dump(pipe, models / f'{family}.joblib')
        export_model(pipe, family, models / f'{family}.json')
        artifacts[family] = hashlib.sha256((models / f'{family}.json').read_bytes()).hexdigest()
        predicted = pipe.predict(val_x)
        logprobs = pipe.predict_log_proba(val_x)
        rows = [{'id': row['id'], 'true_label': row['label'], 'predicted_label': str(predicted[i]),
                 'log_class_scores': logprobs[i].tolist()} for i, row in enumerate(data['validation'])]
        (reports / f'{family}-validation-predictions.jsonl').write_text(
            ''.join(json.dumps(row) + '\n' for row in rows))
    report = {
        'stage': 'validation only; final test not evaluated',
        'selection_rule': 'Highest validation spam F1 per model family; ties by precision, recall, then earlier predefined candidate. No validation refit.',
        'input_sha256': checksums,
        'training_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'versions': {'python': platform.python_version(), 'scikit-learn': sklearn.__version__,
                     'numpy': np.__version__, 'scipy': scipy.__version__, 'joblib': joblib.__version__},
        'counts': {k: dict(Counter(r['label'] for r in rows)) for k, rows in data.items()},
        'confusion_matrix_order': 'Rows=true, columns=predicted; ham then spam',
        'majority_baseline': baseline_metrics, 'candidates': entries, 'selected': selected,
        'provisional_preferred_model': max(selected.values(), key=ranking)['family'],
        'model_json_sha256': artifacts,
        'vocabulary_size': len(fitted[0]['tfidf'].vocabulary_),
        'limitations': 'Validation scores informed model selection and are not final generalization estimates. The tokenizer is ASCII word/number based; the older English corpus does not establish multilingual or modern scam detection.',
    }
    (reports / 'validation-report.json').write_text(json.dumps(report, indent=2) + '\n')
    lines = ['# Validation results', '', 'Preliminary model-selection results. Final test set has not been evaluated.', '',
             '| Model | Spam precision | Spam recall | Spam F1 | Accuracy |', '| --- | ---: | ---: | ---: | ---: |']
    for name, m in [('Majority baseline', baseline_metrics)] + [(f, e['metrics']) for f, e in selected.items()]:
        lines.append(f"| {name} | {m['spam_precision']:.2%} | {m['spam_recall']:.2%} | {m['spam_f1']:.2%} | {m['accuracy']:.2%} |")
    lines += ['', 'Selection: validation spam F1, then precision, recall, and predefined candidate order.',
              'Training: 3,612 messages. Validation: 774 messages (678 ham, 96 spam).',
              'Vocabulary and IDF were fitted only on training messages. Models were not refitted on validation data.',
              'Detailed settings, versions, confusion matrices, and checksums are in validation-report.json.',
              'Browser parity has not yet been verified. These metrics must not be presented as final test results.']
    (reports / 'validation-summary.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    print('Selected parameters:', {k: v['parameters'] for k, v in selected.items()})


if __name__ == '__main__':
    main()
