# Super SMS controlled experiment

Eight candidates were evaluated. None passed the predefined adoption gates, so revision 2 remains served. The selected analysis candidates improve performance on source-labeled external validation data and detect the hacking/payment diagnostic, but both flag the legitimate license reminder and miss more original-validation spam.

## Protocol and partitions

The [protocol](../reports/super-sms-v1-protocol.json) was saved before candidate fitting and validation scoring. A SHA-256 hash of `super-sms-v1:` plus the template group ID assigns groups to approximately 60% training, 20% validation, and 20% reserved test. All 59,615 prepared IDs occur exactly once, and no group crosses partitions.

| New partition | Ham | Spam | Total | Groups |
| --- | ---: | ---: | ---: | ---: |
| Training | 21,413 | 14,289 | 35,702 | 34,957 |
| Validation | 7,303 | 4,859 | 12,162 | 11,868 |
| Reserved test | 7,051 | 4,700 | 11,751 | 11,523 |

New test rows were allocated during splitting and never reopened or scored. Neither existing final-test partition was opened. Test counts describe allocation, not model results. Earlier preparation protected existing evaluation examples through source-corpus overlap checks.

Training combines the new training partition with the original 3,612 training messages. Prior Mendeley/IMC training examples are not added. The prior external validation partition is retained as a third development check alongside original and Super SMS validation.

The fixed grid is two word representations (unigrams; unigrams plus bigrams), two new-data weight budgets (0.25; 1.0), and two families (Naive Bayes alpha 0.1; logistic regression C 10). Each new template group has equal total mass within its class. Each new class's total classifier weight equals its budget times the original training count for that class. Original rows have weight one. Vocabulary and IDF are fitted on combined training text and are not weighted by these classifier weights. No thresholds were tuned.

Adoption requires original false positives at most three, original false negatives no worse than the served family, Super SMS spam F1 improvement of at least 0.02, Super SMS ham false-positive rate at most 5% and no more than one percentage point above baseline, prior external F1 no worse than baseline, and all three diagnostics correct. Ranking favors eligible candidates, then mean spam F1 across the three validation domains, then original precision and earlier order.

## Results

The selected analysis candidate for each family uses word unigrams plus bigrams and budget 1.0. “Selected” here means retained for analysis; neither is eligible for adoption.

| Model | Original FP / FN | Super SMS FP / FN | Super SMS spam F1 | Prior external spam F1 |
| --- | --- | --- | ---: | ---: |
| Served Naive Bayes | 1 / 8 | 23 / 3,243 | 0.4974 | 0.4610 |
| Candidate Naive Bayes | 1 / 11 | 22 / 324 | 0.9633 | 0.9280 |
| Served logistic regression | 1 / 9 | 32 / 3,469 | 0.4426 | 0.3794 |
| Candidate logistic regression | 0 / 10 | 20 / 484 | 0.9455 | 0.8881 |

All eight candidates fail the original missed-spam gate and the diagnostic gate. Every candidate predicts spam for the legitimate license reminder. The selected candidates correctly predict spam for both the parcel-fee and hacking/payment examples. The full grid, confusion matrices, baseline diagnostics, counts, and checksums are in the [experiment report](../reports/super-sms-v1-experiment.json); the [adoption decision](../reports/super-sms-v1-adoption-decision.json) records non-adoption and verification.

These validation results informed selection and are not unbiased final-test estimates. Labels are source-provided, not independently authenticated. Grouping reduces detectable template leakage but cannot guarantee all paraphrases are isolated. The old external validation set and user diagnostics have already influenced earlier experiments. Neither large external gains nor a correct diagnostic establishes general real-world reliability.

## Artifacts and verification

New split files are under `data/super-sms-v1/`; candidate models are under `models/super-sms-v1/`. Prepared input files, existing partitions, app imports, and served models are unchanged. Data files and Python joblib artifacts remain ignored by Git.

Checks verified complete/disjoint group assignments, deterministic splits, preserved input and served-model hashes, and classifier convergence. Browser parity passed 15,580 development and edge cases per model, including all three validation domains. Labels, TF-IDF values, scores, and explanations match Python; maximum score errors were approximately 1.28e-13 for Naive Bayes and 7.99e-15 for logistic regression. No application build was needed because app code and imports were unchanged.

With the existing ML virtual environment:

```sh
../../work/messagecheck-venv/bin/python scripts/train_super_sms.py
../../work/messagecheck-venv/bin/python scripts/make_parity_fixtures.py /tmp/messagecheck-super-sms-parity.json --model-dir models/super-sms-v1 --external --super-sms
node scripts/check-parity.mjs /tmp/messagecheck-super-sms-parity.json models/super-sms-v1
```

The training script intentionally refuses to overwrite an existing protocol. Reproduction requires a clean checkout/output location with the matching local source data and preparation artifacts. Use a distinct, explicitly documented run name for a new experiment rather than overwriting this record.

The [feature and regression comparison](super-sms-comparison.md) investigates the license false alarm and additional original-validation misses using development data only. Any revised feature, weighting, or grid choice must be recorded as an adaptive follow-up experiment. This run does not justify deploying a candidate or opening the final tests.
