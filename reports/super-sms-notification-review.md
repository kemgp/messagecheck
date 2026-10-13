# Super SMS notification review

Reviewed 34 distinct CSV records: 16 labeled ham and 18 labeled spam. No source label was changed, and no message was approved for training.

## Findings

| Content-review outcome | Records |
| --- | ---: |
| label policy review | 3 |
| scam pattern review | 9 |
| promotion review | 6 |
| notification candidate | 5 |
| incomplete | 1 |
| outside notification scope | 10 |

The five notification candidates are CSV records **10917, 17958, 50956, 52775, and 63357**. They cover delivery, account verification, and account debit. These are content-compatible examples, not independently authenticated legitimate messages.

Three source-spam records (**463, 1278, 64348**) resemble routine OTP/payment/allotment notifications. Hold them for label-policy and provenance review. Do not flip their labels from wording alone.

Six other source-spam records contain advertising or mixed service/promotion content. Such labels may be consistent with an unwanted-message policy even when the message is not a scam. Nine have suspicious threat/link/callback patterns, but that does not independently prove fraud.

Ten ham matches are outside the notification scope, and one is truncated. Keyword-hit counts are therefore not usable-notification counts.

## Recommendation

Do not bulk-import this corpus to solve the notification false-positive gap. Keep these 34 records as review references. For future development, seek source/context evidence for the five notification candidates and resolve the three label-policy cases. Decide whether the product predicts unwanted spam or fraudulent/scam content before mixing labels across corpora. No corrected-label training set is produced by this review.

## Method and limitations

Up to four distinct normalized messages per regex category and source label, ordered by SHA-256; union with six previously inspected records. Categories overlap. No model predictions used.

Lossless Latin-1 decoding for inspection. UTF-8 and strict Windows-1252 fail; text artifacts remain unresolved.

This is an assistant content review of a targeted sample, not independent human annotation and not a statistical accuracy audit. The source CSV has only SMSes and Labels; individual sender, consent, and transaction context are absent. No model scores informed the review. The sample is development material and should not be presented as an independent test set.

Raw messages and contact/account details are omitted from this report. The JSON companion retains record references and message hashes for local verification. Record numbers include the CSV header and are not physical line numbers.

Source SHA-256: `ba825b468b59fb229cc56c15a6c2d14d593a88051d54ea2f402166bf2ab894d3`.

Source: [Super SMS repository](https://github.com/smspamresearch/spstudy). Attribution: Salman, Ikram, and Kaafar (2024), *Investigating Evasive Techniques in SMS Spam Filtering: A Comparative Analysis of Machine Learning Models*, IEEE Access. Dataset reuse terms remain to be clarified before redistribution.

## Record-level review

| CSV record | Original label | Outcome | Review reason |
| ---: | --- | --- | --- |
| 463 | spam | label policy review | Routine login OTP with a do-not-share instruction; text alone does not explain its spam label. |
| 1278 | spam | label policy review | Payment-success notice with a link; transaction context and destination authenticity are unavailable. |
| 9790 | spam | scam pattern review | Threat of account blocking combined with a demand to update documents through a supplied bank-themed domain. |
| 10523 | spam | promotion review | Savings-account acquisition and cashback advertising, rather than a transaction receipt. Unwanted marketing is distinct from fraud. |
| 10917 | ham | notification candidate | Delivery status with tracking and courier contact details; content fits an operational notification but origin is unverified. |
| 12238 | ham | incomplete | Truncated NEFT reference notice ending in an HTML fragment; insufficient message content. |
| 17422 | ham | outside notification scope | Personal discussion of an OTP implementation error, not an OTP notification. |
| 17958 | ham | notification candidate | Order-dispatch status and courier contact; content fits delivery notification but origin is unverified. |
| 20416 | spam | scam pattern review | Same-day account-block threat and net-banking login request through a supplied KYC-themed domain. |
| 21105 | spam | promotion review | Plumbing-service discount advertisement framed around a higher water bill. |
| 21168 | spam | scam pattern review | Missed-delivery lure with a redelivery-themed URL and deadline-like wording; no sender verification is available. |
| 22171 | spam | promotion review | Subscription entitlement combined with a claim invitation; whether this is unwanted promotion depends on context. |
| 22975 | ham | outside notification scope | Personal conversation containing the phrase your order; not a delivery notification. |
| 26155 | spam | scam pattern review | Account-suspension claim with an urgent callback demand; consistent with a suspicious pattern, not independently verified fraud. |
| 26852 | spam | scam pattern review | Account-lock claim demanding an immediate login; destination has been redacted, preventing authenticity assessment. |
| 27690 | ham | outside notification scope | Conversational remark about a bill amount, not a service-generated bill notice. |
| 27813 | ham | outside notification scope | A/c or non a/c is likely about air conditioning; no usable financial notification content. |
| 28690 | spam | promotion review | Order/bill update mixed with a discount offer for another product; separate promotional intent from fraud. |
| 28753 | ham | outside notification scope | Bank-detail listing with personal/business identifiers; not a transaction-status notification. |
| 35235 | spam | scam pattern review | Banking-suspension threat followed by an immediate document-update link. |
| 35804 | spam | scam pattern review | Rejected-bill warning and urgent callback mixed with unrelated text; both authenticity and text quality need review. |
| 42708 | ham | outside notification scope | Personal conversation about food delivery; not an automated delivery notice. |
| 47738 | ham | outside notification scope | Personal discussion using OTP in another context; keyword match is not a security notification. |
| 50196 | ham | outside notification scope | Software-project discussion about an OTP function rather than a service notification. |
| 50956 | ham | notification candidate | Delivery notice with cash-on-delivery amount and tracking link; fits operational content, but the transaction is unverified. |
| 52160 | spam | scam pattern review | Generic delivery claim followed by an unexplained domain; may be a delivery lure, but no contextual verification is available. |
| 52775 | ham | notification candidate | Account-verification OTP with an expiry period; operational wording, not independently authenticated. |
| 54133 | spam | promotion review | Coupon and time-limited savings advertisement; no transaction-status purpose. |
| 60137 | spam | scam pattern review | Bank-document expiry and account-block claim requesting net-banking action through a supplied domain. |
| 63357 | ham | notification candidate | Account-debit notification with redacted account/cheque details; operational content, origin unverified. |
| 64348 | spam | label policy review | OTP and agricultural allotment/subsidy details resemble an operational notice; spam label needs source context. |
| 65464 | ham | outside notification scope | Personal conversation about forwarding an OTP; not a suitable example of a safe service notification. |
| 65606 | spam | promotion review | Recharge success mixed with a data-offer activation instruction and romanized Hindi; not a clean English-only receipt. |
| 66830 | ham | outside notification scope | Personal bank/account and birth-date listing; not a notification and unnecessary for this dataset gap. |
