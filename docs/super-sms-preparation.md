# Super SMS candidate preparation

The existing local dataset was prepared without training or changing served models. Source labels are retained (`0` = ham, `1` = spam); they are not independently verified. Dataset reuse terms remain unresolved, so this preparation does not authorize redistribution.

| Result | Count |
| --- | ---: |
| Original CSV rows | 67,010 |
| Excluded source rows | 6,269 |
| Additional normalized duplicates collapsed | 1,126 |
| Retained candidate messages | 59,615 |
| Ham candidates | 35,767 |
| Spam candidates | 23,848 |
| Retained template groups | 58,348 |

## Files and reproduction

Run `python3 scripts/prepare_super_sms.py` from the project root. This regenerates only the preparation outputs and report:

- `data/super-sms-prepared/candidates.jsonl`: retained text, original and mapped label, stable normalized-text ID, template group ID, and all contributing CSV record references and message hashes.
- `data/super-sms-prepared/group-audit.jsonl`: every source row's group, exclusion reasons, and candidate/excluded status. No raw text is copied into this audit.
- [Preparation report](../reports/super-sms-preparation.json): counts, method, limitations, and input/output checksums.

All candidates have `split: unassigned`. They are prepared for a future source-labeled experiment, not imported into current training. Future partitioning must assign whole `group_id` groups and record its protocol before model selection.

## Filtering and grouping

The source checksum must match the earlier review. The script uses lossless Latin-1 decoding for inspection, quarantining records with C1 control or replacement characters rather than guessing repairs. Other encoding artifacts may remain. It also flags missing/invalid labels, empty normalized text, and all 34 previously reviewed records. Holding every reviewed case is deliberately conservative, including the five notification leads.

Revision 3 normalization removes URLs, bracketed artifacts and numbers, then retains lowercase ASCII words. Identical normalized texts collapse to one candidate while preserving every source reference. Related texts form connected components under word-trigram set Jaccard similarity of at least 0.8. Texts shorter than three normalized words can match by normalized equality only. The earliest CSV record represents a retained normalized duplicate group.

The graph includes the entire original cleaned corpus, staged Mendeley/IMC candidates, Financial Scams, and user diagnostics as protected anchors. Both existing split manifests are checked for source-ID coverage. This protects reserved examples through their source corpora without opening final-test partition files or computing model predictions. It also excludes overlap with prior training/development data.

An entire connected component is excluded if it touches a protected anchor, contains a flagged row, or contains both source labels. Flagged rows remain in the graph so they cannot silently bridge retained groups. Protection applies transitively, not just to direct matches.

Exclusion counts by reason overlap and must not be summed: 5,532 source rows belong to protected-overlap groups, 765 to encoding-flagged groups, 44 to conflicting-label groups, 37 to previously reviewed groups, six to malformed-label groups, and five to empty-normalized groups. The unique excluded total is 6,269.

## Verification and limits

Preparation checks group connectivity, candidate-ID uniqueness, exclusion of reviewed/protected nodes, complete source-row accounting, and unchanged input hashes. A separate full-output check verified retained labels and message hashes against the CSV, normalized equivalence for every collapsed record, single-label groups, and one audit assignment for each of the 67,010 source rows.

These checks prevent leakage under the documented matching method; they do not guarantee detection of every paraphrase. Normalization can also merge distinct messages, so the conservative conflict/protection rule can discard useful data. No automatic language classification was performed; ASCII normalization is not evidence of English-language coverage. The subset retains the corpus's source-label and sampling limitations and has not established improved model performance.
