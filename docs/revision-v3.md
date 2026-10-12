# External-data model experiment

## Outcome

36 candidates were trained and compared. No candidate was adopted in the app. The most promising aggregate-eligible logistic model catches the user's hacking/payment threat, but regresses the previously correct legitimate license reminder. The current served revision 2 models remain unchanged, including their known threat false negative.

| Logistic model | Original validation false alarms / misses | External validation false alarms / misses |
| --- | --- | --- |
| Served revision 2 | 1 / 9 | 0 / 1,956 |
| Experimental word-bigram C=10, external spam weight 0.10 | 3 / 7 | 0 / 222 |

Original validation contains 678 legitimate and 96 spam messages. External validation contains only 72 legitimate and 2,554 spam messages. Zero external false alarms on this small and source-specific legitimate sample does not establish real-world reliability. The candidate predicts spam for all three supplied development examples, including the license reminder labeled legitimate by the user.

## Preparation

`prepare_v3.py` reads the staged external candidates and the original cleaned corpus for overlap protection. It removes bracket/redaction artifacts, explicit URLs, selected bare-domain forms, email addresses, and numbers before retaining ASCII word tokens. This loses potentially useful URL/number information deliberately to reduce source-specific shortcuts. It does not verify domains or sender identity.

Equal normalized texts and word-trigram sets with Jaccard similarity at least 0.80 form connected components. New components touching any original message are excluded. Components with conflicting binary labels are excluded. Repeated normalized messages are collapsed. IMC conversational categories (`wrong number`, `hey mum/dad`) and IMC messages with fewer than eight normalized words are excluded by a fixed rule because their standalone label often needs context. Remaining source labels are inherited, not independently verified.

Group hashes assign approximately 60/20/20 to new training, validation, and reserved test partitions. Already inspected hacking examples are development material and their entire component is assigned to training. The user's exact diagnostic is not inserted as a training row. Near-duplicate grouping is a heuristic, not proof of no semantic overlap.

- External training: 8,187 messages (7,952 spam, 235 ham).
- External validation: 2,626 messages (2,554 spam, 72 ham).
- Reserved external test: 2,840 messages (2,750 spam, 90 ham).
- Combined training: 11,799 messages, including the unchanged 3,612 original training messages.

The original split files are preserved. Neither final-test partition was evaluated. Preparation touches original cleaned texts only to exclude overlaps; it does not compute test predictions or metrics.

## Experiment and selection history

The first 12 candidates compare word unigrams, word unigrams+bigrams, and character 3–5-grams. Each representation uses Naive Bayes alpha 0.1/0.5 and logistic regression C 3/10, sublinear TF, training-only vocabulary/IDF, min_df=2, and at most 30,000 features. Logistic regression uses liblinear, seed 42, and a 2,000-iteration limit; convergence is checked. The score cutoff remains zero.

Original rows and added legitimate rows receive classifier weight 1. Added spam rows first share mass 1 per template component. Their total classifier weight is then scaled to 0.75 times the combined training ham count. Vocabulary and IDF still see all training rows; sample weighting applies to the classifier, not vectorizer fitting.

All first-round candidates failed the false-alarm gate. A documented adaptive follow-up repeated the same 12 settings with external-spam budgets of 0.10 and 0.25. These are reused development comparisons, not independent performance estimates. Each run writes its protocol before fitting.

Aggregate eligibility requires original false alarms <=3, original misses no higher than the served family baseline, external ham false-positive rate <=5%, and external spam F1 at least 0.05 above the served baseline. Eligible candidates are ranked by equal-weight mean spam F1 across the two validation domains, then original precision and candidate order. Four low-weight logistic candidates qualify; the word-bigram C=10 candidate ranks first. `selected` in its experiment JSON means an experimental aggregate winner, not deployment approval.

Final diagnostic review rejected adoption because all candidates misclassify the legitimate license reminder. This is an additional development regression review, not a predeclared statistical gate and not independent test evidence. No thresholds were tuned, no outcomes were hardcoded, and no synthetic examples were inserted to force the user's sentence to pass.

## Reproduce

Use the pinned Python environment from `requirements.txt`:

```sh
python scripts/prepare_v3.py
python scripts/check_v3_data.py
python scripts/check_v3_features.py
python scripts/train_v3.py
python scripts/train_v3.py --budget 0.1 --run-name v3-weight010
python scripts/train_v3.py --budget 0.25 --run-name v3-weight025
python scripts/make_parity_fixtures.py /tmp/v3-parity.json --model-dir models/v3-weight010 --external
node scripts/check-parity.mjs /tmp/v3-parity.json models/v3-weight010
python scripts/make_parity_fixtures.py /tmp/current-parity.json --external
node scripts/check-parity.mjs /tmp/current-parity.json
npm run build
```

The candidate directory contains only the eligible logistic model; parity checks explicitly fall back to the current Naive Bayes model for that family. Frontend inference supports the experimental normalizer, n-grams, and sublinear counts while retaining revision 2 behavior. App imports still point to current `models/*.json`.

Reports: `reports/v3-data-preparation.json`, `reports/v3-experiment.json`, `reports/v3-weight010-experiment.json`, and `reports/v3-weight025-experiment.json`. Each training report records the candidate results and selection history; preparation records partition hashes and exclusions. Raw source hashes and licenses remain in the intake audit.

## Next evidence needed

The new corpus improves scam coverage, but contributes few legitimate security, account, government, and payment notifications. Add independently labeled legitimate examples in these categories and review ambiguous scam reports before another model-selection cycle. Keep future training examples separate from grouped validation/test material. Do not rebrand the candidate's high external spam recall as general scam safety or final-test performance.
