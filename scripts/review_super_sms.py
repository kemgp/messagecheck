"""Reproduce a content-only notification review; never change labels or train."""
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path

from text_v3 import normalize_v3

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHA = 'ba825b468b59fb229cc56c15a6c2d14d593a88051d54ea2f402166bf2ab894d3'
PATTERNS = {
    'account_security': r'\b(?:otp|one.?time password|verification code|account.{0,30}(?:blocked|suspended|locked)|(?:suspicious|unauthorized).{0,30}(?:activity|login|transaction))\b',
    'payments': r'\b(?:payment.{0,30}(?:successful|received|completed|processed)|transaction.{0,40}(?:successful|completed|declined)|(?:credited|debited).{0,30}(?:account|rs)|a/c|neft|salary credited)\b',
    'delivery': r'\b(?:out for delivery|your (?:order|parcel|package)|(?:order|parcel|package).{0,30}(?:shipped|dispatched|delivered|tracking)|tracking (?:id|number))\b',
    'billing_service': r'\b(?:your.{0,25}(?:bill|subscription)|(?:bill|subscription).{0,35}(?:due|paid|renew|expire)|recharge.{0,20}successful|appointment.{0,20}(?:confirmed|reminder))\b',
}

# These decisions are explicit assistant content-review judgments, not model outputs.
# The original numeric label remains immutable and no replacement label is assigned.
DECISIONS = {
    463: ('label_policy_review', 'Routine login OTP with a do-not-share instruction; text alone does not explain its spam label.'),
    1278: ('label_policy_review', 'Payment-success notice with a link; transaction context and destination authenticity are unavailable.'),
    9790: ('scam_pattern_review', 'Threat of account blocking combined with a demand to update documents through a supplied bank-themed domain.'),
    10523: ('promotion_review', 'Savings-account acquisition and cashback advertising, rather than a transaction receipt. Unwanted marketing is distinct from fraud.'),
    10917: ('notification_candidate', 'Delivery status with tracking and courier contact details; content fits an operational notification but origin is unverified.'),
    12238: ('incomplete', 'Truncated NEFT reference notice ending in an HTML fragment; insufficient message content.'),
    17422: ('outside_notification_scope', 'Personal discussion of an OTP implementation error, not an OTP notification.'),
    17958: ('notification_candidate', 'Order-dispatch status and courier contact; content fits delivery notification but origin is unverified.'),
    20416: ('scam_pattern_review', 'Same-day account-block threat and net-banking login request through a supplied KYC-themed domain.'),
    21105: ('promotion_review', 'Plumbing-service discount advertisement framed around a higher water bill.'),
    21168: ('scam_pattern_review', 'Missed-delivery lure with a redelivery-themed URL and deadline-like wording; no sender verification is available.'),
    22171: ('promotion_review', 'Subscription entitlement combined with a claim invitation; whether this is unwanted promotion depends on context.'),
    22975: ('outside_notification_scope', 'Personal conversation containing the phrase your order; not a delivery notification.'),
    26155: ('scam_pattern_review', 'Account-suspension claim with an urgent callback demand; consistent with a suspicious pattern, not independently verified fraud.'),
    26852: ('scam_pattern_review', 'Account-lock claim demanding an immediate login; destination has been redacted, preventing authenticity assessment.'),
    27690: ('outside_notification_scope', 'Conversational remark about a bill amount, not a service-generated bill notice.'),
    27813: ('outside_notification_scope', 'A/c or non a/c is likely about air conditioning; no usable financial notification content.'),
    28690: ('promotion_review', 'Order/bill update mixed with a discount offer for another product; separate promotional intent from fraud.'),
    28753: ('outside_notification_scope', 'Bank-detail listing with personal/business identifiers; not a transaction-status notification.'),
    35235: ('scam_pattern_review', 'Banking-suspension threat followed by an immediate document-update link.'),
    35804: ('scam_pattern_review', 'Rejected-bill warning and urgent callback mixed with unrelated text; both authenticity and text quality need review.'),
    42708: ('outside_notification_scope', 'Personal conversation about food delivery; not an automated delivery notice.'),
    47738: ('outside_notification_scope', 'Personal discussion using OTP in another context; keyword match is not a security notification.'),
    50196: ('outside_notification_scope', 'Software-project discussion about an OTP function rather than a service notification.'),
    50956: ('notification_candidate', 'Delivery notice with cash-on-delivery amount and tracking link; fits operational content, but the transaction is unverified.'),
    52160: ('scam_pattern_review', 'Generic delivery claim followed by an unexplained domain; may be a delivery lure, but no contextual verification is available.'),
    52775: ('notification_candidate', 'Account-verification OTP with an expiry period; operational wording, not independently authenticated.'),
    54133: ('promotion_review', 'Coupon and time-limited savings advertisement; no transaction-status purpose.'),
    60137: ('scam_pattern_review', 'Bank-document expiry and account-block claim requesting net-banking action through a supplied domain.'),
    63357: ('notification_candidate', 'Account-debit notification with redacted account/cheque details; operational content, origin unverified.'),
    64348: ('label_policy_review', 'OTP and agricultural allotment/subsidy details resemble an operational notice; spam label needs source context.'),
    65464: ('outside_notification_scope', 'Personal conversation about forwarding an OTP; not a suitable example of a safe service notification.'),
    65606: ('promotion_review', 'Recharge success mixed with a data-offer activation instruction and romanized Hindi; not a clean English-only receipt.'),
    66830: ('outside_notification_scope', 'Personal bank/account and birth-date listing; not a notification and unnecessary for this dataset gap.'),
}


def main():
    path = ROOT / 'data/raw/super_sms_dataset.csv'
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA, 'Source changed; re-review record references.'
    rows = list(csv.DictReader(io.StringIO(raw.decode('latin-1'), newline='')))
    selected, pool_counts = {}, {}
    for category, pattern in PATTERNS.items():
        for label in ('0', '1'):
            candidates, seen = [], set()
            for record, row in enumerate(rows, 2):
                key = normalize_v3(row['SMSes'])
                if row['Labels'] == label and key and key not in seen and re.search(pattern, row['SMSes'], re.I):
                    seen.add(key)
                    candidates.append((hashlib.sha256(key.encode()).hexdigest(), record))
            candidates.sort()
            pool_counts[f'{category}:{label}'] = len(candidates)
            for _, record in candidates[:4]:
                selected.setdefault(record, []).append(category)
    for record in (463, 1278, 10917, 17958, 52775, 63357):
        selected.setdefault(record, []).append('previously_inspected')
    assert set(selected) == set(DECISIONS), 'Sample changed; every selected record needs a review decision.'
    reviews = []
    for record, categories in sorted(selected.items()):
        row = rows[record - 2]
        disposition, reason = DECISIONS[record]
        reviews.append({'csv_record_including_header': record, 'source_label': row['Labels'],
                        'source_label_name': 'ham' if row['Labels'] == '0' else 'spam',
                        'message_sha256': hashlib.sha256(row['SMSes'].encode()).hexdigest(),
                        'sample_categories': categories, 'disposition': disposition, 'reason': reason,
                        'authenticity_verified': False, 'approved_for_training': False})
    report = {
        'source_file': str(path.relative_to(ROOT)), 'source_sha256': EXPECTED_SHA,
        'source_url': 'https://github.com/smspamresearch/spstudy',
        'citation': 'Salman, Ikram, and Kaafar (2024), Investigating Evasive Techniques in SMS Spam Filtering: A Comparative Analysis of Machine Learning Models, IEEE Access.',
        'review_type': 'Assistant qualitative content review; not independent annotation or sender/transaction verification.',
        'sample_method': 'Up to four distinct normalized messages per regex category and source label, ordered by SHA-256; union with six previously inspected records. Categories overlap. No model predictions used.',
        'encoding': 'Lossless Latin-1 decoding for inspection. UTF-8 and strict Windows-1252 fail; text artifacts remain unresolved.',
        'record_numbering': 'Parsed CSV record position including the header, not physical file line number.',
        'pool_counts': pool_counts, 'patterns': PATTERNS,
        'review_counts': dict(Counter(r['disposition'] for r in reviews)),
        'label_counts': dict(Counter(r['source_label_name'] for r in reviews)),
        'limitations': ['Small deliberately targeted sample, not representative; counts are not dataset error rates.',
                       'Regex hits include personal conversations, promotions, and misleading abbreviations.',
                       'Source label spam may describe unwanted marketing rather than fraudulent content.',
                       'No individual source, sender, consent, or transaction evidence is available in the two-column CSV.',
                       'Candidate notifications are development leads, not a verified evaluation set.',
                       'No source relabeling, dataset filtering, model evaluation, or training performed.'],
        'records': reviews,
    }
    output = ROOT / 'reports/super-sms-notification-review.json'
    output.write_text(json.dumps(report, indent=2) + '\n')
    lines = ['# Super SMS notification review', '',
             'Reviewed 34 distinct CSV records: 16 labeled ham and 18 labeled spam. No source label was changed, and no message was approved for training.', '',
             '## Findings', '', '| Content-review outcome | Records |', '| --- | ---: |']
    for key, value in report['review_counts'].items():
        lines.append(f'| {key.replace("_", " ")} | {value} |')
    lines += ['', 'The five notification candidates are CSV records **10917, 17958, 50956, 52775, and 63357**. They cover delivery, account verification, and account debit. These are content-compatible examples, not independently authenticated legitimate messages.', '',
              'Three source-spam records (**463, 1278, 64348**) resemble routine OTP/payment/allotment notifications. Hold them for label-policy and provenance review. Do not flip their labels from wording alone.', '',
              'Six other source-spam records contain advertising or mixed service/promotion content. Such labels may be consistent with an unwanted-message policy even when the message is not a scam. Nine have suspicious threat/link/callback patterns, but that does not independently prove fraud.', '',
              'Ten ham matches are outside the notification scope, and one is truncated. Keyword-hit counts are therefore not usable-notification counts.', '',
              '## Recommendation', '',
              'Do not bulk-import this corpus to solve the notification false-positive gap. Keep these 34 records as review references. For future development, seek source/context evidence for the five notification candidates and resolve the three label-policy cases. Decide whether the product predicts unwanted spam or fraudulent/scam content before mixing labels across corpora. No corrected-label training set is produced by this review.', '',
              '## Method and limitations', '',
              report['sample_method'], '', report['encoding'], '',
              'This is an assistant content review of a targeted sample, not independent human annotation and not a statistical accuracy audit. The source CSV has only SMSes and Labels; individual sender, consent, and transaction context are absent. No model scores informed the review. The sample is development material and should not be presented as an independent test set.', '',
              'Raw messages and contact/account details are omitted from this report. The JSON companion retains record references and message hashes for local verification. Record numbers include the CSV header and are not physical line numbers.', '',
              f'Source SHA-256: `{EXPECTED_SHA}`.', '',
              'Source: [Super SMS repository](https://github.com/smspamresearch/spstudy). Attribution: Salman, Ikram, and Kaafar (2024), *Investigating Evasive Techniques in SMS Spam Filtering: A Comparative Analysis of Machine Learning Models*, IEEE Access. Dataset reuse terms remain to be clarified before redistribution.', '',
              '## Record-level review', '', '| CSV record | Original label | Outcome | Review reason |', '| ---: | --- | --- | --- |']
    for r in reviews:
        lines.append(f"| {r['csv_record_including_header']} | {r['source_label_name']} | {r['disposition'].replace('_', ' ')} | {r['reason']} |")
    (ROOT / 'reports/super-sms-notification-review.md').write_text('\n'.join(lines) + '\n')
    assert path.read_bytes() == raw
    assert len(reviews) == 34
    assert all(not r['approved_for_training'] and not r['authenticity_verified'] for r in reviews)
    print(json.dumps({'reviewed': len(reviews), 'outcomes': report['review_counts'], 'source_unchanged': True}, indent=2))


if __name__ == '__main__':
    main()
