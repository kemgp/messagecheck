# MessageCheck limitations

Applies to the frozen revision 2 models. Updated 2026-10-15.

MessageCheck is a research prototype that classifies SMS text as spam or non-spam. **A non-spam prediction does not establish that a message is safe.** The app cannot authenticate a sender, inspect a destination website, or verify a payment request. Its output should not be the sole basis for clicking a link, sharing information, or sending money.

## Detection errors and generalization

Both models can miss spam and flag legitimate messages. On the primary UCI test set of 773 messages, both achieved 98.06% accuracy, but Naive Bayes missed 15 of 96 spam messages and logistic regression missed 14. Naive Bayes produced zero false alarms in this sample; logistic regression produced one. Zero observed false alarms does not guarantee zero future false alarms.

Performance was substantially weaker on the supplemental test sets:

| Held-out dataset | Naive Bayes spam recall | Logistic regression spam recall |
| --- | ---: | ---: |
| UCI SMS Spam Collection | 84.38% | 85.42% |
| Mendeley / IMC | 29.89% | 21.96% |
| Super SMS | 33.94% | 28.11% |

Recall is the fraction of source-labeled spam detected. These results show limited generalization across SMS sources and do not establish reliable detection of current scams. The development example “You have been hacked! Pay within 12 hours!” remains a known false negative for both served models. It is a diagnostic example, not independent test evidence.

The test sets differ in class balance and collection methods. Their results are reported separately; the primary accuracy must not be presented as expected accuracy for all incoming messages. The small difference between the models' primary-test F1 scores does not establish statistical superiority. See the [final evaluation](final-evaluation.md) and [full metrics](../reports/final-test-report.json).

## Data and label limitations

The served models were trained on 3,612 messages from the older UCI corpus. They do not learn automatically from pasted messages or update themselves as scams change. External-data experiments were not adopted because they introduced unacceptable development regressions.

Dataset labels describe spam/non-spam decisions, not verified safe/unsafe status. Unsolicited advertising can be spam without being fraudulent. Expected receipts, OTPs, and delivery notices can resemble scam messages; recipient expectations and transaction context are often absent from the datasets.

Duplicate and template grouping reduces detectable overlap between partitions but cannot identify every paraphrase. Earlier automated source-corpus audits processed texts for overlap checks; final-test predictions were not used for model selection. Source-label quality and sampling biases remain limitations even after cleaning and grouping. The [labeling policy](labeling-policy.md) explains how ambiguous new examples are handled.

## Language and text representation

The project focuses on English SMS text. It has not established performance on Filipino, code-switched messages, or other languages. The served tokenizer uses lowercase ASCII letters and digits, so it does not fully represent non-ASCII writing systems.

TF-IDF word unigrams represent weighted token counts, not full sentence meaning, conversational context, or sender intent. Wording changes, unfamiliar terms, obfuscation, and missing context can change predictions. A message with no vocabulary matches has a binary prediction driven by the model's prior or intercept; the interface instead highlights insufficient known words. That underlying binary prediction is still counted in evaluation.

## Scores and explanations

Decision scores are not calibrated probabilities or verified confidence percentages. The borderline notice uses an absolute score below 0.5 with known terms; this is an interface heuristic, not a validated uncertainty estimate. Agreement between the two models does not authenticate a message.

Highlighted terms explain mathematical score contributions. They show learned associations and do not establish causal reasons, fraud, or intent. Common words and legitimate notification phrases can contribute toward spam. Python/JavaScript parity verifies implementation consistency, not whether a prediction is correct.

## Privacy and offline behavior

The application performs inference in the browser and contains no message-history or message-upload feature. In the user's local check, no new requests were observed during analysis, and predictions continued to work offline after the page had loaded.

This was a limited user-reported observation, not a comprehensive security audit or deployed-site network inspection. Offline inference after loading does not establish that a fresh page can load offline. Hosting behavior, browser extensions, and later integrations were not covered by that check. See the [verification record](../reports/frontend-verification.md).

## Performance and device coverage

Local measurements on a MacBook Air M4 running macOS Sequoia 15.7.7 and Chrome 154.0.8037.98 (arm64) showed a median combined computation time of 0.2 ms and nearest-rank p95 of 0.6 ms over 20 same-message trials after a confirmed warm-up. The display rounds to 0.1 ms. These timings cover both models' computation, including explanations, but exclude initial loading and result rendering. They do not establish performance across message lengths or devices.

Five localhost reloads with cache disabled and no throttling had a median browser Load time of 338 ms. This is not hosted-site loading time or a measurement of confirmed application readiness. The small samples do not support broad tail-latency guarantees.

The user reported that the app worked acceptably on a phone. The phone model, browser, test cases, and timing results were not recorded, so this is a qualitative usability observation rather than a controlled mobile benchmark. Comprehensive accessibility and cross-browser testing have not been documented.

## Scope and future changes

The interface accepts pasted text up to 5,000 characters. It does not read the user's SMS inbox, inspect screenshots, block messages, or take actions on the user's behalf.

Revision 2 was frozen before final scoring. Final-test results must not be used to tune this release's features, thresholds, or models. Future model improvements require a separately documented study and appropriate evaluation data; they cannot inherit the frozen revision's performance claims automatically.
