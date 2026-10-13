# Frontend verification

## Local checks for requested deployment verification — 2026-10-14

- Executed the browser inference module directly in Node against both built-in examples. Both served models classify the everyday example as ham and the promotional example as spam, with recognized terms and verified explanation sums.
- Verified served JSON model hashes against the final report and checked primary UCI counts and confusion matrices. The dashboard source imports the final report.
- Source inspection confirms that editing clears prior analysis and that empty/whitespace input triggers the validation error. These behaviors were not interactively exercised in this check.
- Hosted verification remains pending: no deployment URL was available in project files, and Computer Use was not approved to access Chrome. No hosted prediction, rendered timing, interaction, or visual result is claimed from these local checks.

## User-reported prediction-computation measurements — 2026-10-14

- App-displayed `ms local computation`, in trial order: **0.6, 0.7, 0.3, 0.2, 0.1, 0.2, 0.2, 0.3, 0.1, 0.2, 0.3, 0.2, 0.3, 0.1, 0.3, 0.2, 0.3, 0.2, 0.1, 0.2 ms**.
- Sample count: **20**. Median: **0.2 ms**. Mean: **0.26 ms**. p95: **0.6 ms**, using nearest rank (19th sorted observation). Range: **0.1–0.7 ms**.
- Environment carried forward from the user's same testing session: **MacBook Air M4; macOS Sequoia 15.7.7; Google Chrome 154.0.8037.98 (Official Build), arm64; localhost**.
- Timing boundary: the app's `performance.now()` interval around both models' `predict` calls. Includes vectorization, classification, and explanation computation; excludes initial loading and React result rendering. These are combined two-model computation timings, not separate model latency or end-to-end response latency.
- Values were manually transcribed from a display rounded to **0.1 ms**. Summary statistics describe these rounded observations, not higher-precision instrumentation. Twenty trials are a small descriptive sample; p95 is not a stable tail-performance guarantee.
- The user confirmed that the same message was used throughout all 20 trials. The exact message/length was not recorded. The user also confirmed completing one warm-up analysis before trial 1. These are user-reported warm computation measurements.
- No new network-throttling or cache settings were confirmed for this computation series. Earlier page-load settings are recorded separately. Hosted-site and other-device timings remain unmeasured.

## User-reported page-load measurements — 2026-10-14

- Browser Network **Load** times, in trial order: **389, 380, 327, 338, 335 ms**.
- Conditions reported by the user: **No throttling; cache disabled**. Five reload measurements.
- Median: **338 ms**. Mean: **353.8 ms**. Range: **327–389 ms**.
- These measure the browser load event, not prediction computation, rendered-result latency, or confirmed application readiness. No throttling does not specify the underlying connection speed.
- User-reported environment: **MacBook Air M4**, **macOS Sequoia 15.7.7**, **Google Chrome 154.0.8037.98 (Official Build), arm64**, running on **localhost**. Exact local URL/port was not supplied. These are local development measurements, not hosted-site performance or internet download timings.
- Five samples provide a small descriptive loading check, not a reliable tail-latency estimate. The computation measurements above are separate from this loading check.

## User-reported local privacy check — 2026-10-14

- The user supplied a Network-panel screenshot with **All** selected and no request rows visible after following the analysis-check instructions.
- The user then confirmed that predictions still worked after switching the browser's Network setting to **Offline**, without reloading the already loaded application.
- Recorded finding: **No new network requests were observed during analysis; predictions continued to work offline after initial loading.**
- This supports local inference in the tested session. It is user-reported verification, not an independently instrumented network capture. The screenshot alone does not establish recording status or the full observation interval.
- Browser/version, device/OS, exact app URL, and number of trials were not recorded. This does not establish deployed-site behavior or rule out delayed transmission. Repeat the Network check on the deployed site.
- This privacy check itself supplies no timing results; separately reported measurements are recorded above.

## Current status: final evaluation, 2026-10-14

Revision 2 is frozen and the dashboard now imports `reports/final-test-report.json`. Primary UCI results, confusion matrices, class supports, interface-notice counts, and separate supplemental results are displayed. Final-test parity passed 15,364 messages per model, with zero label mismatches and maximum score errors 4.80e-14 (NB) and 5.33e-15 (LR). Production build and server-rendered dashboard checks passed. No new browser visual inspection was possible because UI browser tools reported no available browsers. Named-device tests and deployment remain pending. See [final evaluation](../docs/final-evaluation.md).

The entries below are historical verification records from before the freeze.

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
