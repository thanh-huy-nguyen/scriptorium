"""A plain-language lint for the paper's prose: words and habits that make text read as machine-written."""
from __future__ import annotations

import re
from pathlib import Path

BANNED = [
    "delve", "dive into", "leverage", "leverages", "leveraging", "harness", "unlock", "unleash", "pivotal", "paramount",
    "seamless", "seamlessly", "cutting-edge", "groundbreaking", "revolutionize", "game-changer", "transformative",
    "holistic", "synergy", "tapestry", "landscape", "realm", "intricate", "nuanced", "multifaceted", "meticulous",
    "meticulously", "underscore", "underscores", "showcase", "showcases", "foster", "bolster", "navigate", "embark",
    "elevate", "streamline", "empower", "paving the way", "a testament to", "it is worth noting", "it is important to note",
    "notably,", "importantly,", "in today's world", "in the realm of", "not only",
]


BRITISH = re.compile(r"\b(regularis|memoris|normalis|optimis|generalis|minimis|maximis|summaris|categoris|characteris|"
                     r"initialis|parameteris|visualis|recognis|organis|utilis|standardis|randomis|analys(e|ed|ing)\b|"
                     r"behaviour|colour|favour|labour|neighbour|modell|labell|travell|signall|centre|programme\b)",
                     re.I)


def _strip(tex: str) -> str:
    tex = re.sub(r"(?<!\\)%.*", "", tex)
    return tex


def lint(paper: Path) -> list[str]:
    out = []
    for f in sorted(paper.glob("*.tex")):
        if f.name == "main.tex":
            continue
        for i, line in enumerate(_strip(f.read_text()).splitlines(), 1):
            low = line.lower()
            for w in BANNED:
                if re.search(rf"(?<![a-z]){re.escape(w)}(?![a-z])", low):
                    out.append(f"{f.name}:{i}: '{w}'")
            if "&" in line and re.search(r"(^|&)\s*(--?|---|\u2013|\u2014|n/a|N/A)\s*(?=&|\\\\|$)", line):
                out.append(f"{f.name}:{i}: empty or placeholder table cell")
            elif "---" in line or "\u2014" in line:
                out.append(f"{f.name}:{i}: em dash")
            for m in BRITISH.finditer(line):
                out.append(f"{f.name}:{i}: British spelling '{m.group(0)}...' (use American English)")
            if "!" in re.sub(r"\\[a-zA-Z]+|!\]|\[!", "", line) and re.search(r"[a-z]!(\s|$)", line):
                out.append(f"{f.name}:{i}: exclamation mark")
    return out
