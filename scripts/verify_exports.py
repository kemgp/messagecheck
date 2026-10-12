"""Check exported model arithmetic against sklearn on validation and edge cases."""
import json
import re
from collections import Counter
from pathlib import Path

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    texts = [json.loads(line)['text'] for line in
             (ROOT / 'data/splits/validation.jsonl').read_text().splitlines()]
    texts += ['', '   ', '!!!', 'FREE free Free 123', 'https://example.com/a?b=42',
              'zzzzunseenwordxyz', 'Résumé İSTANBUL 中文', 'Hello\nworld\tHELLO']
    report = {'stage': 'Python arithmetic verification; browser parity still pending', 'messages_checked_per_model': len(texts), 'models': {}}
    for family in ('naive_bayes', 'logistic_regression'):
        pipe = joblib.load(ROOT / 'models' / f'{family}.joblib')
        payload = json.loads((ROOT / 'models' / f'{family}.json').read_text())
        v = payload['vectorizer']
        terms = v['vocabulary']
        features = np.zeros((len(texts), len(terms)))
        for i, message in enumerate(texts):
            counts = Counter(re.findall(v['token_pattern'], message.lower()))
            for term, count in counts.items():
                if term in terms:
                    index = terms[term]
                    features[i, index] = count * v['idf'][index]
            length = np.linalg.norm(features[i])
            if length:
                features[i] /= length
        reference = pipe['tfidf'].transform(texts)
        feature_error = float(np.max(np.abs(features - reference.toarray())))
        assert feature_error < 1e-10
        if family == 'logistic_regression':
            scores = features @ np.array(payload['coefficients']) + payload['intercept']
            reference_scores = pipe['classifier'].decision_function(reference)
        else:
            weights = np.array(payload['feature_log_prob'])
            priors = np.array(payload['class_log_prior'])
            scores = features @ (weights[1] - weights[0]) + priors[1] - priors[0]
            logs = pipe.predict_log_proba(texts)
            reference_scores = logs[:, 1] - logs[:, 0]
        score_error = float(np.max(np.abs(scores - reference_scores)))
        assert score_error < 1e-10
        labels = np.where(scores > 0, 'spam', 'ham')
        assert np.array_equal(labels, pipe.predict(texts))
        report['models'][family] = {'maximum_feature_error': feature_error,
                                    'maximum_score_error': score_error,
                                    'label_mismatches': 0}
    (ROOT / 'reports/export-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
