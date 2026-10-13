"""Predeclared bounded experiment; final-test rows are never scored or fitted."""
import json
import hashlib
import platform
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from text_v3 import normalize_v3
from train_models import metrics
from train_v3 import export

ROOT = Path(__file__).resolve().parents[1]
RUN = 'super-sms-v1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def main():
    report_path = ROOT / f'reports/{RUN}-experiment.json'
    protocol_path = ROOT / f'reports/{RUN}-protocol.json'
    assert not protocol_path.exists(), 'Use a new explicit protocol/run name; do not overwrite results'
    prepared = ROOT / 'data/super-sms-prepared'
    prep = json.loads((ROOT / 'reports/super-sms-preparation.json').read_text())
    assert digest(prepared / 'candidates.jsonl') == prep['output_sha256']['candidates.jsonl']
    for path, expected in prep['input_sha256'].items():
        assert digest(ROOT / path) == expected, f'Changed preparation input: {path}'
    served = {str(p.relative_to(ROOT)): digest(p) for p in (ROOT / 'models').glob('*') if p.suffix in ('.json', '.joblib')}
    protocol = {
        'run': RUN, 'split': 'sha256(super-sms-v1: + group_id) first 8 hex digits modulo 100: <60 train, <80 validation, else reserved test',
        'representations': ['word-unigram', 'word-bigram'],
        'families': {'naive_bayes': {'alpha': .1}, 'logistic_regression': {'C': 10, 'solver': 'liblinear', 'max_iter': 2000, 'random_state': 42}},
        'new_data_class_budgets': [.25, 1.0],
        'weighting': 'Original rows weight 1. Each new template group has equal mass within its class; each new class total is budget times original training count for that class. No old external training rows included.',
        'vectorizer': 'normalize_v3, word ngrams, min_df=2, max_features=30000, sublinear_tf=True, L2 TF-IDF. Fit on combined training rows only. Classifier weights do not weight vocabulary or IDF.',
        'candidate_count': 8, 'threshold': 'Default classifier threshold; no threshold tuning',
        'gates': {'legacy_fp': '<=3', 'legacy_fn': '<= served family baseline',
                  'super_sms_f1': '>= served family baseline + 0.02',
                  'super_sms_ham_fpr': '<=0.05 and <= served family baseline + 0.01',
                  'prior_external_f1': '>= served family baseline',
                  'diagnostics': 'All three expected labels correct, including extortion and legitimate license'},
        'ranking': 'Eligible first, then mean spam F1 across three validation domains, then legacy precision, then earlier candidate order. Save one candidate per family even if ineligible, clearly marked.',
        'test_policy': 'Allocate Super SMS test rows once; never reopen or score any final-test partition. Existing protected source rows were used only in prior overlap auditing.',
        'adoption': 'Experiment only. Served models unchanged; eligibility does not deploy a model.',
        'prepared_sha256': prep['output_sha256']['candidates.jsonl'],
        'served_sha256': served, 'script_sha256': digest(Path(__file__)),
    }
    protocol_path.write_text(json.dumps(protocol, indent=2) + '\n')
    partitions = {p: [] for p in ('train', 'validation', 'test')}
    for row in read_rows(prepared / 'candidates.jsonl'):
        assert row['split'] == 'unassigned'
        bucket = int(hashlib.sha256(f"{RUN}:{row['group_id']}".encode()).hexdigest()[:8], 16) % 100
        part = 'train' if bucket < 60 else 'validation' if bucket < 80 else 'test'
        partitions[part].append({**row, 'split': part})
    groups = {p: {r['group_id'] for r in rows} for p, rows in partitions.items()}
    assert not (groups['train'] & groups['validation'] or groups['train'] & groups['test'] or groups['validation'] & groups['test'])
    split_dir = ROOT / f'data/{RUN}'
    split_dir.mkdir(exist_ok=True)
    split_report = {}
    manifest = []
    for part, rows in partitions.items():
        path = split_dir / f'{part}.jsonl'
        payload = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
        path.write_text(payload)
        split_report[part] = {'rows': len(rows), 'groups': len(groups[part]), 'labels': dict(Counter(r['label'] for r in rows)), 'sha256': hashlib.sha256(payload.encode()).hexdigest()}
        manifest.extend({'id': r['id'], 'group_id': r['group_id'], 'split': part} for r in rows)
    (split_dir / 'manifest.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in manifest))
    del partitions['test']
    legacy = read_rows(ROOT / 'data/splits/train.jsonl')
    new = partitions['train']
    train = legacy + new
    validation = {'legacy': read_rows(ROOT / 'data/splits/validation.jsonl'),
                  'super_sms': partitions['validation'],
                  'prior_external': read_rows(ROOT / 'data/revision-v3/validation.jsonl')}
    diagnostics = json.loads((ROOT / 'data/diagnostics/user-examples.json').read_text())
    input_paths = ['data/splits/train.jsonl', 'data/splits/validation.jsonl', 'data/revision-v3/validation.jsonl', 'data/diagnostics/user-examples.json']
    checksums = {p: digest(ROOT / p) for p in input_paths}
    x, y = [r['text'] for r in train], [r['label'] for r in train]
    original_counts = Counter(r['label'] for r in legacy)
    group_counts = Counter(r['group_id'] for r in new)
    new_classes = np.array([r['label'] for r in new])

    def evaluate(pipe):
        return {name: metrics([r['label'] for r in rows], pipe.predict([r['text'] for r in rows])) for name, rows in validation.items()}

    def diagnostic_results(pipe):
        return [{'id': r['id'], 'expected': r['expected_label'], 'predicted': str(p)} for r, p in zip(diagnostics, pipe.predict([r['text'] for r in diagnostics]))]

    baseline = {}
    for family in protocol['families']:
        pipe = joblib.load(ROOT / f'models/{family}.joblib')
        baseline[family] = {'validation': evaluate(pipe), 'diagnostics': diagnostic_results(pipe)}
    out = ROOT / f'models/{RUN}'
    out.mkdir(exist_ok=True)
    entries, selected = [], {}
    report = {'protocol': protocol, 'splits': split_report, 'training_counts': dict(Counter(y)),
              'input_sha256': checksums, 'baseline': baseline, 'candidates': entries, 'selected': selected,
              'environment': {'python': platform.python_version(), 'sklearn': sklearn.__version__},
              'status': 'running; served models unchanged; final tests unevaluated'}
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    for name, ngrams in [('word-unigram', (1, 1)), ('word-bigram', (1, 2))]:
        vectorizer = TfidfVectorizer(preprocessor=normalize_v3, lowercase=False, token_pattern=r'[a-z]+', ngram_range=ngrams, min_df=2, max_features=30000, sublinear_tf=True)
        features = vectorizer.fit_transform(x)
        for budget in protocol['new_data_class_budgets']:
            nw = np.array([1 / group_counts[r['group_id']] for r in new])
            for label in ('ham', 'spam'):
                mask = new_classes == label
                nw[mask] *= budget * original_counts[label] / nw[mask].sum()
                assert np.isclose(nw[mask].sum(), budget * original_counts[label])
            weights = np.concatenate([np.ones(len(legacy)), nw])
            for family, params in protocol['families'].items():
                clf = MultinomialNB(**params) if family == 'naive_bayes' else LogisticRegression(**params)
                clf.fit(features, y, sample_weight=weights)
                if family == 'logistic_regression':
                    assert clf.n_iter_.max() < params['max_iter'], 'Convergence failure'
                pipe = Pipeline([('tfidf', vectorizer), ('classifier', clf)])
                scores, diags = evaluate(pipe), diagnostic_results(pipe)
                old = baseline[family]['validation']
                lm, sm = scores['legacy']['confusion_matrix'], scores['super_sms']['confusion_matrix']
                bm = old['super_sms']['confusion_matrix']
                fpr, base_fpr = sm[0][1] / sum(sm[0]), bm[0][1] / sum(bm[0])
                gates = {'legacy_fp': lm[0][1] <= 3, 'legacy_fn': lm[1][0] <= old['legacy']['confusion_matrix'][1][0],
                         'super_sms_f1': scores['super_sms']['spam_f1'] >= old['super_sms']['spam_f1'] + .02,
                         'super_sms_ham_fpr': fpr <= .05 and fpr <= base_fpr + .01,
                         'prior_external_f1': scores['prior_external']['spam_f1'] >= old['prior_external']['spam_f1'],
                         'diagnostics': all(d['expected'] == d['predicted'] for d in diags)}
                entry = {'order': len(entries), 'family': family, 'representation': name, 'new_class_budget': budget,
                         'parameters': params, 'validation': scores, 'diagnostics': diags,
                         'gates': gates, 'eligible': all(gates.values())}
                entries.append(entry)
                def rank(e):
                    return (e['eligible'], np.mean([m['spam_f1'] for m in e['validation'].values()]), e['validation']['legacy']['spam_precision'], -e['order'])
                if family not in selected or rank(entry) > rank(selected[family]):
                    selected[family] = entry
                    joblib.dump(pipe, out / f'{family}.joblib')
                    export(pipe, family, out / f'{family}.json')
                report_path.write_text(json.dumps(report, indent=2) + '\n')
                print(json.dumps({'order': entry['order'], 'family': family, 'representation': name, 'budget': budget, 'eligible': entry['eligible'], 'failed_gates': [k for k, v in gates.items() if not v], 'legacy_cm': lm, 'super_sms_cm': sm, 'diagnostics': diags}), flush=True)
    assert len(entries) == protocol['candidate_count']
    for path, expected in {**served, **checksums}.items():
        assert digest(ROOT / path) == expected
    report['status'] = 'complete; candidates only; served models unchanged; all final tests unevaluated'
    report['artifact_sha256'] = {str(p.relative_to(ROOT)): digest(p) for p in out.iterdir() if p.suffix in ('.json', '.joblib')}
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print('COMPLETE', {f: {'order': e['order'], 'eligible': e['eligible']} for f, e in selected.items()}, flush=True)


if __name__ == '__main__':
    main()
