"""Bounded v2 experiment; chooses candidates using grouped training-only CV."""
import json
from pathlib import Path
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from train_models import metrics

ROOT = Path(__file__).resolve().parents[1]


def main():
    train = [json.loads(line) for line in (ROOT/'data/splits/train.jsonl').read_text().splitlines()]
    x = np.array([r['text'] for r in train])
    y = np.array([r['label'] for r in train])
    groups = np.array([r['group_id'] for r in train])
    folds = list(StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=42).split(x, y, groups))
    for tr, va in folds:
        assert not set(groups[tr]) & set(groups[va])
    configs = [
        ('naive_bayes', (1,1), False, {'alpha':0.1}),
        ('naive_bayes', (1,2), True, {'alpha':0.1}),
        ('naive_bayes', (1,2), True, {'alpha':0.05}),
        ('logistic_regression', (1,1), False, {'C':10.0}),
        ('logistic_regression', (1,1), False, {'C':10.0, 'class_weight':'balanced'}),
        ('logistic_regression', (1,2), True, {'C':10.0, 'class_weight':'balanced'}),
        ('logistic_regression', (1,2), True, {'C':10.0}),
    ]
    entries, pipes = [], []
    for order, (family, ngrams, sublinear, params) in enumerate(configs):
        classifier = MultinomialNB(**params) if family=='naive_bayes' else LogisticRegression(**params, solver='liblinear', random_state=42, max_iter=2000)
        pipe = Pipeline([('tfidf', TfidfVectorizer(token_pattern=r'[a-z0-9]+', ngram_range=ngrams, sublinear_tf=sublinear)), ('classifier', classifier)])
        predictions = cross_val_predict(pipe, x, y, cv=folds, n_jobs=1)
        entry = {'order':order,'family':family,'ngram_range':list(ngrams),'sublinear_tf':sublinear,'parameters':params,'training_cv_metrics':metrics(y,predictions)}
        entries.append(entry); pipes.append(pipe)
        print(f"{order}: {family}, {ngrams}, {params}, training CV F1 {entry['training_cv_metrics']['spam_f1']:.4f}", flush=True)
    validation = [json.loads(line) for line in (ROOT/'data/splits/validation.jsonl').read_text().splitlines()]
    vx=[r['text'] for r in validation]; vy=[r['label'] for r in validation]
    previous=json.loads((ROOT/'reports/validation-report.json').read_text())
    winners={}
    for family in ('naive_bayes','logistic_regression'):
        best=max((e for e in entries if e['family']==family),key=lambda e:(e['training_cv_metrics']['spam_f1'], e['training_cv_metrics']['spam_precision'], -e['order']))
        pipe=pipes[best['order']].fit(x,y)
        best={**best,'validation_metrics':metrics(vy,pipe.predict(vx))}
        old=previous['selected'][family]['metrics']['confusion_matrix']
        new=best['validation_metrics']['confusion_matrix']
        best['reduces_errors_without_worsening_either_type']=(new[0][1]<=old[0][1] and new[1][0]<=old[1][0] and new[0][1]+new[1][0]<old[0][1]+old[1][0])
        winners[family]=best
        joblib.dump(pipe, ROOT/'models'/f'{family}-candidate.joblib')
        print(f'{family} winner validation: {json.dumps(best)}',flush=True)
    report={'selection':'3-fold stratified grouped CV on training only; highest spam F1, then precision, then earlier candidate. Validation used as a non-regression check. No final test reads.',
            'reason':'User reported false positives/negatives; bounded phrase-feature and class-balancing experiment.',
            'candidates':entries,'winners':winners,
            'limitations':'Development/validation data have now been reused; these are exploratory improvements, not final generalization estimates. More false positives may accompany fewer misses.'}
    (ROOT/'reports/improvement-experiment.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
