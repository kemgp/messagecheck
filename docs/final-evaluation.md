# Frozen revision 2 and final evaluation

On 2026-10-14 (Asia/Manila), the served revision 2 models were frozen before held-out scoring. The [freeze record](../reports/final-model-freeze.json) records hashes of Python pipelines, browser exports, inference code, test files, and the decision/evaluation policy. No model was retrained, replaced, or retuned. The outstanding legacy-feature experiment is deferred.

## Primary UCI test

The primary evaluation contains 773 messages: 677 ham and 96 spam. Models were trained on 3,612 original training messages and selected using development data. The majority baseline always predicts ham, based on the training majority, not the test labels.

| Method | Accuracy | Spam precision | Spam recall | Spam F1 | Macro F1 | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Naive Bayes | 98.06% | 100.00% | 84.38% | 91.53% | 95.21% | 0 | 15 |
| Logistic regression | 98.06% | 98.80% | 85.42% | 91.62% | 95.26% | 1 | 14 |
| Always ham | 87.58% | 0.00% | 0.00% | 0.00% | 46.69% | 0 | 96 |

Confusion matrices use actual rows and predicted columns in `[ham, spam]` order: NB `[[677, 0], [15, 81]]`; LR `[[676, 1], [14, 82]]`. One message has no known terms for each model. NB shows seven borderline notices and LR thirteen. All underlying binary predictions remain counted, even when the interface shows insufficient evidence or a review notice.

The small F1 difference is descriptive; no statistical superiority claim is made. A 100% observed precision here is not a guarantee against future false alarms.

## Supplemental tests

These partitions were designated supplemental before scoring. They have different sources, label provenance, and class balances and are not pooled into the primary metrics.

| Dataset | Ham / spam | Model | Spam recall | Spam F1 | FP | FN |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Mendeley / IMC | 90 / 2,750 | NB | 29.89% | 46.02% | 0 | 1,928 |
| Mendeley / IMC | 90 / 2,750 | LR | 21.96% | 36.02% | 0 | 2,146 |
| Super SMS | 7,051 / 4,700 | NB | 33.94% | 50.53% | 18 | 3,105 |
| Super SMS | 7,051 / 4,700 | LR | 28.11% | 43.69% | 26 | 3,379 |

The low supplemental recall shows limited generalization to these sources. It reinforces the known hacking/payment diagnostic failure and prevents a broad modern-scam detection claim. Source labels are not independent authentication. Template grouping and protected-corpus filtering reduce detectable overlap but cannot guarantee separation of every paraphrase. Source text was processed during earlier automated duplicate/group audits; held-out predictions were not used for selection.

## Artifacts and reproducibility

- [Final report](../reports/final-test-report.json): full metrics, supports, baseline results, interface-notice counts, hashes, and environment.
- `reports/final-{uci,external,super_sms}-predictions.jsonl`: per-message IDs, labels, scores, and known-feature counts; no raw message text.
- `scripts/evaluate_final.py`: records the freeze before loading test rows, verifies manifest membership/group separation, evaluates frozen pipelines, and creates temporary parity fixtures.
- The app imports the final report and displays primary metrics, confusion matrices, and separate supplemental results.

Run `../../work/messagecheck-venv/bin/python scripts/evaluate_final.py` only in a clean reproduction checkout containing the matching local models and data. It refuses to overwrite an existing freeze. Then run `node scripts/check-parity.mjs /tmp/messagecheck-final-parity.json`. Preserve the existing records; any necessary implementation correction needs a separately documented rerun, never performance-driven test tuning.

Parity passed all 15,364 held-out messages per model: zero label mismatches, matching sparse TF-IDF values, decision scores, explanation sums, and borderline notices. Maximum score errors were 4.80e-14 (NB) and 5.33e-15 (LR), below 1e-10. Independent recounts from saved predictions matched confusion matrices, supports, and accuracy. Frozen model/inference and test hashes were unchanged.

The production build passed with the existing bundle-size advisory (approximately 311 KB gzip for JavaScript). Server-rendered dashboard checks verified final metrics, dataset counts, confusion-matrix content, and removal of the validation-only badge. No browser was available through the UI tools for a new visual inspection; desktop/mobile layout and device benchmarking remain the next roadmap tasks. Deployment and the paper are not completed by this evaluation.
