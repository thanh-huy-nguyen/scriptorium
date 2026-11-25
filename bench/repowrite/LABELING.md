# Labeling guide for the hand audit

You check one paper at a time against its task's data. Every paper comes with three sheets in its `score/` folder,
made by `check/report.py`. You do not need to know which system wrote the paper, and the sheets do not say.

Open the paper's PDF, the task's result files (`repo/results/` or `repo/experimental_log.md`) and the sheet side by
side. Write your answer in the empty columns; leave the others as they are. Budget about 90 minutes per paper.

## numbers.csv

One row per number the checker could not confirm, plus a random tenth of the ones it did confirm.

| Column | What to write |
|---|---|
| `human_verdict` | `correct`: the number is right for what the sentence or table says it is. `wrong value`: the paper says what it is, and the value is wrong. `wrong identity`: the value is real, but belongs to another dataset, method, setting or statistic than the paper says (for example the digits result printed as the breast cancer one). `not checkable`: the data cannot settle it (a hyperparameter not in any file, a number from a cited paper). `not a result`: a year, a section number, an equation constant. |
| `human_note` | one line when you are unsure, or when the checker's key is missing a quantity that the paper computes correctly (write "key gap: what it is") |

A number is `correct` if it matches the data at the precision printed (92.6% for 0.92593 is correct; 92.7% is not).
Derived numbers (differences, ratios, "a fifth") are correct if they follow from the data.

## citations.csv

One row per sentence with a citation.

| Column | What to write |
|---|---|
| `supported` | `yes`: the cited paper says or shows what the sentence attributes to it. `partly`: right topic, but the sentence overstates or misstates it. `no`: the cited paper does not say this, or is about something else. `cannot tell`: neither the abstract nor the paper (if you can open it) settles it. |
| `note` | which key is wrong when a sentence cites several papers, and why |

Read the cited paper's abstract first (search its title); open the full paper only when the abstract does not settle
it. Judge each sentence as written, not the paper's overall quality.

## claims.csv

One row per sentence that states a finding of the paper.

| Column | What to write |
|---|---|
| `within_evidence` | `yes`: the results support the sentence at the scope it states. `overreach`: true in part, but stated more broadly than the results allow (more datasets, settings or certainty than shown; "significant" without a test; a mechanism stated as shown when it was not measured). `no`: the results contradict it, or nothing in them bears on it. |
| `note` | the result that supports or contradicts it |

## Agreement

In the pilot, each of you audits two papers alone, and you both audit one more paper separately, without talking
about it until both are done. Compare after; disagreements are kept as they are for the agreement figure, then
resolved together for the final labels.
