# Labeling guide for the hand audit

You check one paper at a time against its task's data. Each paper comes as a folder named by a random code
(`paper_XX3/`) holding `paper.pdf`, `audit.xlsx` and `data/` (the task's raw result files). The packet does not say
which system wrote the paper, and it does not show the checker's verdicts, so neither can sway you.

Open the PDF next to `audit.xlsx`. Its first sheet, "Start here", gives the steps; the "Guide" sheet repeats the
definitions below. Fill in the yellow columns from the dropdowns. Budget about 90 minutes per paper.

The packets are built by `audit/make_packets.py` from an assignment file and read back by `audit/import_labels.py`,
which checks for blanks, computes agreement and scores the checker against the labels.

| Sheet | One row per | Your column |
|---|---|---|
| Numbers | number in the paper, except table cells the checker matched to the data, of which a random quarter is included | your verdict |
| Citations | sentence with a citation | supported |
| Claims | sentence stating a finding of the paper | within evidence |
| References | entry in the reference list | exists |
| Missed | (empty) a result number you saw in the paper that the Numbers sheet lacks | all columns |
| Data | quantity computed from the raw results, with its identity; filter it to look a number up | (read only) |

## Numbers

| Column | What to write |
|---|---|
| your verdict | `correct`: the number is right for what the sentence or table says it is. `wrong value`: the paper says what it is, and the value is wrong. `wrong identity`: the value is real, but belongs to another dataset, method, setting or statistic than the paper says (for example the digits result printed as the breast cancer one). `not checkable`: the data cannot settle it (a hyperparameter not in any file, a number from a cited paper). `not a result`: a year, a section number, an equation constant. |
| note | one line when you are unsure, or when the Data sheet is missing a quantity that the paper computes correctly (write "key gap: what it is") |

A number is `correct` if it matches the data at the precision printed (92.6% for 0.92593 is correct; 92.7% is not).
Derived numbers (differences, ratios, "a fifth") are correct if they follow from the data.

## Citations

| Column | What to write |
|---|---|
| supported | `yes`: the cited paper says or shows what the sentence attributes to it. `partly`: right topic, but the sentence overstates or misstates it. `no`: the cited paper does not say this, or is about something else. `cannot tell`: neither the abstract nor the paper (if you can open it) settles it. |
| note | which key is wrong when a sentence cites several papers, and why |

Read the cited paper's abstract first (the References sheet links a search for each title); open the full paper only when the abstract does not settle
it. Judge each sentence as written, not the paper's overall quality.

## Claims

| Column | What to write |
|---|---|
| within evidence | `yes`: the results support the sentence at the scope it states. `overreach`: true in part, but stated more broadly than the results allow (more datasets, settings or certainty than shown; "significant" without a test; a mechanism stated as shown when it was not measured). `no`: the results contradict it, or nothing in them bears on it. |
| note | the result that supports or contradicts it |

## References

| Column | What to write |
|---|---|
| exists | `yes`: the paper exists with these authors, title and year (one year off is fine for an arXiv version). `wrong details`: it exists, but the first author, title or year is wrong. `no`: you cannot find any such paper. `cannot tell`: you could not search (say why). |

## Agreement

In the pilot, each of you audits two papers alone (one from each system, on different tasks, though you are not
told which) and you both audit one more paper separately. Do not talk about the papers until both of you have sent
all your files. Disagreements are kept as they are for the agreement figure, then resolved together for the final
labels, in the `resolved` column of `disagreements_<code>.csv`.
