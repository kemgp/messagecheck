# MessageCheck one-week roadmap

## Objective

Build and evaluate a responsive SMS spam classifier using public labeled data and two lightweight machine-learning models. The deliverables are a runnable website, reproducible training/evaluation code, and a rubric-aligned IMRAD paper. This plan replaces the FindIt build plan and requires no physical objects or private-message collection.

## First-version features

1. Paste an English SMS message and classify it as spam or non-spam.
2. Compare Multinomial Naive Bayes and logistic regression on the same input.
3. Show terms contributing toward or against the spam decision.
4. Display a held-out evaluation dashboard with actual metrics and a confusion matrix.
5. Include an About page explaining data, models, limitations, and citations.

No accounts, message history, SMS permissions, automatic blocking, chatbot, screenshot OCR, or multilingual claims in the first version. The interface supports phones and desktops; benchmark on named devices rather than claiming universal performance.

## Architecture

Train locally using Python/scikit-learn. Export the vocabulary, IDF values, tokenizer settings, normalization, label ordering, thresholds, logistic-regression coefficients/intercept, and Naive Bayes feature log-probabilities/class priors to static JSON. React/Vite/JavaScript loads these files and runs predictions in the browser. Vercel Hobby hosts the static build. Supabase and Render are unnecessary.

Use matching preprocessing in Python and JavaScript. Start with a deliberately simple, documented tokenizer, word unigrams, standard TF-IDF, and L2 normalization. Export all parameters instead of recomputing training statistics in the browser. Preserve term positions for explanation highlighting.

## Day-by-day plan

| Day | Engineering work | Research work | Acceptance check |
| --- | --- | --- | --- |
| 1 | Obtain UCI data with attribution; validate records; prepare fixed splits; train initial baseline and both models | Define questions, scope, dataset description, and begin collecting 8 credible sources | Local script accepts an SMS and predicts; raw/clean counts and splits are documented |
| 2 | Evaluate small predefined parameter choices on validation data; export models; prove browser inference | Document TF-IDF, model assumptions, and selection rule | Python/JavaScript parity passes on validation examples and edge cases |
| 3 | Build responsive input/result UI, model comparison, and initial Vercel Free deployment | Draft Introduction and Methods | The hosted page runs actual local predictions without sending message content to a server |
| 4 | Add coefficient-based explanations, loading/errors, input limits, and evaluation-page structure | Review explanation validity and document version/device settings; freeze model choices | Highlighted contributions reproduce each model's decision score; final-test configuration is fixed |
| 5 | Run final held-out evaluation; export genuine metrics and predictions; populate dashboard | Create Results tables and representative success/failure screenshots | Test set was not used for tuning; metrics are reproducible and linked to the deployed model versions |
| 6 | Check mobile/desktop behavior and permission-free workflow; fix implementation defects | Write Discussion and Conclusion; finish APA references and appendices | Limitations and conclusions follow measured results; any scoring fixes trigger documented reevaluation |
| 7 | Final deployment verification, README, source package/repository, and backup video | Write abstract from actual findings; format and inspect final paper | A fresh setup works and the paper meets submission requirements |

## Research questions

1. How do TF-IDF with Multinomial Naive Bayes and TF-IDF with logistic regression compare on held-out SMS spam classification?
2. What false positives and false negatives occur, and what message characteristics accompany them?
3. What prediction latency and initial loading behavior does the browser implementation exhibit on the tested devices?
4. Which terms contribute to the models' decisions, including incorrect decisions?

## Dataset and leakage controls

- Retain the source URL, retrieval date, license/attribution, and raw-data checksum.
- Report actual loaded counts rather than copying an advertised row count.
- Check missing entries, label validity, exact duplicates, and conflicting duplicate labels. Apply and document a fixed cleaning policy.
- Group near-identical templates where feasible so they do not appear in different splits; otherwise disclose that limitation.
- Target 70% training, 15% validation, 15% final test, stratified by class where compatible with grouping. Record seed and exact split membership; grouped splits may not match percentages exactly.
- Fit vocabulary and IDF only on training data. Keep transformations in a scikit-learn Pipeline.
- Compare a majority-class baseline with the two trained classifiers.
- Select settings and any decision threshold on validation results, using a predeclared metric such as spam-class F1. Do not tune on the final test.
- For simplicity, keep the training-only fitted candidate after selection and evaluate that exact model on the test set; avoid silently retraining before export.
- Retain final predictions and settings. Any later model revision needs clearly labeled new evaluation rather than an unchanged performance claim.

## Metrics and explanations

Report spam precision, spam recall, spam F1, macro F1, accuracy, class support, and a confusion matrix for each method. Include majority-baseline results so class imbalance is visible. Record actual counts and do not invent target scores as results.

Measure warm end-to-end prediction latency separately from application/model download and first initialization. Identify devices, browsers, repetition count, and timing boundaries. Report median and p95 with sample count when appropriate.

For logistic regression, each term contribution is its TF-IDF value multiplied by its coefficient. Display contributions plus the intercept separately. For Naive Bayes, contributions to the spam-versus-non-spam log-score difference are TF-IDF values multiplied by the difference between the two class feature log-probabilities; show the prior difference separately. These explain mathematical score contributions, not causal reasons or human intent.

Do not present uncalibrated model probabilities as verified certainty. If an input has no vocabulary matches, communicate insufficient known terms rather than presenting an intercept-only prediction as strong evidence. In the final evaluation, still report the underlying classifier outputs for all valid test examples and separately disclose any interface abstentions.

## Meaningful verification

- Python and JavaScript must produce the same feature values within a stated numerical tolerance, matching decision scores and labels for both models.
- Include punctuation, repeated terms, case differences, URLs, unknown terms, empty input, and Unicode in development checks.
- On the final test, record parity discrepancies without tuning to improve test accuracy; fix implementation bugs and rerun transparently when necessary.
- Check that explanation contributions plus the intercept/prior reproduce the score.
- Confirm no pasted-message contents are transmitted through inference, analytics, or error logging.
- Verify that exported dashboard metrics correspond to the models being served.

## Rubric requirements

The supplied rubric requires 6–10 pages excluding title page and references, Tahoma 12 point, 1.5 spacing, 1-inch margins, APA 7, at least 8 credible references, and a 150–250-word abstract. Follow Introduction; Methods 2.1–2.7; Results 3.1–3.3; Discussion 4.1–4.5; Conclusion; References; Appendices. Include real screenshots and source/setup or repository evidence.

Grading: Introduction 10%, Methods 15%, Software 15%, Results 15%, Discussion 15%, Conclusion/Recommendations 10%, Organization/Writing/APA 10%, Originality/Depth 10%.

The document permits pretrained or existing techniques and expects independent application and analysis. This project trains its own lightweight classifiers on a credited public dataset. A model comparison, correct evaluation protocol, faithful explanations, and error analysis supply the original contribution. Confirm the exact topic under the instructor's alternative-topic provision if applicable.

Start the bibliography with verified primary research on SMS spam/text classification and the dataset's original paper, then add model, evaluation, and implementation documentation. Do not reuse the reference exemplar's wording, topic, results, or unverified bibliography entries.

## Limitations to acknowledge

The corpus is older and primarily English. The experiment does not establish detection of current scams, phishing, Filipino-language messages, or new domains. Spam/non-spam labels are not safe/unsafe labels. No automatic action is taken on messages. No training, data download, deployment, or evaluation has been completed at roadmap creation.
