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
