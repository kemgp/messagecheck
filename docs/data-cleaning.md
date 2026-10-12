# Data cleaning

Run `python3 scripts/clean_data.py` from the MessageCheck project folder. The script uses the Python standard library and needs no package installation.

Input: `data/raw/SMSSpamCollection`, retained unchanged with its original readme.

Outputs:

- `data/processed/messages.jsonl`: one JSON object per retained message, including its label, original text, stable ID, and all original source line numbers.
- `data/processed/cleaning-report.json`: raw checksum, class counts, removed-duplicate count, invalid rows, and conflicting-label groups.

The script validates tab-separated records, permits only `ham` or `spam`, and rejects empty messages. It compares lowercase text with repeated whitespace collapsed to detect duplicates. For same-label duplicates, it retains the first message's original text. Conflicting-label groups are excluded and reported for review rather than arbitrarily choosing a label.

It preserves punctuation, capitalization, numbers, URLs, and ordinary words in the retained text. Model tokenization and TF-IDF are separate steps; do not fit a vocabulary or IDF values before splitting the dataset.

This is conservative duplicate removal. Messages that differ in phone numbers, URLs, or other wording can still be near-duplicates. Check template grouping before splitting, and document any remaining leakage risk. Do not remove legitimate repetitions of words within a message or automatically delete difficult examples.
