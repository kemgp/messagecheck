# Training and validation

From the project directory, create a virtual environment and install the pinned dependencies:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/train_models.py
python scripts/revise_model.py
python scripts/predict.py
```

The training script reads only train.jsonl and validation.jsonl. It never loads test.jsonl. Run the cleaning and splitting scripts first if reproducing from the original corpus; retain the recorded split policy and seed.

Every candidate uses lowercase ASCII letter/digit word tokens, word unigrams, raw term counts, smoothed IDF, and L2 normalization. Vocabulary and IDF are learned only from the training messages. Unicode scripts beyond ASCII are not represented by this tokenizer; this is a scope limitation, not evidence of multilingual performance.

The predefined search compares Multinomial Naive Bayes alpha values 0.1, 0.5, and 1.0, and logistic regression C values 1.0, 3.0, and 10.0. Logistic regression uses liblinear, seed 42, and up to 2,000 iterations. Candidates retain the default classifier decision rule with no threshold search. Pick the highest validation spam F1 in each family, breaking ties by spam precision, recall, and earlier candidate order. Do not change this candidate grid in response to final-test results.

The original selected candidates remain fitted on training data alone. The revision script then applies the documented moderate class-weight update below. Save both families for comparison; validation ranking provides only a provisional preferred model. Validation metrics have been used for selection and are not unbiased final-test estimates.

## Revision 2

A user reported modern parcel-fee and license-renewal examples. Original models missed the parcel example. A broader training-group cross-validation experiment evaluated phrase features and balanced class weighting. Its logistic winner reduced validation misses to 6 but incorrectly flagged the supplied license example. That candidate was not adopted.

Moderate weighting (`ham: 1`, `spam: 2`) with the existing unigram representation was evaluated next and adopted. It improves logistic training-group CV spam F1 from about 0.9271 to 0.9330, reduces validation misses from 10 to 9, leaves validation false alarms at 1, and matches both supplied expected labels. Its validation F1 is 0.9457. This choice reflects the diagnostic tradeoff; it is not the highest-F1 candidate from the broad experiment. Naive Bayes remains unchanged.

The two user-supplied messages are development diagnostics, not training rows or independent test evidence. Their labels do not verify actual sender/domain authenticity. The final test remains unread by all training and revision scripts.

Original artifacts are retained under `models/baseline-v1`. `scripts/revise_model.py` reproduces the adopted pipeline and updates the current report/export. `scripts/compare_improvements.py` reproduces the broader experiment; its report should be interpreted relative to the baseline artifact version used for that run.

The interface displays notices when models disagree or a score is within 0.5 of the zero cutoff. This is an explicitly uncalibrated display heuristic, not a changed classifier threshold. All binary outputs, including errors on borderline cases, remain in reported metrics.

Artifacts:

- `models/*.joblib`: local Python pipelines. Load only locally produced trusted files.
- `models/*.json`: exported vectorizer and classifier parameters for future JavaScript inference.
- `reports/validation-report.json`: all candidate metrics, confusion matrices, selection rules, versions, and source/model checksums.
- `reports/*-validation-predictions.jsonl`: per-message validation predictions keyed by stable IDs, with true labels and normalized log probabilities.
- `reports/validation-summary.md`: readable preliminary comparison.

The baseline always predicts the majority training class. Report precision/recall/F1 alongside accuracy because the classes are imbalanced. Confusion matrix rows are true labels and columns are predicted labels, ordered ham then spam.

Next implementation gate: browser feature values, scores, labels, and explanation contributions must match the exported Python models on validation examples and development edge cases. Model files alone do not constitute a tested browser implementation. Keep final-test evaluation for the frozen application/model configuration.
