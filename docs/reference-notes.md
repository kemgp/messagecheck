# MessageCheck reference notes

Source shortlist checked 2026-10-15. These are bibliography and relevance notes, not a draft of the IMRAD paper. Metadata and relevance were checked against publisher, author, university, repository, or official documentation pages; this does not mean every source received a full-text critical review. Verify the exact passages supporting substantive claims when drafting. Eight references is a minimum, not a reason to omit dataset attribution or add unrelated citations.

## Original eight sources retained

1. Almeida, T. A., Gómez Hidalgo, J. M., & Yamakami, A. (2011). Contributions to the study of SMS spam filtering: New collection and results. In *Proceedings of the 11th ACM Symposium on Document Engineering* (pp. 259–262). ACM. [DOI](https://doi.org/10.1145/2034691.2034742). Publication details checked against the [author's publication record](https://www.servidores.ufscar.br/talmeida/publications/); publisher full text was not accessible through the browsing tool. Use for the original SMS collection and historical context, not current real-world prevalence.

2. Salman, M., Ikram, M., & Kaafar, M. A. (2024). Investigating evasive techniques in SMS spam filtering: A comparative analysis of machine learning models. *IEEE Access, 12*, 24306–24324. [DOI](https://doi.org/10.1109/ACCESS.2024.3364671). [University record and paper](https://researchers.mq.edu.au/en/publications/investigating-evasive-techniques-in-sms-spam-filtering-a-comparat/). Use for SMS robustness, evasion, and Super SMS provenance. Do not claim our experiments reproduced their evasion protocol.

3. Agarwal, S., Papasavva, A., Suarez-Tangil, G., & Vasek, M. (2025). Fishing for smishing: Understanding SMS phishing infrastructure and strategies by mining public user reports. In *Proceedings of the 2025 ACM on Internet Measurement Conference*. ACM. [DOI](https://doi.org/10.1145/3730567.3764431). [University manuscript record](https://discovery.ucl.ac.uk/id/eprint/10214522/). Authors/year/DOI checked; final page range still needs confirmation if available. Use for smishing collection methods and supplemental-data context.

4. Manning, C. D., Raghavan, P., & Schütze, H. (2008). *Introduction to information retrieval*. Cambridge University Press. [Author-hosted book](https://nlp.stanford.edu/IR-book/). Use Chapters 6 and 13 for TF-IDF and text classification/Naive Bayes. Match the paper's formula descriptions to our actual implementation.

5. Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830. [Published journal record](https://www.jmlr.org/papers/v12/pedregosa11a.html). Use for software attribution; exact current API settings should cite documentation separately. Author list follows the published journal record, not a differently versioned preprint.

6. Scikit-learn developers. (n.d.). *LogisticRegression*. Scikit-learn documentation. Retrieved October 15, 2026, from [official API documentation](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html). Use for solver, regularization, class weights, and coefficients. The stable URL changes over time; record the project's actual library version (1.9.1) with the experiment.

7. Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. *PLOS ONE, 10*(3), Article e0118432. [DOI and article](https://doi.org/10.1371/journal.pone.0118432). Use for class imbalance and precision/recall interpretation. We did not generate PR curves or PR-AUC; do not imply otherwise or claim universal superiority across every evaluation objective.

8. Cawley, G. C., & Talbot, N. L. C. (2010). On over-fitting in model selection and subsequent selection bias in performance evaluation. *Journal of Machine Learning Research, 11*, 2079–2107. [Journal article](https://www.jmlr.org/papers/v11/cawley10a.html). Use for repeated validation selection, selection bias, and the need to freeze choices before final scoring.

## Additional references

9. Delany, S. J., Buckley, M., & Greene, D. (2012). SMS spam filtering: Methods and data. *Expert Systems with Applications, 39*(10), 9899–9908. [DOI](https://doi.org/10.1016/j.eswa.2012.02.053). [University record with accessible-version link](https://researchprofiles.tudublin.ie/en/publications/sms-spam-filtering-methods-and-data-6/).

   Use in Introduction/Related Literature: reviews SMS filtering and difficulties with collecting and obtaining SMS data. This is historical context, not evidence about 2026 spam prevalence.

10. Wang, S., & Manning, C. D. (2012). Baselines and bigrams: Simple, good sentiment and topic classification. In *Proceedings of the 50th Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers)* (pp. 90–94). Association for Computational Linguistics. [ACL Anthology and full text](https://aclanthology.org/P12-2018/).

    Use in Methods/Discussion: motivates examining simple classifiers and feature choices. It studies sentiment/topic classification and NB/SVM variants, not MessageCheck's SMS task. Do not treat its findings as proof that bigrams must improve our models or describe our model as NBSVM.

11. Rudin, C. (2019). Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. *Nature Machine Intelligence, 1*, 206–215. [Publisher record](https://doi.org/10.1038/s42256-019-0048-x). [Author's accessible preprint](https://arxiv.org/abs/1811.10154).

    Use in Discussion: distinguish interpretable model structure from post-hoc approximation. This is a perspective on high-stakes decisions, not validation that our word highlights establish human understanding, causality, or safety. Our explanations are exact score contributions; no user-comprehension study was performed.

12. Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns, 4*(9), Article 100804. [DOI](https://doi.org/10.1016/j.patter.2023.100804). [University publication record](https://collaborate.princeton.edu/en/publications/leakage-and-the-reproducibility-crisis-in-machine-learning-based-/).

    Use in Methods/Limitations: motivates leakage controls and transparent reproducibility records. It does not prove that our heuristic template grouping eliminates every form of leakage. Use the published article rather than mixing numerical findings from different preprint versions.

## Direct dataset citations and artifacts

Keep these alongside the relevant research papers. Cite the dataset actually used and preserve its version, local filename, checksum, and project role. Use local audit counts in Methods rather than substituting advertised source counts.

| Dataset | Direct citation or artifact link | Project role |
| --- | --- | --- |
| UCI SMS Spam Collection | Almeida, T., & Hidalgo, J. (2011). *SMS Spam Collection* [Data set]. UCI Machine Learning Repository. [Dataset DOI](https://doi.org/10.24432/C5CC84); [repository record](https://archive.ics.uci.edu/dataset/228/sms+spam+collection). This follows UCI's supplied citation year, distinct from its displayed donation date. | Served revision 2 training, validation, and primary final test. Also cite Almeida et al. (2011), the associated paper. |
| Mendeley SMS phishing | Mishra, S., & Soni, D. (2022). *SMS phishing dataset for machine learning and pattern recognition* (Version 1) [Data set]. Mendeley Data. [Versioned DOI](https://doi.org/10.17632/f45bkkt8pr.1); [dataset page](https://data.mendeley.com/datasets/f45bkkt8pr/1). | `Dataset_5971.csv`; external experiments and combined supplemental evaluation after filtering. |
| IMC smishing | [Authors' dataset/code repository](https://github.com/reportsmishing/Smishing-Dataset-IMC25), including `dataset/final_dataset_output.csv`. Cite Agarwal et al. (2025) above as requested by its README, and retain this artifact link. | Filtered English records in external experiments and combined supplemental evaluation. |
| Super SMS | [Authors' repository](https://github.com/smspamresearch/spstudy); [specific CSV](https://github.com/smspamresearch/spstudy/blob/main/Data/super_sms_dataset.csv). Pair with Salman et al. (2024). Repository access date: October 15, 2026; downloaded-file checksum is recorded in our preparation report. | Grouped experimental candidates and supplemental final evaluation; never adopted into served training. Dataset reuse terms remain unresolved; the paper's license does not automatically license the dataset. |
| Financial Scams Detection | Ahmed, A. R., & Islam, G. F. (2025). *Financial scams detection dataset* (Version 1) [Data set]. Mendeley Data. [Versioned DOI](https://doi.org/10.17632/znsk27yk3h.1); [dataset page](https://data.mendeley.com/datasets/znsk27yk3h/1). Contributor names on the record: Al Rafi Ahmed and Gazi Faizul Islam. | Inspected and used as an exclusion anchor in preparation; not used to fit models or score model performance. Cite if describing the audit/rejection, not as training evidence. |

## Use in the eventual paper

Prioritize sources 1–3 and 9 for SMS-specific related work, 4–6 and 10 for methods, and 7–8 and 11–12 for interpretation and evaluation limits. Include direct dataset attribution wherever the data are described. Not every shortlisted source needs to appear if it supports no actual claim in the final paper.

Published studies' accuracy figures are not directly comparable to ours unless datasets, splits, labels, and evaluation protocols align. Do not copy the rubric sample's references or represent any of these publications as evidence for our own measured results. Our result claims must cite the project's frozen evaluation artifacts.
