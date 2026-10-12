# MessageCheck

An explainable SMS spam detection web application for an AI case study.

Status: React/JavaScript/Vite frontend and browser inference are implemented locally. Both models, explanations, and the validation comparison are connected. Production build and 782-case Python/JavaScript parity checks pass. Final test evaluation and public deployment are pending.

The external-data revision is now evaluated: 36 candidates were compared, but none was adopted after regression review. The leading candidate catches the hacking/payment diagnostic while incorrectly flagging the legitimate license reminder. Served models remain revision 2. See [the revision 3 experiment](docs/revision-v3.md) for data preparation, results, limitations, and reproduction commands. Expanded Python/JavaScript parity checks cover 3,418 cases per model.

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
- Data: UCI SMS Spam Collection, with attribution and license retained.

Read [the roadmap](docs/roadmap.md) for the implementation and research plan.

Read [the cleaning procedure](docs/data-cleaning.md) to reproduce data preparation with `python3 scripts/clean_data.py`.

Then follow [the splitting procedure](docs/data-splitting.md) with `python3 scripts/split_data.py`.

Follow [training and local prediction instructions](docs/training.md) to reproduce the models. See [preliminary validation results](reports/validation-summary.md); these are not final test results.

No paid APIs, paid hosting, custom-domain purchases, or trial-dependent services. Pasted messages should stay in the browser; do not add message-content analytics or remote logging.

## Proposed paper title

Development and Evaluation of an Explainable SMS Spam Detection Web Application Using Machine Learning

## References

- Dataset: https://archive.ics.uci.edu/dataset/228/sms+spam+collection
- Text features: https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction
- Leakage prevention: https://scikit-learn.org/stable/common_pitfalls.html
- Vercel Free eligibility: https://vercel.com/docs/plans/hobby
