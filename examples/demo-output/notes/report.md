# Scriptorium report: A Linear Model's Out-of-Fold Disagreements Find the Flipped Labels: Filtering Label Noise Without a Clean Set or a Noise Rate

1 check(s) still fail; see below.

| Check | Result |
|---|---|
| Build | 5 pages, main text 4, 0 undefined refs, 0 overfull boxes |
| Numbers | 85 tagged numbers in the text, 169 recipes; all recompute |
| Citations | 15 entries, all fetched from bibliographic databases; 0 missing, 2 unused |
| Prose lint | 0 flag(s) |
| Review scores | review0: 4.25, review1: 4.25 |
| Agent sessions | 102 sessions, 1428 turns, 602,140 output tokens, 19,290,403 input tokens |

## Revision decisions

- revise1: kept: mean score 4.25 -> 4.25

## Open problems

- consistency: notation: table_main.tex: 'symmetric label noise' appears 1 time(s); the paper's name is 'symmetric noise' (fix it in .scriptorium/tables/main.json and rerun `scriptorium table main`)

## Storytelling notes

- 05_results.tex: paragraph 4 ("Breast cancer gives weaker evidence. At the higher rate the filter win...") prints 3 numbers; at most 2 per paragraph. Open with the insight, keep one headline number, move the rest to a table
- 05_results.tex: paragraph 6 ("With clean labels the filter loses a fraction of a point to logistic r...") prints 3 numbers; at most 2 per paragraph. Open with the insight, keep one headline number, move the rest to a table
