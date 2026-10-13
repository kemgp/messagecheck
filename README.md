# MessageCheck

An explainable SMS spam detection web application for an AI case study.

Status: React/JavaScript/Vite frontend and browser inference are implemented locally. Both models, explanations, and the validation comparison are connected. Production build and 782-case Python/JavaScript parity checks pass. Final test evaluation and public deployment are pending.

The external-data revision is now evaluated: 36 candidates were compared, but none was adopted after regression review. The leading candidate catches the hacking/payment diagnostic while incorrectly flagging the legitimate license reminder. Served models remain revision 2. See [the revision 3 experiment](docs/revision-v3.md) for data preparation, results, limitations, and reproduction commands. Expanded Python/JavaScript parity checks cover 3,418 cases per model.

## Datasets

| Dataset | Local data / coverage | Project use |
| --- | --- | --- |
| [UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection) | Original labeled spam/non-spam SMS corpus; cleaning and split details are documented below. | Trains the served revision 2 models and supplies the original validation and reserved test partitions. |
| [Mendeley SMS Phishing Dataset, version 1](https://data.mendeley.com/datasets/f45bkkt8pr/1) | `data/raw/Dataset_5971.csv`: 5,971 rows with ham, spam, and smishing labels. Source lists CC BY 4.0. | Audited and used in revision 3 experiments after overlap filtering. Most rows overlap with the original corpus. No resulting model was adopted. |
| [Fishing for Smishing — IMC 2025](https://github.com/reportsmishing/Smishing-Dataset-IMC25) | `data/raw/final_dataset_output.csv`: 33,869 rows across languages, including 22,078 labeled English. Source lists CC BY 4.0. | English scam reports were filtered, grouped, and used in revision 3 experiments. The supplied file has no explicit legitimate-message control class. No resulting model was adopted. |
| [Financial Scams Detection Dataset, version 1](https://data.mendeley.com/datasets/znsk27yk3h/1) | 523 rows: 310 scam and 213 ham. Source lists CC BY 4.0. A separate copy excludes 101 records containing Bengali script, leaving 422; this is not an English-language guarantee. | Inspected; ambiguous labels prevent bulk adoption. Original download preserved. Not used for training or model evaluation. |
| [Super SMS dataset](https://github.com/smspamresearch/spstudy) | `data/raw/super_sms_dataset.csv`: 67,010 rows, including two without labels. Encoding artifacts and dataset reuse terms remain unresolved. | A targeted 34-record notification review found five candidates needing context and three unresolved label-policy cases. No records approved for training. See [the review](reports/super-sms-notification-review.md). |

Preserve source attribution and original downloads. See [the external-data audit](docs/external-data.md) for overlap counts and [revision 3](docs/revision-v3.md) for the subsequent preparation, experiment, and non-adoption decision. Source labels and keyword coverage are not proof of message authenticity or real-world detection performance.

### Labeling and collection

The [labeling policy](docs/labeling-policy.md) defines spam as unsolicited advertising or scam attempts, and ham as supported legitimate communication, including expected notifications. Ambiguous examples stay out of new curated training and scored evaluation sets until resolved. Predictions do not authenticate a sender or link.

Use the [example review template](docs/example-review-template.md) to record provenance, source labels, recipient context, proposed labels, and duplicate/template checks. Financial Scams and Super SMS remain review sources rather than approved bulk training additions. The served models remain revision 2, and both final-test partitions remain unevaluated.

The [notification evidence queue](reports/notification-evidence-queue.md) contains eight previously reviewed leads with original labels and specific missing-context requirements. All eight remain on hold; recipient-confirmed examples have not yet been collected.

Current collection scope is existing local datasets only. Direct overlap checks found matches for one of the eight leads; unresolved context remains unknown, and original labels are preserved.

The [Super SMS candidate preparation](docs/super-sms-preparation.md) provides 59,615 source-labeled messages in 58,348 template groups after exclusions and deduplication. Existing-corpus overlaps, malformed/encoding-flagged groups, conflicting labels, and all previously reviewed cases are quarantined. A separate [controlled experiment](docs/super-sms-experiment.md) assigned these groups to partitions and evaluated eight candidates. None passed the adoption gates: all missed more original-validation spam and flagged the legitimate license reminder. Revision 2 remains served; all final tests remain unevaluated.

## Next steps

1. Collect and review supported legitimate notifications and spam examples using the policy and template. Start with receipts, OTPs, delivery updates, and account notices; keep unresolved source labels on hold.
2. Audit duplicates and related templates against existing data, protect reserved test groups, and preserve already inspected examples as development material. Document coverage and intended use before adding approved records to a dataset.
3. If suitable, prepare a controlled training mixture and compare revised models on development partitions. Track false alarms and missed spam separately, including the known hacking/payment and legitimate license diagnostics.
4. Adopt a candidate only when the measured tradeoff and diagnostic review support it; verify Python/JavaScript feature values, scores, labels, and explanations before changing app model imports and dashboard metrics.
5. Once model choices are frozen, evaluate the reserved final tests, update the results, verify the application on desktop/mobile, and complete deployment and the paper.

The policy, review template, candidate preparation, and initial Super SMS experiment are complete. The next development investigation is the license false alarm and additional original-validation misses. No new model has been adopted.

## Run the website

Use Node.js 24 and pnpm. From this project directory:

```sh
pnpm install --frozen-lockfile
pnpm dev
```

Open the Local URL printed by Vite. `pnpm build` creates the deployable `dist/` directory; `pnpm preview` serves the built application locally. No Python server, database, account, or API key is needed to use the website. The existing exported models are included in the frontend build.

For Vercel, use the Vite framework preset, build command `pnpm build`, and output directory `dist`. Publish only the built website, not raw datasets, Python artifacts, or evaluation fixtures.

## Verify JavaScript predictions

With the Python training environment active:

```sh
python scripts/make_parity_fixtures.py /tmp/messagecheck-parity.json
pnpm test:parity /tmp/messagecheck-parity.json
```

This checks all 774 validation examples and 8 edge cases against Python, including feature values, scores, labels, and explanation arithmetic. It does not load the final test set.

This is the selected replacement for FindIt. The previous project remains available as reference.

## Project scope

Users paste a message, receive a spam/non-spam prediction, inspect influential terms, and compare Multinomial Naive Bayes with logistic regression. An evaluation page shows measured held-out performance and methodology.

- AI concepts: Natural Language Processing and supervised Machine Learning.
- Training: Python and scikit-learn on a local computer.
- Interface: React, Vite, and JavaScript; responsive for desktop and phone browsers.
- Inference: exported TF-IDF settings and model parameters evaluated in the browser.
- Hosting: Vercel Hobby Free, subject to eligibility and usage limits.
- Database: unnecessary for the first version. No Supabase or Render dependency.
- Data: UCI SMS Spam Collection for served models; additional external sources and their experiment/pending status are listed in the dataset table above.

Read [the roadmap](docs/roadmap.md) for the implementation and research plan.

Read [the cleaning procedure](docs/data-cleaning.md) to reproduce data preparation with `python3 scripts/clean_data.py`.

Then follow [the splitting procedure](docs/data-splitting.md) with `python3 scripts/split_data.py`.

Follow [training and local prediction instructions](docs/training.md) to reproduce the models. See [preliminary validation results](reports/validation-summary.md); these are not final test results.

No paid APIs, paid hosting, custom-domain purchases, or trial-dependent services. Pasted messages should stay in the browser; do not add message-content analytics or remote logging.

## Proposed paper title

Development and Evaluation of an Explainable SMS Spam Detection Web Application Using Machine Learning

## References

- Datasets: https://archive.ics.uci.edu/dataset/228/sms+spam+collection
- https://github.com/reportsmishing/Smishing-Dataset-IMC25
- https://data.mendeley.com/datasets/f45bkkt8pr/1
- Text features: https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction
- Leakage prevention: https://scikit-learn.org/stable/common_pitfalls.html
- Vercel Free eligibility: https://vercel.com/docs/plans/hobby
