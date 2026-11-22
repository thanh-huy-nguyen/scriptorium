# Response to review0

No new experiments could be run, so points needing them are answered by narrowing claims or stating limits.

## Soundness
- [major] Weak baselines (no tuned C, MLP on filtered data): not runnable. Abstract and contributions now call the MLP comparison weak/secondary; Discussion says the MLP comparison is secondary and the tuned-C question is open; Sec 5.3 already states the data do not show filtering beats regularization.
- [minor] Untuned C and K, "no hyperparameters": abstract now says K and C were fixed and not tuned; Sec 3 says the filter is not setting-free, states that the out-of-fold models and refit both use C=1, and that sensitivity is untested. "No threshold" is reworded to "no confidence threshold". Sweep not run. Questions on different C for the OOF models, iteration: untested.
- [minor] Thin evidence: more seeds/datasets not possible. Headline 66% in abstract and contributions is now paired with the 4/5-seed result and the 4.4-point loss; Table 1 gains a paired-range column (existing recipes) so ranges sit next to means. Seed confounding is stated in the Protocol paragraph; no intervals added.
- [minor] Mechanism ablations (oracle, confidence threshold, per-class, Wilson, cleanlab): not runnable; remain in limitations. Sec 5.2 states per-class drop rates were not measured.
- [minor] Fig. 1 framing: caption narrowed to digits and 20% breast cancer. Per-panel clean reference line not redrawn (figure unchanged); the caption keeps both clean values.
- [minor] Breast cancer explanation: reworded to "consistent with", small-sample explanation added as untested alternative (Sec 5.1, 5.2).
- [minor] Symmetric noise only: title now says "symmetric label noise in logistic regression"; class-dependent noise not run.
- [question] Recovery reference: Sec 4 Metrics now states clean-label logistic regression per dataset, with the formula. Per-seed recovery with spread not added.
- Other questions (CV-chosen C, per-class drops, second pass, breast-cancer variance breakdown) need new runs; not answered.

## Clarity
- [major] Recovery defined in abstract (parenthetical, pointing to Sec 4) and intro contribution 2; the 66% is paired with the 4.4-point loss in the abstract. Table 1 now shows paired ranges.
- [major] Sec 4 split into Baselines, Protocol, Metrics, with the recovery formula in display; states C is shared between OOF models and refit, no early stopping for the MLP, and that all models standardize features. Solver left at scikit-learn default (stated).
- [minor] Contribution bullets reworded per setting (digits all seeds, bc 20% 4/5, bc 40% unclear).
- [minor] Table bolding now simply best mean per row; caption notes many differences are within one sd; paired column added.
- [minor] Fig 2 caption shortened, interpretation removed, "precision undefined with clean labels" added. Recall labels not added to the figure; recall is in the text.
- [minor] Sec 3 labelled intuition, not a derivation, with one sentence on why a linear model approximates the local majority.
- [minor] Sec 5.4 ending rephrased; 5.1 title shortened. Build reports 4 pages of main text.
- [minor] Title says logistic regression and symmetric noise; "no threshold" now says "no confidence threshold" with K and C noted.
