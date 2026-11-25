"""Extract every reported number, with the identity the paper gives it, and every sentence that states a finding.

A model reads the paper one section at a time and maps each number onto the task's vocabulary (datasets, methods,
conditions, metrics, statistics). It judges nothing: code matches the numbers against the answer key (match.py).
"""
from __future__ import annotations

import json
from pathlib import Path

from common import ask, pdf_chunks

FIELD = {"type": "string"}
SCHEMA = {
    "type": "object",
    "properties": {
        "numbers": {"type": "array", "items": {"type": "object", "properties": {
            "printed": {"type": "string", "description": "the number exactly as printed, with %, \\times10^{} etc."},
            "comparator": {"type": "string", "enum": ["=", "<", ">", "~"]},
            "context": {"type": "string", "description": "the sentence, or for a table the caption, row and column"},
            "where": {"type": "string", "enum": ["abstract", "prose", "table", "caption", "figure"]},
            "attributed_to": {"type": "string", "description": "the table or figure the sentence points to for "
                                                            "this number, as printed ('Table 2') or as its \\ref "
                                                            "label ('tab:main'); '' if none"},
            "kind": {"type": "string", "enum": ["result", "setup", "other"]},
            "dataset": FIELD, "method": FIELD, "versus": FIELD, "condition": FIELD, "metric": FIELD,
            "statistic": FIELD},
            "required": ["printed", "comparator", "context", "where", "attributed_to", "kind", "dataset", "method",
                         "versus", "condition", "metric", "statistic"]}},
        "claims": {"type": "array", "items": {"type": "object", "properties": {
            "sentence": {"type": "string"}, "type": {"type": "string", "enum": ["finding", "comparison", "mechanism",
                                                                                "generalization", "significance"]}},
            "required": ["sentence", "type"]}},
    },
    "required": ["numbers", "claims"],
}

PROMPT = """You annotate the numbers in one part of a research paper, given as the text of its compiled PDF
(two-column pages read column by column; table rows appear as lines of cells), for a faithfulness check.

The study behind the paper uses this vocabulary. Map every number onto it: use the vocabulary's key (e.g. "logreg",
"noise=0.2", "mean") when the paper's wording refers to it, "" when the paper does not say, and "other" when the paper
refers to something outside the vocabulary.

{vocab}

List EVERY number that reports a quantity of the study: results in sentences, tables (one entry per cell) and figure
captions; statistics (means, standard deviations, differences, p-values, effect sizes, counts of dropped or flipped
samples); and setup values (dataset sizes, seeds, folds, hyperparameters, noise rates). Do not list section, figure,
table, equation, page or reference numbers, years, or numbers inside citations, URLs or LaTeX lengths.

For each number give:
- printed: exactly as printed (keep %, signs, \\times10^{{-4}}, \\pm parts as separate numbers);
- comparator: "<" for "p < 0.001", ">" for "more than", "~" for "about", else "=";
- context: the sentence, or for a table cell "caption | row label | column label";
- where, attributed_to (only for a number in a sentence that points to a table or figure for it: "Table 2", or
  as printed, e.g. "Table 2");
- numbers written in words ("five seeds", "a fifth") count too: give them as printed;
- kind: "result" for outcomes of the study, "setup" for settings and dataset facts, "other" for anything else;
- dataset, method, versus (the method compared against, for differences and p-values), condition, metric,
  statistic, each mapped as described. A difference between two methods has statistic "mean difference"; a p-value
  names its test when the paper does ("p-value, paired t-test").

Also list every sentence that states a finding of this study (claims): what works, what beats what, why, how
general, or whether a difference is significant. Copy each sentence exactly.

The paper part:
<<<
{text}
>>>"""


def vocab_text(key: dict) -> str:
    v = key.get("vocabulary", {})
    out = []
    for field in ("dataset", "method", "condition"):
        for k, d in (v.get(field) or {}).items():
            out.append(f"{field} {k!r}: {d}")
    out.append("metric (use these names): " + "; ".join(v.get("metric") or []))
    out.append("statistic (use these names): " + "; ".join(v.get("statistic") or []))
    return "\n".join(out)


def extract(paper: Path, key: dict, cache: Path | None = None) -> dict:
    """{'numbers': [...], 'claims': [...], 'tokens': n}, cached in `cache` (a JSON file) when given."""
    if cache and cache.exists():
        return json.loads(cache.read_text())
    res = {"numbers": [], "claims": [], "tokens": 0}
    for i, part in enumerate(pdf_chunks(paper)):
        r = ask(PROMPT.format(vocab=vocab_text(key), text=part), SCHEMA)
        for n in r["data"].get("numbers", []):
            n["chunk"] = i
            res["numbers"].append(n)
        res["claims"] += r["data"].get("claims", [])
        res["tokens"] += r["tokens"]
    if cache:
        cache.write_text(json.dumps(res, indent=1))
    return res
