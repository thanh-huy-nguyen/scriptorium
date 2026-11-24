"""Figure lint: deterministic checks of every rendered figure at its print size.

Data figures saved with scriptorium_fig.save() leave paper/figures/<id>.layout.json, from which we check:
- text smaller than the minimum point size at print width (scaled when the figure is placed wider or narrower);
- text overlapping other text, and text running off the figure;
- the legend covering data marks;
- series colours that become hard to tell apart under deuteranopia or protanopia;
- the paper's own method not drawn in the accent colour, or the accent used for a baseline;
- values drawn from typed numbers rather than recipes (no scriptorium_fig.recipe() call).

Diagrams (any figure PDF without a layout file) are checked from the PDF: words overlapping words and text off the
page. Every check is code; the vision critic comes after the lint passes.
"""
from __future__ import annotations

import json
import re
import math
from pathlib import Path

from .config import Config

MIN_PT = 6.2
WIDTHS = {"column": 3.25, "full": 6.75, "half": 3.25}


# --- colour helpers ---------------------------------------------------------------------------------------------------

def _rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    r, g, b = (_lin(c) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


# Machado et al. (2009) severity-1.0 matrices, applied in linear RGB.
CVD = {"deuteranopia": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
       "protanopia": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998))}


def _simulate(rgb, kind):
    lin = [_lin(c) for c in rgb]
    out = [max(0.0, min(1.0, sum(m * c for m, c in zip(row, lin)))) for row in CVD[kind]]
    return tuple((12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055) for c in out)


def delta_e(a, b) -> float:
    return math.dist(_lab(a), _lab(b))


def contrast(fg: str, bg: str = "#ffffff") -> float:
    def lum(h):
        r, g, b = (_lin(c) for c in _rgb(h))
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    l1, l2 = sorted((lum(fg), lum(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


# --- checks -------------------------------------------------------------------------------------------------------------

def _overlap(a, b) -> float:
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    if w <= 0 or h <= 0:
        return 0.0
    small = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1])) or 1e-9
    return w * h / small


def lint_layout(fid: str, lay: dict, placed: str | None, ours_labels: list[str]) -> list[str]:
    out = []
    W, H = lay["size"]
    target = WIDTHS.get(placed or lay.get("width") or "column", W)
    scale = target / W if W else 1.0
    texts = lay.get("texts", [])
    small = [(t["size"] * scale, t["text"]) for t in texts if t["size"] * scale < MIN_PT - 1e-6]
    if small:
        pt = min(s for s, _ in small)
        ex = ", ".join(f"'{x[:18]}'" for _, x in small[:4])
        out.append(f"{fid}: {len(small)} text item(s) below {MIN_PT} pt at print size (smallest {pt:.1f} pt; e.g. "
                   f"{ex}); draw the figure at its print width with sf.figure() or enlarge the fonts")
    for t in texts:
        x0, y0, x1, y1 = t["box"]
        if x0 < -0.01 or y0 < -0.01 or x1 > W + 0.01 or y1 > H + 0.01:
            out.append(f"{fid}: text '{t['text'][:30]}' runs off the figure")
        bg = t.get("bg") or "#ffffff"
        if contrast(t.get("color", "#000000"), bg) < 4.5:
            out.append(f"{fid}: text '{t['text'][:30]}' in {t.get('color')} has contrast below 4.5:1 on {bg}")
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            if _overlap(texts[i]["box"], texts[j]["box"]) > 0.15:
                out.append(f"{fid}: text '{texts[i]['text'][:25]}' overlaps '{texts[j]['text'][:25]}'")
    out += [f"{fid}: {i}" for i in lay.get("issues") or []]
    if lay.get("kind") == "diagram":
        return sorted(set(out))
    for lg in lay.get("legends", []):
        inside = sum(lg[0] <= x <= lg[2] and lg[1] <= y <= lg[3] for x, y in lay.get("marks", []))
        if inside:
            out.append(f"{fid}: the legend covers {inside} data mark(s); move it off the data")
    pal = lay.get("palette") or {}
    cols = {}
    for s in lay.get("series", []):
        lab = s.get("label") or ""
        if lab and not lab.startswith("_"):
            cols.setdefault(lab, s["color"])
    names = list(cols)
    for kind in CVD:
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = _simulate(_rgb(cols[names[i]]), kind), _simulate(_rgb(cols[names[j]]), kind)
                if cols[names[i]] != cols[names[j]] and delta_e(a, b) < 12:
                    out.append(f"{fid}: '{names[i]}' and '{names[j]}' look alike under {kind} (use another ink, a "
                               "marker or a line style)")
    accent = (pal.get("ours") or "#4e2a84").lower()
    for lab, c in cols.items():
        is_ours = any(o.lower() in lab.lower() for o in ours_labels) or "ours" in lab.lower()
        if is_ours and c.lower() != accent:
            out.append(f"{fid}: our method ('{lab}') is not in the accent colour {accent}")
        if not is_ours and c.lower() == accent:
            out.append(f"{fid}: '{lab}' uses the accent colour, which is reserved for our method")
    if lay.get("marks") and not lay.get("recipes"):
        out.append(f"{fid}: no value comes from scriptorium_fig.recipe(); plot recipe values so the figure shows "
                   "exactly the numbers the text prints")
    return sorted(set(out))


def lint_pdf(fid: str, pdf: Path) -> list[str]:
    """For diagrams: words overlapping other words, and words off the page."""
    try:
        import pymupdf
    except ImportError:
        return []
    out = []
    try:
        page = pymupdf.open(str(pdf))[0]
    except Exception as e:  # noqa: BLE001
        return [f"{fid}: cannot open the PDF ({e})"]
    W, H = page.rect.width, page.rect.height
    words = page.get_text("words")
    boxes = [(w[0], w[1], w[2], w[3], w[4], (w[5], w[6])) for w in words]
    for b in boxes:
        if b[0] < -1 or b[1] < -1 or b[2] > W + 1 or b[3] > H + 1:
            out.append(f"{fid}: '{b[4][:20]}' runs off the figure")
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if boxes[i][5] == boxes[j][5]:
                continue
            if _overlap(boxes[i][:4], boxes[j][:4]) > 0.25:
                out.append(f"{fid}: '{boxes[i][4][:20]}' overlaps '{boxes[j][4][:20]}'")
    for s in page.get_text("dict")["blocks"]:
        for line in s.get("lines", []):
            for span in line.get("spans", []):
                if span["text"].strip() and span["size"] < MIN_PT - 0.05:
                    out.append(f"{fid}: text '{span['text'][:20]}' is {span['size']:.1f} pt (minimum {MIN_PT})")
    return sorted(set(out))[:30]


HEX_RE = re.compile(r"['\"]#([0-9A-Fa-f]{6})['\"]")


def theme_colors(cfg: Config) -> dict:
    import importlib.util
    from .config import PKG
    spec = importlib.util.spec_from_file_location("_sf", PKG / "recipelib" / "scriptorium_fig.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.THEMES.get(cfg.theme, m.THEMES[m.DEFAULT_THEME])


def typed_colors(script: Path) -> list[str]:
    """Chromatic colours typed into a figure script (neutral grays are fine): figures take colours from the theme."""
    out = []
    for h in HEX_RE.findall(script.read_text() if script.exists() else ""):
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        if max(r, g, b) - min(r, g, b) > 24:
            out.append("#" + h.upper())
    return sorted(set(out))


def color_rule(cfg: Config, fid: str) -> list[str]:
    typed = typed_colors(cfg.paper / "figures" / f"{fid}.py")
    if not typed:
        return []
    t = theme_colors(cfg)
    return [f"{fid}: the script types colours ({', '.join(typed[:6])}); take them from the theme '{cfg.theme}' "
            f"instead: sf.color(name, ours=True) is {t['ours']}, partner=True {t['partner']}, other baselines "
            f"sf.color(name) from {', '.join(t['base'])}; diagram fills come from d.panel(k=...) and box(ours=True)"]


def lint(cfg: Config, figures: list[dict], ours_labels: list[str] | None = None) -> dict[str, list[str]]:
    """Lint every planned figure. `figures` are the outline's figure entries (id, kind, width)."""
    res = {}
    fdir = cfg.paper / "figures"
    for f in figures:
        fid = f.get("id")
        rule = color_rule(cfg, fid)
        lay_p, pdf = fdir / f"{fid}.layout.json", fdir / f"{fid}.pdf"
        if lay_p.exists():
            res[fid] = lint_layout(fid, json.loads(lay_p.read_text()), f.get("width"), ours_labels or [])
        elif pdf.exists():
            res[fid] = lint_pdf(fid, pdf)
            if f.get("kind") == "plot":
                res[fid].append(f"{fid}: a data plot must be saved with scriptorium_fig.save() so it can be checked")
        else:
            res[fid] = [f"{fid}: paper/figures/{fid}.pdf does not exist"]
        res[fid] = res[fid] + rule
    return res
