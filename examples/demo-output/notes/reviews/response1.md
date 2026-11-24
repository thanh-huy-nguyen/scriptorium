# Response to the meta-review (round 1)

Build: 5 pages, main text 4, no undefined references. `scriptorium check` and `scriptorium lint` pass.

## Required changes

1. **One scoped claim about the gain over logistic regression.**
   - The abstract, intro paragraph 4, contribution 2 and the Sec. 4 opening now say the same thing. The gain is clear on digits at both rates. On breast cancer it is significant at the higher rate with a large spread and a partial recovery. At the lower rate it is not significant.
   - "In every noisy setting we ran", "all but one paired noisy run" and "five of six cells" are removed.
   - Sec. 4.2 states three of four noisy cells and gives the per-cell p-values and seed counts.

2. **Precision null.**
   - The "p vs 50%" column is dropped. Table 2 now has the realized flip rate (the precision a random drop would reach), the lift over it, and recall. New recipes: `noisy_pct_*_n20`, `lift_*`.
   - Sec. 4.1 says the lift is large at 20% and smaller at 40%, smallest on breast cancer at 40%.
   - The pooled 71% is gone from the abstract, intro and text. Teaser panel 2 now shows digits at 40% only, and the caption gives the flip rate.

3. **MLP demoted.**
   - It is called an untuned MLP reference throughout.
   - It is removed as an abstract headline and moved after the logistic regression comparison in contribution 2.
   - The Sec. 4.3 heading now reads "An untuned MLP reference is hurt more by noisy labels", and the text says it shows that this MLP overfits, not that filtering beats a trained network.
   - Setup describes the MLP (solver, standardization, never sees the filtered set).
   - Sec. 5 lists as not run: an MLP on the filtered set, a regularized or early-stopped MLP, and a tuned-C logistic regression.
   - The figure 1 and figure 2 captions are updated.

4. **Known filter, not a new method.**
   - The abstract, intro and contribution 1 now present an empirical check of the 1999 single-algorithm filter.
   - Sec. 5 states that no comparison with confident learning, a majority-vote variant or a noise-aware logistic regression was run, so the paper cannot say whether thresholds or per-class counts matter.

5. **Title, "Why" paragraph, Sec. 5.**
   - The title is now "Out-of-Fold Filtering of Symmetric Label Noise for a Linear Model: A Small Measurement Study".
   - The Sec. 3 paragraph is retitled "Why disagreement may mark a flipped label". It is limited to small, nearly linearly separable problems with symmetric noise, and it names class-dependent noise as the failure case.
   - Sec. 5 adds that no random-drop or oracle-drop control was run, so the effect of targeting cannot be separated from the effect of dropping samples.
   - "A simple first thing to try" is tied to small symmetric-noise problems.

6. **Statistics.**
   - Setup says the p-values come from 5 paired seeds and about a dozen uncorrected tests, so they are descriptive. It also describes the trend test in one sentence.
   - The Sec. 4.2 cross-reference is fixed: the breast cancer trend p-value (0.66) and the 20% p-value (0.12) are printed in the text.
   - The pooled win counts are replaced by a per-cell "Seeds" column in Table 2 (new recipes `nwin_lr_*`).

7. **Clean-label cost and recovered share.**
   - Sec. 4.4 gives the cost on both datasets and the value of one test sample (0.19 points on digits, 0.58 on breast cancer). The breast cancer cost is below one sample, and five seeds cannot show equivalence.
   - Recovered share is defined in the Table 2 caption and Sec. 4.2. The raw loss it divides by is a new column, and the text notes the share is unstable when the loss is small.
   - The orphan breast cancer sentence is merged into the clean-label paragraph.

8. **Setup details added.**
   - Argmax disagreement, uniform multiclass flips, standardization fit inside each fold, folds stratified on the noisy labels, MLP solver and scaling, and timing as wall-clock on an unrecorded machine.
   - The per-class breakdown of clean-label drops is listed as not done.

9. **Contribution 3, Scriptorium sentence, Sec. 5.**
   - Contribution 3 is now findings: cost below test resolution, fit time, and the unstable cell.
   - The pipeline sentence is removed from Sec. 3. The pipeline's reproducibility hook requires one visible sentence citing Scriptorium, so it is kept, rephrased, at the end of the setup section rather than deleted.
   - Sec. 5 is cut to the take-away plus limits not given elsewhere. The untested line about passing the dropped set to a reviewer is deleted.

## Optional changes

- **Noise labels and Fig. 1 line.** The dashed clean-accuracy line was already per dataset, and the caption now says so. Table 1 keeps its none/low/high headers. I did not replace the network icon in Fig. 1.
- **Space.** The paper fits in 4 pages of main text, so I kept both Fig. 2 and Table 1.
- **MLP seed.** The setup now says the MLP variance mixes data and initialization. Timing is marked indicative.
- **Source of the 9-point sd.** The text says the cause is unknown, since no recipe separates the two candidates.

## Not done (dismissed in the meta-review)

New datasets, class-dependent noise, cleanlab, a C sweep, random-drop and oracle-drop controls, and more seeds all need new runs. They are listed as limitations in Sec. 5.
