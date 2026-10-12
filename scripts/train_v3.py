"""Bounded external-data experiment. Never reads either final-test partition."""
import hashlib
import argparse
import json
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from prepare_v3 import read_jsonl
from text_v3 import normalize_v3
from train_models import metrics

ROOT = Path(__file__).resolve().parents[1]


def export(pipe, family, path):
    v, clf = pipe['tfidf'], pipe['classifier']
    data = {'format_version': 2, 'family': family, 'classes': clf.classes_.tolist(),
            'vectorizer': {'preprocessing': 'ascii-artifact-removal-v3', 'analyzer': v.analyzer,
                           'ngram_range': list(v.ngram_range), 'sublinear_tf': v.sublinear_tf,
                           'vocabulary': {k: int(i) for k, i in v.vocabulary_.items()},
                           'idf': v.idf_.tolist(), 'norm': 'l2'},
            'prediction_policy': 'Positive score predicts spam; ties ham; no probability calibration.'}
    if family == 'naive_bayes':
        data.update(feature_log_prob=clf.feature_log_prob_.tolist(), class_log_prior=clf.class_log_prior_.tolist())
    else:
        data.update(coefficients=clf.coef_[0].tolist(), intercept=float(clf.intercept_[0]))
    path.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--budget', type=float, default=0.75)
    parser.add_argument('--run-name', default='v3')
    args = parser.parse_args()
    assert args.budget in (0.75, 0.25, 0.1)
    assert args.run_name in ('v3', 'v3-weight025', 'v3-weight010')
    out = ROOT / 'models' / args.run_name
    out.mkdir(exist_ok=True)
    legacy = read_jsonl(ROOT / 'data/splits/train.jsonl')
    external = read_jsonl(ROOT / 'data/revision-v3/train.jsonl')
    train = legacy + external
    validation = {'legacy': read_jsonl(ROOT / 'data/splits/validation.jsonl'),
                  'external': read_jsonl(ROOT / 'data/revision-v3/validation.jsonl')}
    diagnostics = json.loads((ROOT / 'data/diagnostics/user-examples.json').read_text())
    x, y = [r['text'] for r in train], [r['label'] for r in train]
    # Limit each external spam template to total mass 1 before source-budget normalization.
    gc = Counter(r['group_id'] for r in external if r['label'] == 'spam')
    weights = np.ones(len(train))
    for i, r in enumerate(external, len(legacy)):
        if r['label'] == 'spam':
            weights[i] = 1 / gc[r['group_id']]
    spam_indices = [i for i in range(len(legacy), len(train)) if y[i] == 'spam']
    budget = args.budget * y.count('ham')
    weights[spam_indices] *= budget / weights[spam_indices].sum()
    config = {'representations': ['word-unigram', 'word-bigram', 'character-3-5'],
              'naive_bayes_alpha': [0.1, 0.5], 'logistic_C': [3.0, 10.0],
              'external_spam_weight_budget': budget, 'threshold': 0,
              'selection': 'Per family, highest mean of legacy and external spam F1 among candidates passing all adoption gates; then legacy precision, then earlier order.',
              'gates': 'Legacy false positives <= 3, legacy false negatives <= served baseline; external ham false-positive rate <= 5%; external spam F1 improves >= 0.05 over baseline. Diagnostics reported, not a ranking metric.',
              'test_policy': 'Neither test partition is loaded or evaluated.'}
    # Record protocol before fitting/evaluating any candidates.
    (ROOT / 'reports' / f'{args.run_name}-experiment-protocol.json').write_text(json.dumps(config, indent=2) + '\n')

    def evaluate(pipe):
        return {name: metrics([r['label'] for r in rows], pipe.predict([r['text'] for r in rows])) for name, rows in validation.items()}

    baseline = {family: evaluate(joblib.load(ROOT / 'models' / f'{family}.joblib'))
                for family in ('naive_bayes', 'logistic_regression')}
    entries, fitted = [], {}
    for representation, analyzer, grams in [('word-unigram', 'word', (1, 1)), ('word-bigram', 'word', (1, 2)), ('character-3-5', 'char', (3, 5))]:
        for family, values in [('naive_bayes', [0.1, 0.5]), ('logistic_regression', [3.0, 10.0])]:
            for value in values:
                clf = MultinomialNB(alpha=value) if family == 'naive_bayes' else LogisticRegression(C=value, solver='liblinear', max_iter=2000, random_state=42)
                vectorizer = TfidfVectorizer(preprocessor=normalize_v3, lowercase=False, analyzer=analyzer,
                                            token_pattern=r'[a-z]+' if analyzer == 'word' else None, ngram_range=grams, min_df=2,
                                            max_features=30000, sublinear_tf=True)
                pipe = Pipeline([('tfidf', vectorizer), ('classifier', clf)])
                pipe.fit(x, y, classifier__sample_weight=weights)
                if family == 'logistic_regression':
                    assert int(clf.n_iter_.max()) < 2000
                scores = evaluate(pipe)
                old = baseline[family]
                lm, em = scores['legacy']['confusion_matrix'], scores['external']['confusion_matrix']
                gates = {'legacy_false_alarms': lm[0][1] <= 3,
                         'legacy_misses': lm[1][0] <= old['legacy']['confusion_matrix'][1][0],
                         'external_false_alarms': em[0][1] / max(sum(em[0]), 1) <= .05,
                         'external_improvement': scores['external']['spam_f1'] >= old['external']['spam_f1'] + .05}
                entry = {'order': len(entries), 'family': family, 'representation': representation,
                         'parameters': {'alpha' if family == 'naive_bayes' else 'C': value},
                         'validation': scores, 'gates': gates, 'eligible': all(gates.values()),
                         'diagnostics': [{'id': r['id'], 'expected': r['expected_label'], 'predicted': str(p)}
                                         for r, p in zip(diagnostics, pipe.predict([r['text'] for r in diagnostics]))]}
                entries.append(entry)
                fitted[entry['order']] = pipe
                print(json.dumps(entry), flush=True)
    selected = {}
    for family in baseline:
        eligible = [e for e in entries if e['family'] == family and e['eligible']]
        if eligible:
            best = max(eligible, key=lambda e: (np.mean([m['spam_f1'] for m in e['validation'].values()]), e['validation']['legacy']['spam_precision'], -e['order']))
            selected[family] = best
            pipe = fitted[best['order']]
            joblib.dump(pipe, out / f'{family}.joblib')
            export(pipe, family, out / f'{family}.json')
    report = {'protocol': config, 'baseline': baseline, 'candidates': entries, 'selected': selected,
              'counts': {'train': dict(Counter(y)), **{k: dict(Counter(r['label'] for r in v)) for k, v in validation.items()}},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'status': 'Candidates only, not deployed. Both final-test sets remain unevaluated.'}
    (ROOT / 'reports' / f'{args.run_name}-experiment.json').write_text(json.dumps(report, indent=2) + '\n')
    print('SELECTED', {f: e['order'] for f, e in selected.items()}, flush=True)


if __name__ == '__main__':
    main()
