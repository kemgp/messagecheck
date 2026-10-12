# Error analysis and model revision

Original validation counts: Naive Bayes produced 1 false positive and 8 false negatives; logistic regression produced 1 false positive and 10 false negatives among 678 ham and 96 spam messages. A nonzero error count is expected; the original accuracy figure did not imply perfect detection.

Inspection identified short ambiguous text, obfuscated marketing, and dataset messages whose spam label may depend on sender/context absent from the text. Labels were not changed. Word-based text alone cannot verify sender identity, domain ownership, or whether a recipient consented to a message.

The user's parcel and license messages exposed a mismatch between the older SMS corpus and modern local examples. The supplied labels were retained as diagnostics, not silently added to training or counted as independent test successes.

## Adopted change

Keep Naive Bayes unchanged. Change logistic regression from equal class weighting to `ham: 1, spam: 2`, keeping the same training-only vocabulary, unigram TF-IDF, C=10, solver, seed, and splits. This modestly raises the cost of missing spam. The revised logistic model matches both supplied labels but both examples remain close to its decision boundary.

Validation logistic confusion matrix changes from [[677, 1], [10, 86]] to [[677, 1], [9, 87]], with rows=true and columns=predicted, ordered ham then spam. Spam F1 changes from 93.99% to 94.57%. This is a small observed improvement on reused validation data, not proof of better generalization to all modern messages.

A broader phrase-feature/fully-balanced candidate reached 6 validation misses and 1 false alarm, but wrongly flagged the user's expected non-spam license example. Its favorable aggregate score was insufficient reason to replace the model blindly.

## User interface

Raw predictions remain visible. Borderline scores and disagreement trigger review notices. No government-domain whitelist or hardcoded PHLPost/LTO outcome was added. Those notices do not erase errors or alter the displayed binary evaluation counts.

## Remaining work

### Extortion diagnostic (2026-10-12)

The user-supplied message “You have been hacked! Pay within 12 hours!” is an unresolved false negative in both served models. Browser inference gives Naive Bayes a score of -2.5116 and logistic regression -3.0755, with a spam cutoff of zero. Neither triggers the existing borderline notice. The word `hacked` is absent from both learned vocabularies; `pay` contributes toward non-spam in both models. Unigram features do not represent the combined threat and payment demand.

An exploratory cutoff lowered just enough to catch this message increases validation false positives from 1 to 23 for Naive Bayes and from 1 to 69 for logistic regression, while reducing false negatives to 4 and 2 respectively. No threshold change was adopted. Details are retained in `reports/extortion-diagnostic.json`, and the example is recorded in `data/diagnostics/user-examples.json` outside training and final testing.

Further model development needs representative labeled threat/payment messages and legitimate payment/security messages, with separate development and independent evaluation groups. Evaluate contextual features against these groups before adopting a replacement. A non-spam prediction must not be interpreted as evidence that a message is safe. This observed gap remains unresolved; recording the example does not improve model performance.

Naive Bayes still misses the parcel example. More representative, independently labeled modern SMS examples are needed to substantiate broader improvements. Keep future training examples separate from an independent evaluation set. Record diagnostic-driven model selection transparently in Methods and Discussion, and evaluate the frozen final model only once settings and browser behavior are finalized.
