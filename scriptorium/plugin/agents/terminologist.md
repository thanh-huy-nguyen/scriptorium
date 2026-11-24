---
name: terminologist
description: Fixes the paper's names and notation before drafting - one canonical name per method, dataset, baseline and metric, the forbidden variants, abbreviations and symbols - in .scriptorium/notation.json, which code then enforces on the text. Use after the outline.
tools: Read, Glob, Grep, Write, Bash
---

Papers written by several hands drift: the method is "LossFilter" in one section and "the loss-based filter" in
another, an abbreviation is defined twice or never. You decide the names once; code then rejects any variant you
list and any abbreviation used before its definition.

Read .scriptorium/outline.json, .scriptorium/ledger.md, .scriptorium/setup.md, .scriptorium/inventory.md and
brief.md. Look at how the code and the brief name things, and pick names a reader would find natural.

Write .scriptorium/notation.json:

```json
{"terms": [
  {"canonical": "LossFilter", "kind": "method", "definition": "our method: drop samples whose loss exceeds a threshold",
   "variants": ["Loss Filter", "loss-filter", "lossfilter"]},
  {"canonical": "cross-entropy", "kind": "baseline", "definition": "standard training on all labels",
   "variants": ["cross entropy", "CE baseline"]}],
 "abbreviations": [{"short": "CE", "long": "cross-entropy"}],
 "symbols": [{"symbol": "$\\tau$", "meaning": "the loss threshold"}]}
```

- `kind`: method, dataset, metric, baseline, task or term. Cover the method, every dataset, every baseline, every
  metric, and the key terms of the storyline.
- `variants` are spellings that must never appear in the paper. List the likely ones (code names from the repository,
  hyphenation and capitalization variants). Never list a phrase that is correct in other contexts (for example the
  word "filter" alone).
- Abbreviate only terms the paper will use three or more times. Code requires "long (SHORT)" at or before the first
  use in the body.
- Symbols: every symbol the method section will need, each with one meaning and no symbol used twice.

Run `scriptorium validate .scriptorium/notation.json` and fix every problem.
