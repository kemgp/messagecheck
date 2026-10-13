# Example review template

Copy the blank record below for each candidate and apply the [labeling policy](labeling-policy.md). Keep completed records and message text in a private local review location unless sharing is permitted and identifying details have been removed. This template is documentation, not a training-data importer.

Do not fill a missing fact with an assumption. Use `unknown` where evidence is unavailable. Default to `hold` and `unassigned`; neither a source label nor a completed form approves a message for training.

## Blank record

| Field | Value to complete |
| --- | --- |
| Review ID | |
| Policy version | 1 (2026-10-13) |
| Reviewer / review date | |
| Dataset or contribution source | |
| Local file and CSV record including header, or stable source ID | |
| Source-file SHA-256 / original-message SHA-256 | |
| Original source label and its documented meaning | |
| Permission or reuse basis for intended use | unknown |
| Private text reference or permitted, redacted text | |
| Redactions / encoding repairs applied | |
| Language and text-quality notes | |
| Message category | receipt / OTP / delivery / account notice / personal / promotion / scam attempt / other |
| Expected by recipient? Evidence? | unknown |
| Sender/transaction context and evidence reference | unknown |
| Evidence basis | recipient-confirmed / source-documented / explicit-content judgment / wording-only / unknown |
| Proposed label or disposition | ham / spam / uncertain / exclude |
| Reason, including what remains uncertain | |
| Second review / disagreement resolution, if needed | pending or not needed, with reason |
| Previously inspected or used as a model diagnostic? | unknown |
| Duplicate / related-template group ID | pending audit |
| Cross-dataset conflicts or protected-split overlap | pending audit |
| Intended role | development reference / training candidate / evaluation candidate |
| Assigned partition | unassigned |
| Approval status and reviewer | hold |

## Before marking a candidate approved

- The proposed label has a stated basis under the policy; uncertainty is resolved rather than hidden.
- The original label is preserved and any disagreement has a documented resolution.
- Text quality, provenance, privacy, and intended reuse have been reviewed.
- Duplicate/template checks are complete; protected evaluation groups are respected.
- The intended role reflects prior exposure. Previously inspected Super SMS examples and user diagnostics remain development material.

Approval makes a record eligible for a separately documented preparation step. It does not change the dataset, partition, or served model by itself. Keep a dated change history when a review decision changes.
