# Why the Super SMS candidates regressed

The comparison uses the saved revision 2 models and the selected Super SMS candidates on original validation and the three development diagnostics. No fitting, source-label changes, or final-test reads were performed. Reproduce with `../../work/messagecheck-venv/bin/python scripts/compare_super_sms.py`; detailed signed contributions and stable message IDs are in the [comparison report](../reports/super-sms-comparison.json).

## License reminder

Positive scores predict spam; negative scores predict ham. These are decision scores, not probabilities, and magnitudes should not be compared across model families.

| Family | Served score | Candidate score | Served model on v3-normalized input |
| --- | ---: | ---: | ---: |
| Naive Bayes | -0.0695 | +4.1503 | -0.7687 |
| Logistic regression | -0.0352 | +1.8421 | +1.0107 |

The served models' correct decisions were very close to zero. Both candidates recognize 46 features versus 29 for the served models, partly because candidates include bigrams.

For Naive Bayes, the prior stays essentially identical at -1.9497. Positive feature contributions grow from 3.5324 to 6.7576, while negative contributions weaken from -1.6521 to -0.6576. Leading candidate spam contributions include `on or` (+0.526), `official` (+0.380), `account at` (+0.361), `please log` (+0.350), `renewal on` (+0.336), and `for renewal` (+0.327). These are learned associations, not evidence that renewal messages are fraudulent. Normalizing the text alone makes the frozen served NB model more confidently ham, so preprocessing alone does not explain its candidate regression.

For logistic regression, the intercept changes from -3.4989 to -3.2600, positive feature contributions grow from 4.1315 to 5.5859, and negative contributions weaken from -0.6679 to -0.4837. Candidate contributors include `your` (+0.835), `to` (+0.427), `reply` (+0.410), `an` (+0.338), and `account` (+0.331). Normalizing the text before passing it to the unchanged served model already flips its label. Removing URL, number, and bracketed content changes the recognized tokens and their L2-normalized weights; even unchanged surviving coefficients can then contribute differently.

This frozen-model input transformation is a sensitivity check, not a retrained preprocessing ablation. Training data, vocabulary, IDF, ngrams, TF scaling, and classifier weights changed together in the experiment. It cannot establish the individual causal contribution of each change.

## Changed original-validation decisions

Naive Bayes has four new errors and one corrected error. Logistic regression has two new errors and two corrected errors. Net missed-spam counts alone hide this turnover.

| Message ID prefix | Source-labeled content summary | Newly wrong model | Served → candidate score |
| --- | --- | --- | --- |
| `02abbf9c353e` | Very short ringtone promotion with a number | NB | +1.136 → -1.950 |
| `5dd7ef98111b` | Picture-link notification/lure | NB | +2.383 → -0.838 |
| `c2a6ae06b999` | Balance claim and paid quiz/text-answer prompt | NB and LR | NB +0.471 → -0.512; LR +1.622 → -0.481 |
| `d7c83b3738ca` | Source-ham reference-check notification | NB | -2.772 → +0.049 |
| `075d3052f8d7` | Chat invitation containing premium-call pricing/contact details | LR | +0.502 → -0.810 |

The ringtone example has zero recognized candidate features, leaving NB to predict ham from its prior. The new pipeline strips numbers and its vocabulary does not represent the remaining text. The picture-link example also flips to ham when only v3 normalization is applied to the frozen served NB model, consistent with loss of URL-related evidence. The premium-chat example flips under the same input-only check for served LR. The quiz message exposes a broader learned-feature change: LR remains spam on normalized input under the served model but becomes ham under the candidate. The reference-check notice becomes a new, borderline NB false alarm.

These summaries describe dataset labels and text, not independently verified authenticity. Full messages and contact details are omitted from this document.

## What this supports next

A follow-up should isolate representation changes before increasing dataset size or changing thresholds. Start with a fixed legacy tokenization/TF-IDF configuration and the same prepared training mixture, keeping parameter and weighting choices explicit. Compare that controlled variant with the completed experiment on the same development sets. This would test whether preserving numeric/URL tokens and the legacy feature treatment recovers useful evidence; it would not assume that doing so solves every regression.

The normalization checks already show that aggressive text removal can matter, while NB's unchanged prior and changed feature contributions show that preprocessing is not the only issue. Do not add a license whitelist or change labels to force the three diagnostics to pass. Keep revision 2 served and record any new experiment as an adaptive follow-up, since these findings now inform its design.

All reported explanations were checked to sum with the model bias/prior to the actual decision score within numerical tolerance. This comparison changes no model artifacts.
