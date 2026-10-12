# External dataset intake

The supplied files are preserved unchanged in `data/raw/`. Run `python3 scripts/audit_external_data.py` to reproduce the audit and candidate staging. Input SHA-256 hashes, source URLs, label counts, and exclusion counts are recorded in `reports/external-data-audit.json`.

| Source | Input rows | Novel unique candidates | Candidate labels |
| --- | ---: | ---: | --- |
| Mendeley Dataset 5971 | 5,971 | 847 | 463 ham, 384 spam/smishing |
| IMC 2025 | 33,869 | 15,530 | Provisionally spam/scam; original English text only |

Mendeley has 5,025 lowercase/whitespace matches and another 98 template matches against the original cleaned corpus. These were excluded across all original partitions to protect the existing evaluation. IMC has 22,078 English-labeled rows; one lacks a usable scam category. Other languages and English translations of non-English originals were excluded from this English-only candidate set.

Combined staging contains 16,377 unique messages after collapsing 6,548 duplicate rows. Exact-text binary label conflicts were checked; none were found among the novel candidates. Each staged message retains its source record number, original category, and template group. These are candidate data, not approved training data or independently verified labels.

## Coverage and limitations

Two IMC candidates describe hacking a phone, copying private data, and demanding payment before a deadline. They closely resemble each other, so they provide roughly one threat template rather than two independent scenarios. This supports further development on the user's missed example, but does not demonstrate adequate coverage of extortion. No novel candidates contain the literal stems `blackmail` or `extort`; keyword absence does not establish category absence.

The additions are heavily skewed: 15,914 spam/scam candidates versus 463 legitimate candidates. IMC supplies no explicit ham control class in this file. Some scam reports, such as conversational opening messages, may be indistinguishable from legitimate messages without surrounding context. Their category mapping needs review before binary training.

Of the 15,530 unique IMC candidates, 12,786 contain uppercase angle-bracket placeholders such as `<URL>` and `<DATE_TIME>`. Learning these source-specific markers could inflate evaluation scores and fail on real pasted messages. Consistent preprocessing of both sources and browser inputs must be designed and verified before retraining.

The current template heuristic does not group every paraphrase or redaction variant. Strengthen campaign/template grouping before any new split, particularly for the two near-identical hacking messages. Retain the original final test as a legacy benchmark and reserve a separate grouped external test before candidate selection; do not treat a reused validation score as independent evidence.

## Next model-development step

Update: the preparation and 36-candidate comparison are complete. No candidate was adopted after diagnostic regression review. See [revision 3 results](revision-v3.md). The paragraph below records the original intake plan.

Review ambiguous external labels, normalize redaction/URL artifacts consistently, strengthen near-duplicate grouping, and select a controlled training mixture with legitimate payment/security examples. Compare word and character features on development partitions. Then verify Python/browser parity and measure false negatives and false positives before adopting a model. The current models and split files were not changed during intake, and the reported threat remains unresolved.

## Sources

- [Mendeley SMS Phishing Dataset, version 1](https://data.mendeley.com/datasets/f45bkkt8pr/1), DOI 10.17632/f45bkkt8pr.1; source lists CC BY 4.0.
- [Fishing for Smishing, IMC 2025 repository](https://github.com/reportsmishing/Smishing-Dataset-IMC25); source lists CC BY 4.0. Preserve attribution and consult the source license when redistributing derived data.
