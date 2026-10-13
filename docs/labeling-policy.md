# Labeling policy for new examples

Policy version: 1, 2026-10-13. MessageCheck predicts **spam versus non-spam (ham)**. Spam includes unsolicited advertising and scam attempts. A spam prediction is not proof of fraud, and a ham prediction does not authenticate a sender, link, or payment request.

This policy guides new curated examples and future experiments. Existing corpora retain their source labels and documented limitations; this document does not retroactively verify or relabel them. The served revision 2 models are unchanged.

## Label decisions

| Content and available context | Decision |
| --- | --- |
| Expected receipt, OTP, delivery update, or account/service notice supported by recipient or source context | `ham` |
| Ordinary personal communication with enough context to establish its purpose | `ham` |
| Advertising documented as unsolicited or unwanted | `spam` |
| A scam attempt supported by evidence, or an explicit coercive demand such as “You have been hacked! Pay within 12 hours!” | `spam`; record whether the decision rests on context or explicit content |
| Advertising with unknown consent, mixed service/promotion content with unclear purpose, or a routine-looking notice with unknown origin | `uncertain`; hold out of the curated training and scored evaluation sets |
| Truncated, corrupted, or out-of-scope text that cannot be reviewed reliably | `exclude`; record the reason |

`uncertain` and `exclude` are review dispositions, not new classifier outputs. An OTP, amount, URL, urgent deadline, or brand name alone does not determine the label. Legitimate advertising can still be spam when unsolicited. A message need not be fraudulent to be spam.

For mixed service and promotional messages, use evidence about the recipient's expectations and the promotional content. If that context cannot resolve the label, keep the example uncertain. Do not infer English-language suitability merely from the absence of Bengali script; romanized non-English text also needs review.

## Evidence and review

Use the [example review template](example-review-template.md) for each candidate. Preserve its original source label separately from the proposed project label. Record the dataset/file, CSV record including header, source checksum or message hash, and a concise reason for the decision. For contributed messages, record permission and recipient context without retaining unnecessary personal details.

Describe evidence honestly: recipient-confirmed, source-documented, explicit-content judgment, or wording-only. Routine notification wording alone cannot establish legitimacy. Never change a label to agree with a model prediction. Make the initial label decision without viewing model scores; record any later disagreement separately. Seek a second reviewer for disputed labels and keep unresolved cases on hold.

Keep original downloads intact. Store any permitted working copy privately and redact names, account identifiers, OTP values, and personal contact details before sharing. Record redaction because it can alter model features. Keep provenance and reuse terms with the source; unresolved reuse terms do not authorize redistribution. Do not open suspicious links to investigate a label.

## From review to an experiment

1. Approve only candidates with a supported label, adequate text quality, and a documented basis for the intended use. A completed review is not an automatic import.
2. Audit exact, normalized, and related-template duplicates against existing corpora. Quarantine conflicting labels for review; do not resolve them by majority vote alone. Keep related templates in one partition, including redacted variants.
3. Keep already inspected examples and user-reported failures as development references. Do not present them as a fresh independent test set. Have the split/audit process protect existing reserved test groups without using their model outcomes for development.
4. Before training, record the mixture, grouping/split method, selection criteria, and acceptable false-alarm/missed-spam tradeoff. Fit vocabulary and all learned preprocessing on training data only.
5. Compare candidates on development partitions, report false positives and false negatives separately, and revisit the hacking/payment and legitimate license diagnostics. Freeze model choices before final-test evaluation.

## Current review queue

The [Super SMS review](../reports/super-sms-notification-review.md) is a targeted content review, not an authentication or accuracy audit. Its five notification candidates (CSV records 10917, 17958, 50956, 52775, 63357) still need supporting context. The three source-spam policy cases (463, 1278, 64348) remain unresolved; notification-like wording does not justify flipping their labels. None is approved for training.

The Financial Scams and Super SMS datasets should not be bulk-merged to address the notification gap. First gather supported examples across receipts, OTPs, deliveries, account notices, unwanted promotions, and scam attempts. Document coverage gaps rather than claiming that a small curated collection represents real-world prevalence.
