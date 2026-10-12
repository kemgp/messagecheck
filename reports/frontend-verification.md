# Frontend verification

- Stack: React, JavaScript JSX, Vite, and Tailwind CSS. No TypeScript application files.
- Production build: passed.
- Prediction parity: 782 validation/edge cases per model; zero label mismatches. Maximum score differences were approximately 2.49e-14 for Naive Bayes and 4.88e-15 for logistic regression, below the 1e-10 tolerance.
- TF-IDF feature values and explanation sums passed the same tolerance checks.
- Browser checks: promotional and everyday examples classify using both models; empty input produces a validation message; an unknown-word input reports insufficient known words.
- Layout visually inspected at the default desktop viewport and a 390px phone-width viewport. This is responsive-layout verification, not performance testing on an actual phone.
- Input changes clear prior predictions to prevent stale results.
- Source uses local inference and contains no message-storage, inference-request, or analytics integration.
- Metrics displayed are validation results; final test evaluation remains pending.
- Model parameters currently produce a roughly 1.1 MB uncompressed JavaScript bundle (approximately 310 KB gzip). Vite reports a bundle-size advisory; model loading can be split later if needed.
- Public Vercel deployment remains pending.

## External-data experiment verification

- Expanded parity passed on 3,418 original/external validation, diagnostic, and edge cases per model. Served models had zero label mismatches; maximum score errors were 4.27e-14 (Naive Bayes) and 4.56e-15 (logistic regression).
- The experimental v3 word-bigram logistic candidate also passed all 3,418 cases with maximum score error 5.33e-15. Feature values and explanation sums passed the 1e-10 tolerance.
- A separate 42-case Python/JavaScript comparison passed for v3 normalization, word unigrams/bigrams, and character 3–5-grams, including URL/redaction, repeated-word, empty, and Unicode edge cases.
- Dataset integrity checks passed for IDs, group partition separation, counts, input hashes, normalized overlap exclusions, provenance, and development-only hacking groups.
- Production build passed after inference support was added; the existing bundle-size advisory remains. No new browser visual inspection or device performance claim is made because this revision did not change the UI.
- Served model JSON files, original split files, and current dashboard metrics were verified unchanged against Git. The experimental candidate was not adopted because it regresses the user's legitimate license diagnostic. Neither final-test partition was evaluated.
- Reproduction and full comparison: `docs/revision-v3.md`.
