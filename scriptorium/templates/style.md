# How this paper is written

Every agent that writes or reviews text follows this guide. Edit it to match your group's style; `scriptorium init`
copied it to `.scriptorium/style.md`, which is the copy the agents read.

## Storyline first

- Write around insights, not results. Each section moves the reader one step along one storyline: the problem, the
  key idea, why it works, and what it changes.
- Results paragraphs open with the insight, then point to the evidence ("Table 2", "Fig. 3"). Never a run of
  "X gets 0.81, Y gets 0.79, Z gets 0.77". The prose tells the story; tables and figures hold the numbers. Code
  counts the numbers in running text (tables, figures and captions do not count): at most two in the abstract, three
  in the introduction, none in related work, two per paragraph elsewhere (four in the setup).
- Frame findings as broadly as the evidence allows, and never beyond it. A claim the data does not support is
  narrowed or removed, not softened with hedges.
- Settings, hyperparameters and dataset details go in the setup and the tables, not in the story.

## Voice

- Plain, scientific American English. A first-year PhD student in the field should follow every sentence on first
  read. Short declarative sentences, one idea per paragraph.
- "We" for the authors, active voice by default.
- State claims directly. Save caveats for the limitations paragraph.
- No em dashes; use commas, parentheses, colons or a new sentence. No rhetorical questions, exclamation marks, hype,
  or emoji.
- Avoid: delve, dive into, leverage, harness, unlock, unleash, pivotal, crucial, paramount, seamless, robust (unless
  measured), cutting-edge, groundbreaking, revolutionize, transformative, holistic, synergy, landscape, realm,
  intricate, nuanced, multifaceted, meticulous, comprehensive (unless literal), underscore, showcase, highlight (as a
  verb for results), foster, bolster, navigate, embark, elevate, streamline, empower, paving the way, a testament to,
  "it is worth noting", "notably," and "importantly," as openers, "not only X but also Y".
- No summary sentence at the end of every paragraph that repeats the paragraph.

## Emphasis (as strong CVPR and NeurIPS papers use it)

- The contributions at the end of the introduction are a list; each item opens with a bold lead-in that names the
  contribution, then one sentence starting with a verb: `\item \textbf{A recompute check at the edit.} We ...`.
- Related-work paragraphs, and the parts of the method and experiments, open with a bold run-in head:
  `\paragraph{Learning with noisy labels.}`.
- The central claim is in italics once where it is stated, in the abstract or the introduction:
  `\emph{the corrected masks themselves carry the value}`. One to three italic phrases in the abstract and
  introduction together; italics also mark a term at its definition.
- No other bold in running text (at most two phrases per section). Best results in tables are bold.

## The framework figure

- One diagram shows the main idea of the paper, the way a reader should remember it: what goes in, what the method
  does, and the result that the abstract claims. It carries the contributions, so a reader who sees only this figure
  and its caption knows what the paper offers. The introduction refers to it where the idea is introduced. It can be
  Figure 1 (the teaser) or the method overview.

## Structure (methods paper)

1. Abstract, one paragraph: the problem and why current practice falls short; "We present X, a method for ..."; the
   key idea in one or two sentences; the breadth of the evaluation; the main insight. No lists of numbers.
2. Introduction: the task and why it matters to the people who do it; the gap; what we do; three contributions as a
   bulleted list, each one sentence starting with a verb. Reference Figure 1 early.
3. Related work: short paragraphs, each ending with one sentence on how this work differs.
4. Method: notation defined once; every equation introduced in words first.
5. Experiments: a compact setup, then results subsections whose headings state the finding.
6. Discussion and limitations: the big picture, then short limitations framed as future work.

## Numbers

- Every number that comes from data is printed with its recipe key right after it: `81.8\%\src{acc}`. Each number
  gets its own tag: `0.42\src{dice} $\pm$ 0.03\src{dice_sd}`.
- Choose the precision in the text; the checker rounds the recipe's value to the printed precision.
- Never use `\val{}`: it prints nothing in the PDF. Write the number in digits, followed by its `\src{key}`.
- Digits for measurements and counts, thousands separators, a space before units, the same decimals per column.
- Never type a number that has no recipe. If the paper needs a number that has none, add a recipe to
  paper/sources.py first (see the evidence rules), or leave the number out.

## Figures and tables

- Captions: the first sentence says what the figure shows; the rest says how to read it and what to notice. Full
  sentences. Say what error bars are (sd, 95% CI) and what n is.
- Tables: booktabs rules, no vertical lines, best result in bold, mean ± sd, decimals aligned. No empty cells,
  dashes or placeholders: when a value does not exist for a row, restructure the table (drop the column, move the
  quantity to its own small table or the text) so every cell holds a value.
- Figures: our method in the theme's accent colour (`[figures] theme`; see `scriptorium themes`), its partner colour
  for the strongest comparison, each other baseline in one muted colour used the same way in every figure, gray for
  references. High contrast, harmonized colours. Sans-serif labels, no titles inside the plot (the caption does that),
  legends off the data, axes labeled with units.
