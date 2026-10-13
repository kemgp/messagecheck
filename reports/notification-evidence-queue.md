# Notification evidence queue

Eight existing Super SMS leads have been entered using the review-template fields: five source-ham candidates and three unresolved source-spam cases. All remain **uncertain / hold**, with no partition assigned. No new recipient evidence has been supplied.

This queue is initialized from the [earlier content review](super-sms-notification-review.md), not a new authentication check. The [JSON records](notification-evidence-queue.json) preserve original labels, source/message hashes, review reasons, and missing evidence without copying raw messages.

| Source CSV record | Source label | Category | Evidence needed |
| ---: | --- | --- | --- |
| 463 | spam | OTP | Evidence that the recipient initiated this login and that the OTP came from the service; explanation of the original spam label. |
| 1278 | spam | receipt | Confirmation of the referenced payment from recipient or source records, plus an explanation of the spam label. A payment-success claim alone is insufficient. |
| 10917 | ham | delivery | Confirmation that the recipient expected this shipment and that the delivery notice corresponds to it. |
| 17958 | ham | delivery | Confirmation of the order and dispatch from recipient or documented source context. |
| 50956 | ham | delivery | Confirmation of the expected order, cash-on-delivery arrangement, and courier notification. |
| 52775 | ham | OTP | Confirmation that the recipient initiated account verification with the named service. |
| 63357 | ham | account notice | Confirmation that the debit corresponds to a recipient-known transaction and service notice. |
| 64348 | spam | OTP | Confirmation of the subsidy/allotment interaction and requested OTP; explanation of the original spam label. |

## Current scope: existing datasets only

The user selected existing datasets only. Personal contributions are not part of the current collection plan. Use available source documentation and original labels, recording missing sender, consent, or transaction context as unknown. Do not promote these leads to verified examples or reverse their source labels based on wording alone.

The [direct overlap audit](notification-overlap-audit.json) compared all eight leads with Super SMS, the original cleaned corpus, staged external candidates, and Financial Scams. Record 1278 has two matching records: one within Super SMS and one in the staged external data. The other seven have no direct matches under lowercase/whitespace equality, revision 3 normalization, or word-trigram Jaccard at least 0.8. This is a direct comparison, not complete template grouping, and it does not establish authenticity. No final-test files or model predictions were read.

These eight already inspected leads remain development references. All source labels and hold decisions are preserved. Existing dataset labels can support source-labeled experiments with disclosed limitations; they must not be described as independently verified ground truth.

## Remaining collection gaps

The source-ham leads cover three delivery notices, one OTP, and one debit notice. They do not yet provide a verified payment receipt or a broad range of account notices. The three source-spam cases cannot fill those gaps until their labels and context are resolved. No representative performance or coverage claim follows from these counts.

If original recipient or source context cannot be obtained for a lead, leave it unresolved and collect a different supported example. Re-reading the wording cannot supply the missing context.
