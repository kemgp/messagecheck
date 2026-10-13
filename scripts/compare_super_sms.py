"""Development-only attribution and regression comparison; no fitting or test reads."""
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np

from text_v3 import normalize_v3

ROOT = Path(__file__).resolve().parents[1]


def explain(pipe, text):
    v, clf = pipe['tfidf'], pipe['classifier']
    x = v.transform([text]).getrow(0)
    names = v.get_feature_names_out()
    if hasattr(clf, 'coef_'):
        weights = clf.coef_[0]
        bias = float(clf.intercept_[0])
        actual = float(clf.decision_function(x)[0])
    else:
        weights = clf.feature_log_prob_[1] - clf.feature_log_prob_[0]
        bias = float(clf.class_log_prior_[1] - clf.class_log_prior_[0])
        lp = clf.predict_log_proba(x)[0]
        actual = float(lp[1] - lp[0])
    terms = [{'term': str(names[i]), 'tfidf': float(value), 'weight': float(weights[i]),
              'contribution': float(value * weights[i])} for i, value in zip(x.indices, x.data)]
    total = bias + sum(t['contribution'] for t in terms)
    assert np.isclose(total, actual, atol=1e-10)
    return {'prediction': str(pipe.predict([text])[0]), 'score': actual, 'bias': bias,
            'known_features': len(terms),
            'spam_evidence': sum(t['contribution'] for t in terms if t['contribution'] > 0),
            'ham_evidence': sum(t['contribution'] for t in terms if t['contribution'] < 0),
            'top_spam': sorted((t for t in terms if t['contribution'] > 0), key=lambda t: -t['contribution'])[:10],
            'top_ham': sorted((t for t in terms if t['contribution'] < 0), key=lambda t: t['contribution'])[:10]}


def main():
    val = [json.loads(line) for line in (ROOT / 'data/splits/validation.jsonl').read_text().splitlines()]
    diags = json.loads((ROOT / 'data/diagnostics/user-examples.json').read_text())
    report = {'method': 'Signed TF-IDF times class-log-weight difference (NB) or coefficient (LR), plus prior/intercept. Positive scores predict spam. Scores are not calibrated or comparable across model families.',
              'limitations': 'Observational comparison changes training data, normalization, vocabulary, IDF, features and weighting together. Attribution is arithmetic, not causal identification. Normalizing input to the frozen served model is a sensitivity check, not a fitted ablation.',
              'model_sha256': {}, 'families': {}}
    for family in ('naive_bayes', 'logistic_regression'):
        paths = {name: ROOT / f'models/{prefix}{family}.joblib' for name, prefix in [('served', ''), ('candidate', 'super-sms-v1/')]}
        models = {name: joblib.load(path) for name, path in paths.items()}
        report['model_sha256'].update({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths.values()})
        diagnostic_comparison = []
        for row in diags:
            diagnostic_comparison.append({'id': row['id'], 'expected': row['expected_label'],
                **{name: explain(pipe, row['text']) for name, pipe in models.items()},
                'served_on_v3_normalized_input': explain(models['served'], normalize_v3(row['text']))})
        preds = {name: pipe.predict([r['text'] for r in val]) for name, pipe in models.items()}
        regressions, improvements = [], []
        for i, row in enumerate(val):
            before, after = preds['served'][i], preds['candidate'][i]
            if before == after:
                continue
            entry = {'id': row['id'], 'expected': row['label'],
                     **{name: explain(pipe, row['text']) for name, pipe in models.items()},
                     'served_on_v3_normalized_input': explain(models['served'], normalize_v3(row['text']))}
            (regressions if before == row['label'] else improvements).append(entry)
        report['families'][family] = {'diagnostics': diagnostic_comparison, 'regressions': regressions, 'improvements': improvements}
        print(family, 'regressions', len(regressions), 'improvements', len(improvements))
        for d in diagnostic_comparison:
            if d['id'] == 'user-license-reminder':
                for name in ('served', 'candidate', 'served_on_v3_normalized_input'):
                    e = d[name]
                    print(name, 'score', e['score'], 'bias', e['bias'], 'spam', [(x['term'], round(x['contribution'], 3)) for x in e['top_spam']], 'ham', [(x['term'], round(x['contribution'], 3)) for x in e['top_ham']])
        for row in regressions:
            print('REGRESSION', row['id'][:12], row['expected'], 'scores', round(row['served']['score'],3), round(row['candidate']['score'],3), 'normalized-served',round(row['served_on_v3_normalized_input']['score'],3), 'candidate ham', [(t['term'],round(t['contribution'],3)) for t in row['candidate']['top_ham'][:5]])
    (ROOT / 'reports/super-sms-comparison.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
