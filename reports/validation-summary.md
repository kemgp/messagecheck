# Validation results

Revision 2. These are reused development/validation results, not final-test estimates.

| Model | Spam precision | Spam recall | Spam F1 | False positives | False negatives |
| --- | ---: | ---: | ---: | ---: | ---: |
| naive_bayes | 98.88% | 91.67% | 95.14% | 1 | 8 |
| logistic_regression | 98.86% | 90.62% | 94.57% | 1 | 9 |

Revision 2: Naive Bayes unchanged. Moderate logistic class weighting chosen after user diagnostics; improves training-group CV and validation misses without increasing validation false alarms, while matching both user-supplied labels. Not the highest-F1 candidate in the separate broad experiment. No final-test evaluation.

All binary outputs remain counted, including borderline cases. Review notices are a separate interface feature.
