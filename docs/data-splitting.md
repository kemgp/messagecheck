# Dataset splitting

Run `python3 scripts/split_data.py` from the project root after cleaning. Uses only Python's standard library.

The script groups similar templates before partitioning. Its fixed, label-independent template key lowercases text, replaces explicit URLs and emails with placeholders, replaces digit runs, and ignores punctuation between word tokens. Original text and labels remain unchanged. All messages sharing a key stay in one partition, including mixed-label groups.

This conservative heuristic prevents some common forms of duplicate leakage. It can group unrelated short messages and does not detect all near-duplicates or paraphrases. Report those limitations rather than asserting that all semantic leakage has been eliminated.

A deterministic allocation with seed 42 targets 70% training, 15% validation, and 15% test. Groups are assigned whole while approximately preserving class proportions. Exact percentages are secondary to keeping groups intact.

Outputs in `data/splits`:

- `train.jsonl`: model fitting, including vocabulary and IDF fitting.
- `validation.jsonl`: parameter selection and browser/Python prediction checks.
- `test.jsonl`: reserved for final evaluation after settings are frozen.
- `manifest.jsonl`: stable message IDs, template group IDs, and partition membership.
- `split-report.json`: source and output checksums, counts, seed, grouping policy, limitations, and overlap checks.

Do not browse final test messages for model design, tune on their predictions, or regenerate splits to obtain a better score. Aggregate labels/counts are used only to balance and audit the partitions. TF-IDF must be fitted on training text only.
