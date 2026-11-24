"""Clarity measured, not guessed: a quiz from the claim ledger, answered from the compiled paper alone.

1. A quiz writer (no access to the paper) writes 15 questions with short answers from the ledger and the recipes:
   what the method takes as input, which baseline is strongest where, at what setting a gain vanishes.
2. A reader answers them from the PDF text only. A control answers them with no paper at all.
3. A grader marks each answer right or wrong against the key.

Only questions the control gets wrong count: the rest can be answered from priors and say nothing about the paper.
Each discriminative question the reader misses points to a passage the editor must make clearer.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import ledger
from .config import Config
from .runner import run_judge

QUIZ_SCHEMA = {"type": "object", "properties": {"questions": {"type": "array", "items": {
    "type": "object", "properties": {"q": {"type": "string"}, "a": {"type": "string"}, "claim": {"type": "string"}},
    "required": ["q", "a", "claim"]}}}, "required": ["questions"]}
ANS_SCHEMA = {"type": "object", "properties": {"answers": {"type": "array", "items": {"type": "string"}}},
              "required": ["answers"]}
GRADE_SCHEMA = {"type": "object", "properties": {"correct": {"type": "array", "items": {"type": "boolean"}}},
                "required": ["correct"]}

QUIZ = ("You write a reading-comprehension quiz for a research paper you have not seen, from the facts the paper must "
        "convey. Facts (the paper's claims, with scope and evidence):\n\n{facts}\n\nWrite {n} questions a careful reader "
        "of the paper should answer correctly and a reader who has not seen it could not guess: the method's inputs "
        "and outputs, which method is best in which setting, where an effect holds or vanishes, the size of the main "
        "effect to the nearest unit, what the paper does not claim. Each answer is a short phrase. Tag each question "
        "with the claim id it tests. Answer with JSON only.")
ANSWER = ("Answer each question in a short phrase{src}. If you cannot tell, answer \"unknown\". Answer with JSON only: "
          "{{\"answers\": [...]}} in the same order.\n\n{questions}{paper}")
GRADE = ("Grade each answer against the key. An answer is correct if it states the same fact (wording may differ; "
         "numbers within the stated rounding). \"unknown\" is wrong. Answer with JSON only: {{\"correct\": [true, false, "
         "...]}} in the same order.\n\n{items}")


def _json(r: dict, key: str):
    try:
        return json.loads(r.get("text") or "")[key]
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def run(cfg: Config, pdf: Path, n: int = 15, model: str = "sonnet") -> dict:
    from .judges import pdf_text
    led = ledger.load(cfg)
    facts = "\n".join(f"- [{c['id']}] {c['text']} (scope: {c.get('scope')}; strength: {c.get('strength')})"
                      for c in led.get("claims", []) if c.get("strength") != "unsupported")
    nums = json.loads((cfg.work / "numbers.json").read_text()) if (cfg.work / "numbers.json").exists() else {}
    keyvals = "\n".join(f"- {v.get('means')}: {v['value']:.4g}" for k, v in sorted(nums.items())
                        if isinstance(v, dict) and isinstance(v.get("value"), (int, float)))[:12000]
    qz = _json(run_judge(cfg, model, QUIZ.format(facts=facts + "\n\nMeasured values:\n" + keyvals, n=n),
                         json_schema=QUIZ_SCHEMA), "questions") or []
    if not qz:
        return {"ok": False, "error": "quiz writer failed"}
    qtext = "\n".join(f"{i + 1}. {q['q']}" for i, q in enumerate(qz))
    paper = pdf_text(pdf)
    reader = _json(run_judge(cfg, model, ANSWER.format(src=" using only the paper below", questions=qtext,
                                                       paper="\n\nThe paper:\n" + paper), json_schema=ANS_SCHEMA),
                   "answers") or []
    control = _json(run_judge(cfg, model, ANSWER.format(src=" from your general knowledge", questions=qtext,
                                                        paper=""), json_schema=ANS_SCHEMA), "answers") or []

    def grade(ans: list[str]) -> list[bool]:
        items = "\n".join(f"{i + 1}. Q: {q['q']}\n   Key: {q['a']}\n   Answer: {ans[i] if i < len(ans) else 'unknown'}"
                          for i, q in enumerate(qz))
        g = _json(run_judge(cfg, model, GRADE.format(items=items), json_schema=GRADE_SCHEMA), "correct") or []
        return [bool(g[i]) if i < len(g) else False for i in range(len(qz))]

    gr, gc = grade(reader), grade(control)
    disc = [i for i in range(len(qz)) if not gc[i]]
    missed = [{"q": qz[i]["q"], "key": qz[i]["a"], "reader": reader[i] if i < len(reader) else "",
               "claim": qz[i].get("claim")} for i in disc if not gr[i]]
    res = {"ok": True, "questions": len(qz), "discriminative": len(disc),
           "reader_right": sum(gr[i] for i in disc), "control_right_all": sum(gc),
           "score": (sum(gr[i] for i in disc) / len(disc)) if disc else 1.0, "missed": missed}
    (cfg.work / "comprehension.json").write_text(json.dumps({**res, "quiz": qz, "reader": reader, "control": control},
                                                            indent=1))
    return res
