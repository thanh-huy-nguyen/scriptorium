# Response to review round 0

The paper is now framed as a measurement of a known filter. It reports what the filter leaves in the training set,
words the borderline results as borderline and prints in the template's bold and italic. No experiment was added.
All new numbers come from recipes on `results/runs.jsonl`. The build gives 4 pages of main text, every tagged number
recomputes, lint raises no flag, figlint and citation checks pass, and the consistency pass has no errors (its
warnings are scope words such as "every", each checked against the seed means).

## Before submission, the authors should check

- The Scriptorium sentence and its reference stay, as the task and the area chair require. The reference names people
  in an anonymous submission and its title mentions AI agents, which conflicts with the project writing rule.
- The grouped column headers in Tables 1 and 2 were edited in the rendered `.tex` files, because `scriptorium table`
  has no column groups. Rendering the tables again removes the grouping; the JSON headers stay readable without it.
- `paper/figures/paired_gain.py` now draws nothing and could not be deleted here. It and its old PDF, PNG and layout
  file are unused and can be removed.
- Three references still print as preprints, and "Python" prints in lower case (details under optional change 7).

## Required changes (meta-review, in order)

1. **Measurement of a known filter.** Done. New title (the working title). Sec. 1, paragraph 2 is now the question the
   runs answer. The first contribution is the study. The italic claim is the measured finding. Sec. 2 states what
   Brodley and Friedl report in their abstract and then what this study reports, without claiming an omission on their
   side. Their noise level is written in words, since it is not a number from our data and related work carries no
   figures. "Needs no clean set or noise rate" stays as a property in Sec. 3.
2. **Residual noise and correct samples dropped.** Done. Table 1 now has settings as columns and adds the rows "Left in
   kept set" and "Correct dropped" (recipes `kept_noisy_share_*`, `correct_dropped_*`). Sec. 4.1 is rebuilt around
   them, states the random-removal expectation, says removal exceeds the flipped share, says the higher rate costs
   both missed flips and lost correct samples, and compares precision only with the flipped share. No accuracy gain is
   attributed to these quantities. Ledger entries `kept_set_cleaner` and `removal_exceeds_flipped` were added and
   `drop_quality_shifts_with_noise` was rewritten.
3. **Two overstated results.** Done. The mean stays below the clean-label reference in all four noisy settings
   (abstract, third contribution, Sec. 4.2, Sec. 5, Fig. 1 caption). Sec. 4.2 gives both lower-rate gaps as borderline.
   Breast cancer at the lower rate is counted among settings that win back much only in Sec. 4.2, where the same
   paragraph says its gain is not established and gives the per-seed range (`recovered_seed_min_breast_noise20`,
   `recovered_seed_max_breast_noise20`).
4. **Checkable statistics.** Done. "Established" is defined once in Sec. 4 (two-sided paired t-test, five percent
   level, no multiplicity correction), with the note that overlapping splits make p-values likely too low. The pairing
   sentence is plain. The three borderline p-values are printed. The one-half sentences are gone. All four gap
   verdicts are called tentative. The abstract and introduction say "not significantly", since they precede the
   definition.
5. **Scope of the control.** Done. Sec. 4 "Methods" names the only comparison that isolates filtering and says no other
   noise treatment was run. The abstract and third contribution say "logistic regression with the same settings". The
   non-attribution sentence sits next to the accuracy result. The limitations add the regularization confound, the
   untried stronger regularization and the restriction to tasks where clean-label logistic regression is very accurate.
6. **Template fonts.** Done in the `main.tex` preamble (TeX Gyre Termes, Heros and Cursor under an engine test).
   `cvpr.sty` and the margins are unchanged. The log has no undefined font shapes, and run-in heads, lead-ins, the
   italic claim and bold values were checked on the page. The abstract is italic because the template sets it so.
7. **Dataset facts and the weak case.** Done. Sec. 4 states the two task types, cites the diagnosis dataset and explains
   what symmetric noise means with two classes. No class counts are printed. Sec. 4.2 reports the association for the
   two least accurate seeds (kept-set shares in the text, flipped shares in the Table 1 caption), worded as an
   association over five seeds (ledger `breast_high_seed_association`).
8. **One accuracy figure.** Done. The paired-gain plot is Fig. 1(c), with a true zero, sd, seed dots and clean columns;
   the zero line is labeled logistic regression and a gray mark shows the clean-label reference in each noisy setting.
   The legend reads "Mislabeled in training set". Fig. 2 is removed, references and the outline are updated, the caption
   was rewritten around how to read each panel, and the render was checked.
9. **One finding per paragraph.** Done. Sec. 4.2 has one finding per paragraph. The comparisons with the clean-label
   gain are gone. Sec. 4 states the MLP question and its results paragraph has two sentences. The third contribution is
   shorter.

## Optional changes

1. Names and tables: done. Text uses "ours" or "the filter" and "logistic regression"; "Won back" is defined by a
   displayed ratio (Eq. 2); Table 2 groups columns by dataset.
2. Reproducibility details: done (test fraction, scikit-learn defaults, versions not recorded, iteration limit, shared
   split, nested flips, checked against `experiments/run.py`).
3. Clean-label cost by scale: done in Sec. 4.3 (per-seed range on digits; one seed and one test sample on breast
   cancer, with recipes). The MLP sentence there was cut; Table 2 and its caption still show that ours is not best on
   clean labels.
4. Abstract: done. Plainer opening, explicit list of what the filter does not use, "on average over seeds", MLP dropped.
5. Discussion wording: done, with less restatement.
6. Related work: done. The deep-network paragraph is shorter and the four nearest alternatives are cited within what
   was verified. The two book-chapter records print without a book title, as fetched.
7. Bibliography records: not changed. DBLP returned no data, Semantic Scholar and OpenAlex were rate-limited during
   the searches, Crossref returned no published record, and the one OpenAlex fetch that succeeded gave the same
   preprint. Protecting "Python" by hand fails `scriptorium cite verify`, so the edit was reverted. The missing accent
   in Frenay is also as fetched.
8. Fig. 1(a): done. Both pills read "Needs no ..." and the correctly labeled sample that is later dropped is marked.
9. Nadeau and Bengio test: not added. No verified record was at hand, and a second criterion would not fit the page
   limit. The text instead says the p-values are likely too low and treats the gap verdicts as tentative.

## Points the area chair dismissed (left as they are)

- Removing the Scriptorium sentence and reference: kept (see above).
- Printing the bootstrap intervals: not printed, since some disagree with the stated criterion.
- Equivalence with a confident learning variant: not claimed; the abstract does not support it.
- Adding Chen et al. and Natarajan et al.: not in the verified list.
- Motivating with linear probes: nothing of the kind was run.
- Calling clean-label drops "unflipped": notation fixes "correctly labeled", and Sec. 4 says existing errors are not
  counted.
- Linking the MLP result to the report on lower-capacity models: it does not explain this comparison.
- Per-class drops, convergence status and practitioner checks: not recorded, or untested.

## Soundness reviewer

- Tests never shown: required changes 3 and 4. The corrected test and intervals were not added (optional change 9).
- Only one comparator, regularization confound: required changes 2 and 5.
- Nothing beyond the antecedent: required change 1.
- Class numbers, nested noise, spread on breast cancer: required change 7 and optional change 2.
- Precision mixes quality with prevalence: required change 2.
- "Removal adapts to the labels": rewritten as growth with noise that exceeds the flipped share.
- Scale of the clean-label cost: optional change 3; "unflipped" was dismissed.
- Repeated content: required changes 8 and 9.
- Repeated caveats and long caption: required changes 8 and 9.
- Figure encodings: required change 8.
- Pipeline sentence: dismissed.
- Question, difference from Brodley and Friedl's filter: only their abstract was read, so the paper claims no
  procedural difference.
- Question, in-sample filtering: not run; named among the missing controls.
- Question, per-class removal: not recorded in the saved runs.
- Question, which verdicts are claims: "established" is now defined, with its optimism stated.
- Question, how K, C and the MLP settings were chosen: the repository does not say; Sec. 3 states that K and C were
  fixed without tuning and Sec. 4 calls the MLP untuned.

## Clarity reviewer

- Lost fonts: required change 6.
- Undefined "establish": required change 4.
- Digits missing from the gap sentence: required change 3.
- Chained comparisons: required change 9.
- Repeated results: required change 8.
- Question and novelty in the introduction: required change 1.
- Drifting names: optional change 1.
- Hard abstract: optional change 4.
- Long Fig. 1 caption: required change 8.
- Legend and ticks in Fig. 1(b): legend renamed; ticks extend further beyond the bars.
- First tile of Fig. 1(a): optional change 8.
- Zero line and axis label of the paired plot: required change 8.
- Table headers: optional change 1.
- Missing setup facts: required change 7 and optional change 2.
- Reason for the MLP: required change 9.
- Discussion sentences: optional change 5.
- Pipeline sentence: dismissed.
- Title: required change 1.
- References: optional change 7.
- Question, the threshold: the five percent level; the repository does not record when it was chosen.
- Question, the MLP: answered in Sec. 4 "Methods".
- Question, other linear classifiers: the new title makes no such claim.
- Question, a second figure: it was merged into Fig. 1(c).

## Significance reviewer

- Learning beyond the 1999 work: required change 1.
- Gap that does not hold: removed; required change 1.
- Residual noise absent: required change 2.
- When the finding transfers: required changes 5 and 7; linear probes were dismissed.
- No other noise treatment: stated in Sec. 4 and the limitations (required change 5); MLP shortened.
- Repeated results and truncated axis: required change 8.
- Caveats and the one-half test: required changes 4 and 9.
- Precision across rates: required change 2.
- Thin related work: optional changes 6 and 7.
- Pipeline sentence: dismissed.
- Question, their linear learner and zero noise: their abstract does not settle it, so no claim is made.
- Question, residual noise and seed order: Sec. 4.2 reports the association for the two weakest seeds only.
- Question, effect of a smaller training set: cannot be separated without controls; in the limitations.
- Question, stronger regularization: not run; in the limitations.
- Question, vision setting: none beyond the digits task was tested, and no claim is made.

## Experiments reviewer

- No controls: required changes 2 and 5; the limitations list what cannot be separated.
- Placement against prior work: required change 1.
- Kept-set noise and the weak case: required changes 2 and 7.
- Statistics: required changes 3 and 4.
- Correct samples discarded: required change 2.
- Classes and features: task types stated; counts have no recipe and are not printed.
- Duplicate displays and truncated axis: required change 8.
- Hard results prose: required change 9.
- MLP paragraph: required change 9.
- Scale of the clean-label cost: optional change 3.
- Pipeline sentence: dismissed.
- Reproducibility: optional change 2.
- Discussion, related work and bibliography: optional changes 5 to 7; extra citations and practitioner checks were
  dismissed.
- Question, confusion-matrix variant: not checked against the source; no equivalence claimed.
- Question, oracle filter: not run; in the limitations.
- Question, smaller C: not run; in the limitations.
- Question, per-class removal: not recorded.
- Question, why one half: the comparison was removed.
- Question, convergence: not recorded.
