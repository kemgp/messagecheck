"""Reproduce the moderate class-weight revision and explicitly record selection history."""
import hashlib
import json
import shutil
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from train_models import metrics, export_model

ROOT = Path(__file__).resolve().parents[1]


def main():
    archive = ROOT/'models/baseline-v1'
    archive.mkdir(exist_ok=True)
    for family in ('naive_bayes', 'logistic_regression'):
        for extension in ('json', 'joblib'):
            destination = archive/f'{family}.{extension}'
            if not destination.exists():
                shutil.copy2(ROOT/'models'/destination.name, destination)
    original_report = archive/'validation-report.json'
    if not original_report.exists():
        shutil.copy2(ROOT/'reports/validation-report.json', original_report)
    report = json.loads(original_report.read_text())
    train = [json.loads(line) for line in (ROOT/'data/splits/train.jsonl').read_text().splitlines()]
    validation = [json.loads(line) for line in (ROOT/'data/splits/validation.jsonl').read_text().splitlines()]
    x=[r['text'] for r in train]; y=[r['label'] for r in train]
    groups=[r['group_id'] for r in train]
    vx=[r['text'] for r in validation]; vy=[r['label'] for r in validation]
    pipeline=Pipeline([
        ('tfidf', TfidfVectorizer(token_pattern=r'[a-z0-9]+', lowercase=True, norm='l2')),
        ('classifier', LogisticRegression(C=10.0, class_weight={'ham':1,'spam':2}, solver='liblinear', random_state=42, max_iter=2000)),
    ])
    folds=list(StratifiedGroupKFold(n_splits=3,shuffle=True,random_state=42).split(x,y,groups))
    for tr,va in folds:
        assert not {groups[i] for i in tr} & {groups[i] for i in va}
    cv_metrics=metrics(y,cross_val_predict(pipeline,x,y,cv=folds,n_jobs=1))
    pipeline.fit(x,y)
    predictions=pipeline.predict(vx)
    new_metrics=metrics(vy,predictions)
    before=report['selected']['logistic_regression']['metrics']
    diagnostics=json.loads((ROOT/'data/diagnostics/user-examples.json').read_text())
    base=joblib.load(archive/'logistic_regression.joblib')
    diagnostic_results=[]
    for example in diagnostics:
        text=example['text']
        diagnostic_results.append({'id':example['id'],'user_expected_label':example['expected_label'],
            'before':str(base.predict([text])[0]),'after':str(pipeline.predict([text])[0]),
            'revised_score':float(pipeline.decision_function([text])[0]),
            'is_independent_test':False})
    # Adoption gates are development checks, not claims of independent testing.
    assert new_metrics['confusion_matrix'][0][1] <= before['confusion_matrix'][0][1]
    assert new_metrics['confusion_matrix'][1][0] < before['confusion_matrix'][1][0]
    assert all(e['after']==e['user_expected_label'] for e in diagnostic_results)
    joblib.dump(pipeline,ROOT/'models/logistic_regression.joblib')
    export_model(pipeline,'logistic_regression',ROOT/'models/logistic_regression.json')
    entry={'family':'logistic_regression','parameters':{'C':10.0,'class_weight':{'ham':1,'spam':2}},'order':6,'metrics':new_metrics}
    report['candidates'].append(entry)
    report['selected']['logistic_regression']=entry
    report['selection_rule']='Revision 2: Naive Bayes unchanged. Moderate logistic class weighting chosen after user diagnostics; improves training-group CV and validation misses without increasing validation false alarms, while matching both user-supplied labels. Not the highest-F1 candidate in the separate broad experiment. No final-test evaluation.'
    report['revision']='moderate-spam-weight-v2'
    report['revision_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report['model_json_sha256']['logistic_regression']=hashlib.sha256((ROOT/'models/logistic_regression.json').read_bytes()).hexdigest()
    report['limitations']+=' Model revision uses development diagnostics and reused validation data; user examples are not independent performance evidence.'
    (ROOT/'reports/validation-report.json').write_text(json.dumps(report,indent=2)+'\n')
    logs=pipeline.predict_log_proba(vx)
    (ROOT/'reports/logistic_regression-validation-predictions.jsonl').write_text(''.join(json.dumps({
        'id':row['id'],'true_label':row['label'],'predicted_label':str(predictions[i]),'log_class_scores':logs[i].tolist()})+'\n' for i,row in enumerate(validation)))
    revision={'before_validation':before,'after_validation':new_metrics,'training_group_cv':cv_metrics,
              'diagnostics':diagnostic_results,'selection':report['selection_rule'],
              'review_notice_policy':'Display a review notice for model disagreement or absolute log-score margin below 0.5. This heuristic is not calibrated and does not change or remove raw classifier predictions from metrics.'}
    (ROOT/'reports/model-revision.json').write_text(json.dumps(revision,indent=2)+'\n')
    lines=['# Validation results','','Revision 2. These are reused development/validation results, not final-test estimates.','',
           '| Model | Spam precision | Spam recall | Spam F1 | False positives | False negatives |',
           '| --- | ---: | ---: | ---: | ---: | ---: |']
    for family,selected in report['selected'].items():
        m=selected['metrics'];cm=m['confusion_matrix']
        lines.append(f"| {family} | {m['spam_precision']:.2%} | {m['spam_recall']:.2%} | {m['spam_f1']:.2%} | {cm[0][1]} | {cm[1][0]} |")
    lines+=['',report['selection_rule'],'','All binary outputs remain counted, including borderline cases. Review notices are a separate interface feature.']
    (ROOT/'reports/validation-summary.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(revision,indent=2))


if __name__=='__main__':main()
