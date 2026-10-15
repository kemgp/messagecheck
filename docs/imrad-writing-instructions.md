# MessageCheck IMRAD paper writing instructions

Prepared October 15, 2026. This is a guide for writing the paper, not the paper itself. It combines the instructor's required format, a project-specific content plan, verified findings, evidence links, and the complete retained reference table.

## 1. Authority and scope

Follow the supplied `AI_Case_Study_IMRAD_Outline_Sample_Rubric.docx`, particularly Section I (requirements), Section III (required outline), and Section V (grading rubric). Section IV, **Sample Case Study**, demonstrates structure and depth only. Do not copy or paraphrase its prose, reuse its rice-disease topic, or transfer its results, citations, participants, or procedures into this study.

The instructor requirements below are distinct from the recommended MessageCheck content. The suggested research questions, table plan, and writing order are recommendations for this project, not additional instructor mandates.

Write about **MessageCheck's frozen revision 2**, a browser application comparing TF-IDF-based Naive Bayes and logistic regression for English SMS spam classification. Separate the deployed-in-code models from experimental candidates that were not adopted. Treat spam/ham classification as the task; do not redefine it as verified scam/safe classification.

The available technical evidence is sufficient to draft the case study. Final screenshots, author details, citation checks, and submission packaging still require preparation. Do not invent missing evidence or run more training merely to make the paper appear stronger.

## 2. Instructor requirements

| Item | Requirement |
| --- | --- |
| Length | 6–10 pages, excluding the title page and references. The instructions do not explicitly exclude appendices from the count; do not assume they are excluded. |
| Typography and layout | Tahoma, 12 pt; 1.5 line spacing; 1-inch margins. |
| Citation style | APA 7th edition. |
| Sources | At least eight credible references: journal articles, conference papers, official documentation, or reputable technical sources. |
| Structure | Title page; abstract; Introduction; Methods; Results; Discussion; Conclusion; References; Appendices. Preserve the required Methods, Results, and Discussion subsections below. |
| Abstract | One paragraph, 150–250 words. |
| Software | A working prototype, application, or simulation demonstrating the AI technique and producing observable output. Production readiness is not required. |
| Software submission | Source code with README/setup instructions, or a hosted repository/demo link; submit the software/source code as a zipped folder or repository link with the paper. |
| Demonstration evidence | Screenshots, sample output, or demo evidence in Results and/or Appendices. The required appendix specifically includes screenshots of the software in use and code excerpts or a repository link. |
| Final paper format | One Word or PDF document, with the software submission. |

The sample's survey, participant count, field trials, and mobile deployment are not requirements for MessageCheck. Do not add a user study unless one was actually conducted. A public deployment is not necessary when a working, documented repository/source submission satisfies the assignment.

## 3. Writing and evidence rules

1. Use original, precise academic prose. Explain technical terms at first use and use consistent names for the models and datasets.
2. Use past tense for completed procedures and observed results; distinguish planned work from completed work.
3. Cite external claims near the sentence they support. Read the relevant supporting passages before citing detailed findings; a verified title or abstract is not a substitute for checking the claim.
4. Attribute project measurements to project reports, not to outside studies. Use the final evaluation for final performance; older validation reports document development only.
5. Report sample sizes, class balances, metric definitions, and evaluation conditions alongside results. Present accuracy with spam precision, recall, F1, false positives, and false negatives.
6. Keep Results factual. Put explanations, comparisons, implications, and limitations in Discussion.
7. Distinguish automated checks, source inspection, user-reported observations, and direct interactive tests. Do not describe one as another.
8. Use numbered tables and figures with descriptive titles/captions, defined abbreviations, and references from the prose. Do not use screenshots as substitutes for readable results tables.
9. Do not claim statistical superiority, calibrated confidence, comprehensive privacy/security validation, verified scam detection, or general mobile performance without supporting evidence.
10. Final test sets have been consumed. Do not tune models, thresholds, or preprocessing on their results. Any future model study needs a separately documented evaluation design.

## 4. Content required in each paper section

### Title page

Include a descriptive title, student name(s), course and section, instructor's name, and submission date. Confirm personal and course details before final export. The supplied document identifies ITPD 6 — Artificial Intelligence 1 and instructor Arnold M. Narte.

Suggested working title: **Development and Evaluation of MessageCheck: A Browser-Based SMS Spam Classifier Using Naive Bayes and Logistic Regression**. This is a proposed title, not a finalized title page.

### Abstract

Write this last, as one paragraph of 150–250 words. Cover the problem, purpose, two algorithms and TF-IDF representation, prototype, evaluation design, key primary and supplemental findings, and a restrained conclusion. Identify the primary test size and acknowledge weak cross-source recall. Do not present 98.06% accuracy alone as the study's takeaway. Do not add unmeasured usability benefits, fraud reduction, or deployment claims.

### I. Introduction

Include all six elements in the instructor's outline:

- **Background:** Explain SMS spam and smishing, their distinction, and the motivation for a lightweight text-classification prototype. Use R1, R2, R3, and R9 as relevant. Do not invent current Philippine prevalence or financial-loss statistics.
- **Problem/research questions:** State answerable questions tied to recorded evidence. Suggested questions: How do frozen Naive Bayes and logistic regression perform on the primary UCI holdout? How does performance change on separately reported supplemental sources? Can the browser implementation reproduce Python inference and support local computation in the documented test conditions?
- **Objectives:** Develop the prototype; compare both models against an always-ham baseline; evaluate cross-source performance; verify export/inference parity; describe observed local computation and application behavior.
- **Significance:** Explain the educational and practical value of transparent local text classification and documented evaluation. Describe possible benefits as potential benefits, not measured reductions in fraud.
- **Scope and limitations:** English SMS text, binary source labels, frozen revision 2, public datasets, and a browser prototype. Briefly flag data age, source shift, false negatives, and limited device testing; develop these in Discussion.
- **Related literature/systems:** Synthesize SMS filtering research, TF-IDF and simple text models, robustness, evaluation leakage, and interpretability. Organize by concepts rather than summarizing one source per paragraph without connecting them to this study.

### II. Methods

#### 2.1 Research Design

Describe a developmental and evaluative case study with a comparative model evaluation. Explain that development experiments preceded the freeze, with the primary and supplemental evaluation roles recorded before final scoring. Do not characterize the work as a randomized trial, survey study, or production field experiment.

#### 2.2 System/Subject of the Study

Describe MessageCheck, its text input, two independent model outputs, term contributions, review/insufficient-word notices, and evaluation dashboard. Identify frozen revision 2 as the evaluated system. A compact pipeline diagram may show dataset preparation → training/validation → model freeze/export → browser inference → evaluation, with final tests separated from training.

#### 2.3 AI Techniques Used

Explain TF-IDF word unigrams, multinomial Naive Bayes, and logistic regression at a level suitable for the course. Justify these as simple, efficient text-classification methods with inspectable feature contributions. Explain the always-ham baseline and why class imbalance makes it necessary.

Read the actual training code and model metadata before specifying tokenization, vocabulary settings, smoothing, solver, regularization, class weighting, or thresholds. Use [training notes](training.md), [revision records](../reports/model-revision.json), and the frozen artifacts to reconcile the final configuration. Do not attribute an experimental bigram configuration to the served unigram models. Cite R4–R6 where applicable.

Explain that output scores are decision scores, not calibrated probabilities. Term highlights are additive learned contributions, not causal explanations. Explain how unknown vocabulary and borderline notices behave, including that all underlying binary predictions remain in evaluation.

#### 2.4 Data Collection and Materials

Provide a dataset provenance table with source, original/retained counts where relevant, label mapping, cleaning/exclusion rules, split role, and citation. Verify counts against preparation reports rather than treating original download counts as evaluation counts.

- UCI supplied served training, validation, and the primary test; training contains 3,612 messages, validation 774, and final test 773.
- Mendeley SMS phishing and filtered English IMC records supported external experiments and the combined supplemental evaluation. Explain how source labels map to spam/ham and the limitations of that mapping.
- Super SMS supported grouped experimental candidates and a separate supplemental evaluation; it was not adopted into served training.
- Financial Scams Detection was inspected and used as an exclusion anchor, not for model fitting or scored performance. Mention it when explaining the audit/exclusion process, with D5.
- Describe duplicate/template grouping, protected-corpus exclusions, ambiguous-label review, encoding handling, and relevant language filtering according to the recorded procedures. Do not claim exhaustive removal of semantic duplicates or perfect labels.

List software and versions from the reports and dependency records: Python/scikit-learn for training and export; React, JavaScript JSX, Vite, and Tailwind CSS for the application. Record the measured device/browser environment separately from the training environment. Do not call the application TypeScript-based.

#### 2.5 Procedure

Describe the reproducible sequence, supported by linked project records:

1. Obtain and record source datasets and provenance.
2. Audit labels, duplicates, encoding, and language; prepare partitions and protect held-out groups.
3. Train baseline models and select/refine using training and development evidence.
4. Run controlled external-data experiments; document development gains and regressions and the decision not to adopt candidates.
5. Freeze revision 2 on October 14, 2026, recording model, inference, and dataset hashes.
6. Score the predesignated primary and supplemental holdouts without fitting or tuning on their results.
7. Export model parameters and verify Python/JavaScript parity, including features, scores, labels, and explanation sums.
8. Document prototype checks, user-reported local timings, and local offline/network observations with their scope.

Explain rejected experiments briefly in the main text, with details in an appendix if needed. A negative adoption result is a valid finding. Do not erase regressions or imply the final models incorporated every downloaded dataset.

#### 2.6 Evaluation Metrics

Define spam as the positive class: TP = detected spam, TN = correctly classified ham, FP = ham flagged as spam, FN = missed spam. Define accuracy, precision, recall, F1, and macro F1; include formulas if space permits. State the zero-division convention used for the always-ham baseline. Label confusion-matrix axes and class order.

Describe primary versus supplemental evaluation separately. Do not pool different datasets into one overall accuracy or compare percentages without their class supports. No PR-AUC, ROC-AUC, significance test, confidence interval, or user-satisfaction score should appear as a measured result unless separately computed and documented.

For timing, specify sample size, warm-up, repeated-message condition, display rounding, timing boundary, and device. Separate browser Load event time from combined local model computation and end-to-end rendering. State that the computation samples are user-reported and exclude page loading and React result rendering.

#### 2.7 Software/Application/Simulation Description

Describe the user flow: paste text, analyze, inspect both predictions and term contributions, and consult the evaluation information. Explain browser-local inference using exported parameters. State the 5,000-character input limit if discussing input constraints.

Include screenshots and the source repository link: <https://github.com/kemgp/messagecheck>. Confirm repository accessibility and setup instructions before submission. Provide a hosted-demo link only if one has actually been deployed and verified. Explain how to install, build, and run using the repository's documented commands; do not promise training reproduction without the required local data/model artifacts and provenance instructions.

### III. Results

#### 3.1 Presentation of Findings

Present sample counts and the primary results table below. Include labeled confusion matrices and the baseline. Put supplemental results in a distinct table. Include a concise development-experiment outcome table only if needed to answer the stated objectives; label every result as validation/development or final test.

#### 3.2 Performance Summary

Report classification results, parity outcomes, and local timings with their conditions. State both the strengths and observed errors without explaining causes here. Round percentages consistently to two decimal places; preserve integer error counts and sample sizes.

#### 3.3 Software/Application Output

Include current screenshots showing the working input/results interface, both models, explanations, and evaluation dashboard. Select benign demonstration text without personal information. Capture an ordinary ham example and a spam example; include an unknown-vocabulary or known failure example if it helps explain limits. Label diagnostic examples as demonstrations, not independently sampled accuracy evidence.

Use captions stating the input/example type and what the screenshot demonstrates. Put the required screenshots and repository link in the appendices even if selected screenshots also appear in Results. Do not rely on an outdated preview that shows validation-only metrics.

### IV. Discussion

#### 4.1 Interpretation of Results

Answer the research questions directly. Explain that strong UCI performance coexists with substantially lower supplemental recall. Discuss class imbalance, source differences, label provenance, old training data, and lexical features as possible contributors; do not claim an untested factor caused the gap. The two primary F1 scores are close and do not establish statistical superiority.

Explain why experiments with improved external development recall were rejected when they introduced unacceptable regressions. Distinguish an unsuccessful candidate-adoption decision from an unsuccessful study.

#### 4.2 Comparison with Related Systems/Literature

Compare findings and methods with verified passages in R1, R2, R3, R9, and other relevant sources. Do not rank published accuracy values as if datasets, class balances, splits, and evaluation protocols were identical. R10 concerns sentiment/topic classification, so use it to motivate feature comparisons, not as direct evidence that bigrams must improve SMS results. R11 supports an interpretability discussion, not a claim that users understood our explanations.

#### 4.3 Implications

Discuss the usefulness of a local educational prototype and the importance of disclosing missed spam and false alarms. A non-spam prediction does not establish safety. Neither model verifies senders, destination websites, or payment requests. Discuss browser-local processing based on the implementation and limited recorded checks, without claiming a comprehensive privacy audit.

#### 4.4 Limitations of the Study

Use [limitations.md](limitations.md) as the detailed source. Cover older English training data; noisy/source-dependent labels; residual duplicate/paraphrase risks; cross-source recall; lack of Filipino/code-switched evaluation; vocabulary and contextual limitations; uncalibrated scores; heuristic notices; limited timing samples and devices; qualitative phone feedback only; and lack of a formal user study or comprehensive accessibility/security assessment.

State that automated overlap audits processed source texts before final scoring, while held-out predictions were not used for selection. Do not equate automated grouping with proof of no leakage. Explain that final holdouts are now consumed and cannot support future performance-driven tuning followed by an independent-test claim.

#### 4.5 Recommendations for Future Work

Give specific recommendations connected to evidence: better verified and diverse labels; reviewed expected-notification examples; evaluation of current English and multilingual/code-switched messages; new protected evaluation data for future models; robustness testing; broader device/browser/accessibility checks; and fuller deployment/network checks if deployed later. Note unresolved Super SMS reuse terms before redistribution. Keep these as future work, not completed procedures.

### V. Conclusion

Briefly restate the problem, approach, and supported takeaway: the prototype implements and reproduces two text classifiers with strong in-corpus results but limited cross-source generalization. Mention the key limitation and a concrete next research step. Do not repeat the abstract verbatim, introduce new results, or claim readiness for autonomous scam protection.

### References

Use at least eight credible works actually cited in the text. The full planning table appears below. Retain direct citations to datasets used or substantively discussed in Methods; pair artifact links with associated papers when indicated. Do not treat repository links as additional independent research studies or pad the bibliography with uncited items.

Convert the chosen entries into an alphabetized APA 7 References section with hanging indents. The planning table is not the final bibliography layout. Match every in-text citation to an entry and every entry to actual use. Confirm unresolved metadata and inspect supporting passages before finalization.

### Appendices

Include required screenshots and code excerpts or repository link. Recommended additions, as space permits: setup/reproduction instructions, dataset audit/split summary, experiment/adoption summary, confusion matrices if omitted from the body, and detailed verification conditions. Avoid raw personal messages, active OTPs, unrestricted dataset redistribution, or large unneeded code listings. Keep full machine-readable reports in the repository and cite their paths.

## 5. Verified findings to carry into the paper

Use [final-evaluation.md](final-evaluation.md) and [final-test-report.json](../reports/final-test-report.json) as the authoritative final results. Reconcile any future edits against those records.

### Primary UCI holdout

773 messages: 677 ham and 96 spam. Metrics below express F1 and macro F1 as percentages.

| Model | Accuracy | Spam precision | Spam recall | Spam F1 | Macro F1 | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Naive Bayes | 98.06% | 100.00% | 84.38% | 91.53% | 95.21% | 0 | 15 |
| Logistic regression | 98.06% | 98.80% | 85.42% | 91.62% | 95.26% | 1 | 14 |
| Always ham | 87.58% | 0.00% | 0.00% | 0.00% | 46.69% | 0 | 96 |

Confusion matrices have actual rows and predicted columns in `[ham, spam]` order: NB `[[677, 0], [15, 81]]`; LR `[[676, 1], [14, 82]]`. Zero observed NB false positives is sample-specific, not a guarantee.

### Supplemental holdouts

| Dataset | Ham | Spam | Model | Spam recall | Spam F1 | FP | FN |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| Mendeley / IMC | 90 | 2,750 | Naive Bayes | 29.89% | 46.02% | 0 | 1,928 |
| Mendeley / IMC | 90 | 2,750 | Logistic regression | 21.96% | 36.02% | 0 | 2,146 |
| Super SMS | 7,051 | 4,700 | Naive Bayes | 33.94% | 50.53% | 18 | 3,105 |
| Super SMS | 7,051 | 4,700 | Logistic regression | 28.11% | 43.69% | 26 | 3,379 |

These are separate source-based evaluations, not real-world field trials or verified scam-authenticity tests.

### Implementation and local observations

| Finding | Recorded evidence | Reporting boundary |
| --- | --- | --- |
| Python/JavaScript parity | 15,364 held-out messages per model; zero label mismatches; maximum score errors 4.80e-14 NB and 5.33e-15 LR, below 1e-10 tolerance. | Confirms implementation agreement, not classification correctness. |
| Combined model computation | 20 trials, same message, one confirmed warm-up; median 0.2 ms, mean 0.26 ms, nearest-rank p95 0.6 ms, range 0.1–0.7 ms. | User-reported display values rounded to 0.1 ms; includes vectorization/classification/explanations, excludes initial loading and React rendering; exact message/length unrecorded. |
| Page loading | Five localhost browser Load times: 389, 380, 327, 338, 335 ms; median 338 ms, mean 353.8 ms. | Cache disabled, no throttling; browser Load event, not hosted performance or application readiness. |
| Timing environment | MacBook Air M4, macOS Sequoia 15.7.7, Chrome 154.0.8037.98 (Official Build, arm64), localhost. | One device/browser; retain as user-reported environment. |
| Network/offline check | User reported no new requests during analysis and working predictions offline after initial page load. | Limited local observation; no fresh offline-load or comprehensive security claim. |
| Phone feedback | User reported that it worked acceptably on a phone. | Qualitative only; model, browser, cases, and timings unrecorded. |
| Known diagnostic failure | “You have been hacked! Pay within 12 hours!” remains a false negative for both served models. | Development diagnostic, not independent final-test evidence. |

Source: [frontend verification](../reports/frontend-verification.md). Some earlier entries in that file describe historical pre-freeze status; use dated, applicable records and do not repeat superseded statements as current facts.

## 6. Evidence map for the writer

| Paper content | Project evidence |
| --- | --- |
| Setup and application scope | [README](../README.md), [roadmap](roadmap.md), `src/App.jsx`, `src/inference.js` |
| Original cleaning and partitions | [Data cleaning](data-cleaning.md), [data splitting](data-splitting.md) |
| Training and revision history | [Training](training.md), [revision report](../reports/model-revision.json), [error analysis](error-analysis.md) |
| External dataset audit and experiments | [External data](external-data.md), [revision v3](revision-v3.md) |
| Super SMS preparation and candidate decisions | [Preparation](super-sms-preparation.md), [experiment](super-sms-experiment.md), [comparison](super-sms-comparison.md) |
| Label interpretation | [Labeling policy](labeling-policy.md) |
| Frozen model identity and final metrics | [Freeze record](../reports/final-model-freeze.json), [final report](../reports/final-test-report.json), [evaluation narrative](final-evaluation.md) |
| Device, timing, parity, and behavior checks | [Frontend verification](../reports/frontend-verification.md) |
| Limitations | [Limitations](limitations.md) |
| Literature metadata and detailed cautions | [Reference notes](reference-notes.md), [standalone reference table](reference-table.md) |

## 7. Rubric alignment

| Criterion | Weight | What the paper/submission should demonstrate |
| --- | ---: | --- |
| Introduction | 10% | Clear problem, justified scope, measurable objectives, and synthesized relevant literature. |
| Methods | 15% | Appropriate algorithms and enough detail to reproduce data preparation, model selection, freeze, and evaluation. |
| Software/Application/Simulation Development | 15% | Working relevant prototype, observable outputs, organized source and usable setup instructions. |
| Results | 15% | Objective, labeled tables/figures and software evidence tied to stated metrics. |
| Discussion | 15% | Supported interpretation, meaningful literature comparison, implications, and candid limitations. |
| Conclusion & Recommendations | 10% | Concise supported takeaway and specific future work. |
| Organization, Writing & APA Citation | 10% | Required IMRAD structure, professional prose, correct consistent APA citations. |
| Originality & Depth of Analysis | 10% | Independent analysis of model behavior, rejected experiments, generalization, and evidence boundaries. |

## 8. Writing order and submission checklist

Recommended order: reconcile Methods against artifacts → assemble Results tables and screenshots → write Discussion → write Introduction → write Conclusion → write Abstract → finalize title page and APA references → check layout and submission package.

- [ ] Confirm student names, course section, date, and final title.
- [ ] Preserve the required section/subsection structure and formatting.
- [ ] Verify all counts, percentages, confusion matrices, and model identities against the final report.
- [ ] Distinguish validation experiments, final tests, and diagnostic demonstrations throughout.
- [ ] Include supplemental results and limitations prominently, not only in an appendix.
- [ ] Capture current screenshots of the frozen-model interface and dashboard; caption them and include required appendix evidence.
- [ ] Cite at least eight credible sources actually used, with direct dataset attribution where applicable.
- [ ] Resolve metadata questions in the reference table and check the passages supporting each literature claim.
- [ ] Confirm repository access, README commands, and a fresh setup/build or clearly document any reproduction dependencies still missing.
- [ ] Do not claim a hosted demo exists unless deployment has been verified.
- [ ] Remove placeholders and instructional text from the eventual paper; retain this guide separately.
- [ ] Verify page count, font, spacing, margins, tables, captions, and APA formatting in the final Word/PDF.
- [ ] Submit the single paper document and required software/repository material.

## 9. Full reference planning table

The following retains all 12 literature/documentation sources and five dataset/artifact records from [reference-table.md](reference-table.md). These are shortlisted sources and intended uses; the paper has not yet been drafted. Inclusion here does not mean every source must appear in the final bibliography. Direct citations should be retained for datasets actually used or substantively discussed.

### Literature and technical documentation

| ID | Reference and direct links | Source type | Intended paper section | Purpose |
| --- | --- | --- | --- | --- |
| R1 | Almeida, T. A., Gómez Hidalgo, J. M., & Yamakami, A. (2011). Contributions to the study of SMS spam filtering: New collection and results. In *Proceedings of the 11th ACM Symposium on Document Engineering* (pp. 259–262). ACM. [DOI](https://doi.org/10.1145/2034691.2034742). | Conference paper | Introduction; Methods | Original SMS collection and historical spam-filtering research. |
| R2 | Salman, M., Ikram, M., & Kaafar, M. A. (2024). Investigating evasive techniques in SMS spam filtering: A comparative analysis of machine learning models. *IEEE Access, 12*, 24306–24324. [DOI](https://doi.org/10.1109/ACCESS.2024.3364671). [University record and paper](https://researchers.mq.edu.au/en/publications/investigating-evasive-techniques-in-sms-spam-filtering-a-comparat/). | Journal article | Introduction; Discussion | SMS robustness and evasion; associated Super SMS research. |
| R3 | Agarwal, S., Papasavva, A., Suarez-Tangil, G., & Vasek, M. (2025). Fishing for smishing: Understanding SMS phishing infrastructure and strategies by mining public user reports. In *Proceedings of the 2025 ACM on Internet Measurement Conference*. ACM. [DOI](https://doi.org/10.1145/3730567.3764431). [University manuscript record](https://discovery.ucl.ac.uk/id/eprint/10214522/). | Conference paper | Introduction; Methods; Discussion | Smishing reports, infrastructure, and IMC dataset provenance. |
| R4 | Manning, C. D., Raghavan, P., & Schütze, H. (2008). *Introduction to information retrieval*. Cambridge University Press. [Author-hosted book](https://nlp.stanford.edu/IR-book/). Use Chapters 6 and 13 for TF-IDF and text classification/Naive Bayes. Match the paper's formula descriptions to our actual implementation. | Academic textbook | Methods | TF-IDF and Naive Bayes; Chapters 6 and 13. |
| R5 | Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830. [Published journal record](https://www.jmlr.org/papers/v12/pedregosa11a.html). | Journal article | Methods; Software description | Attribution for the Python machine-learning library. |
| R6 | Scikit-learn developers. (n.d.). *LogisticRegression*. Scikit-learn documentation. Retrieved October 15, 2026, from [official API documentation](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html). | Official documentation | Methods | Logistic-regression solver, regularization, class weights, and coefficients. |
| R7 | Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. *PLOS ONE, 10*(3), Article e0118432. [DOI and article](https://doi.org/10.1371/journal.pone.0118432). | Journal article | Methods; Discussion | Precision/recall interpretation under class imbalance; no claim that we computed PR-AUC. |
| R8 | Cawley, G. C., & Talbot, N. L. C. (2010). On over-fitting in model selection and subsequent selection bias in performance evaluation. *Journal of Machine Learning Research, 11*, 2079–2107. [Journal article](https://www.jmlr.org/papers/v11/cawley10a.html). | Journal article | Methods; Limitations | Validation-selection bias and freezing choices before final testing. |
| R9 | Delany, S. J., Buckley, M., & Greene, D. (2012). SMS spam filtering: Methods and data. *Expert Systems with Applications, 39*(10), 9899–9908. [DOI](https://doi.org/10.1016/j.eswa.2012.02.053). [University record with accessible-version link](https://researchprofiles.tudublin.ie/en/publications/sms-spam-filtering-methods-and-data-6/). | Journal review article | Introduction; Related literature | SMS filtering methods and dataset-collection challenges. |
| R10 | Wang, S., & Manning, C. D. (2012). Baselines and bigrams: Simple, good sentiment and topic classification. In *Proceedings of the 50th Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers)* (pp. 90–94). Association for Computational Linguistics. [ACL Anthology and full text](https://aclanthology.org/P12-2018/). | Conference paper | Methods; Discussion | Feature choices and simple text baselines; different tasks from SMS filtering. |
| R11 | Rudin, C. (2019). Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. *Nature Machine Intelligence, 1*, 206–215. [Publisher record](https://doi.org/10.1038/s42256-019-0048-x). [Author's accessible preprint](https://arxiv.org/abs/1811.10154). | Perspective article | Discussion | Interpretability; explanations do not establish safety, causality, or user understanding. |
| R12 | Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns, 4*(9), Article 100804. [DOI](https://doi.org/10.1016/j.patter.2023.100804). [University publication record](https://collaborate.princeton.edu/en/publications/leakage-and-the-reproducibility-crisis-in-machine-learning-based-/). | Journal article | Methods; Limitations | Leakage risks and reproducibility; not proof that our grouping removes all leakage. |

### Direct dataset and artifact citations

| ID | Dataset | Citation and direct links | Actual project use |
| --- | --- | --- | --- |
| D1 | UCI SMS Spam Collection | Almeida, T., & Hidalgo, J. (2011). *SMS Spam Collection* [Data set]. UCI Machine Learning Repository. [Dataset DOI](https://doi.org/10.24432/C5CC84); [repository record](https://archive.ics.uci.edu/dataset/228/sms+spam+collection). This follows UCI's supplied citation year, distinct from its displayed donation date. | Served revision 2 training, validation, and primary final test. Also cite Almeida et al. (2011), the associated paper. |
| D2 | Mendeley SMS phishing | Mishra, S., & Soni, D. (2022). *SMS phishing dataset for machine learning and pattern recognition* (Version 1) [Data set]. Mendeley Data. [Versioned DOI](https://doi.org/10.17632/f45bkkt8pr.1); [dataset page](https://data.mendeley.com/datasets/f45bkkt8pr/1). | `Dataset_5971.csv`; external experiments and combined supplemental evaluation after filtering. |
| D3 | IMC smishing | [Authors' dataset/code repository](https://github.com/reportsmishing/Smishing-Dataset-IMC25), including `dataset/final_dataset_output.csv`. Cite Agarwal et al. (2025) above as requested by its README, and retain this artifact link. | Filtered English records in external experiments and combined supplemental evaluation. |
| D4 | Super SMS | [Authors' repository](https://github.com/smspamresearch/spstudy); [specific CSV](https://github.com/smspamresearch/spstudy/blob/main/Data/super_sms_dataset.csv). Pair with Salman et al. (2024). Repository access date: October 15, 2026; downloaded-file checksum is recorded in our preparation report. | Grouped experimental candidates and supplemental final evaluation; never adopted into served training. Dataset reuse terms remain unresolved; the paper's license does not automatically license the dataset. |
| D5 | Financial Scams Detection | Ahmed, A. R., & Islam, G. F. (2025). *Financial scams detection dataset* (Version 1) [Data set]. Mendeley Data. [Versioned DOI](https://doi.org/10.17632/znsk27yk3h.1); [dataset page](https://data.mendeley.com/datasets/znsk27yk3h/1). Contributor names on the record: Al Rafi Ahmed and Gazi Faizul Islam. | Inspected and used as an exclusion anchor in preparation; not used to fit models or score model performance. Cite if describing the audit/rejection, not as training evidence. |

### Citation status and boundaries

- R3: authors, year, title, and DOI are recorded; the final proceedings page range still needs confirmation if available. Do not invent it.
- R6: the stable documentation URL can change. The access date and the project's scikit-learn version (1.9.1) should accompany its use.
- D3 and D4 retain direct artifact links and their associated paper citations. No separate dataset publication year or DOI has been invented.
- D5 was inspected and used as an exclusion anchor, not as model training or scored evaluation data.
- Publication metadata and relevance were checked in the source search. Before drafting detailed claims, review the supporting passages; not every entry has undergone a complete full-text critical review.
- The table is a planning aid. The final APA 7 References section should be alphabetized, include only cited works, and use hanging indents rather than this table layout.
- Project measurements must be supported by the [final evaluation](final-evaluation.md) and [verification records](../reports/frontend-verification.md), not attributed to outside studies.
