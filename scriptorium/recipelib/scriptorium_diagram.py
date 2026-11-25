"""Diagram kit for paper/figures/*.py: flat pastel panels, rounded cards, arrows that line up by construction,
numbered steps and a small set of vector icons drawn from simple shapes, so every diagram in a paper shares one look.

    import scriptorium_diagram as sd
    d = sd.canvas("full", height=2.2)                      # coordinates are inches from the bottom left
    a = d.panel(0.05, 0.05, 2.0, 2.1, "Annotate a case", step=1)
    b = d.panel(2.35, 0.05, 2.0, 2.1, "Train the model", step=2, k=1)
    d.card(*a.inset(0.1), "Clinician", "marks a few pixels", icon="person")
    d.connect(a, b)                                        # centred in the gap, at the middle of their shared span
    d.save("teaser")                                       # paper/figures/teaser.{pdf,png} + layout for the lint

Typography: panel titles in Source Serif 4 semibold, card titles in Inter semibold, labels in Inter at 8 pt, notes at
7.5 pt in a dark gray that keeps 7:1 contrast. Every label is set in sentence case (first letter capitalized) unless
case=None; a label that wraps is one text with line breaks, never several texts.

Arrows: d.connect(a, b) joins two panels, cards or boxes through the middle of the span they share, so arrows between
shapes of equal height sit at the same height; d.flow([a, b, c]) joins a row or column at one common height;
style="badge" draws a round arrow badge for narrow gutters. d.arrow draws a straight or curved arrow between two
points; d.elbow and d.route draw right angles with rounded corners. Heads are TikZ-style stealth heads.

Rules the lint checks: text at least 7 pt at print size, no text overlapping other text or running off the figure,
readable contrast, no diagonal arrows, labels inside their box. Keep labels to one to three words; put notation in the
caption, not the figure.
"""
from __future__ import annotations

import math

import scriptorium_fig as sf

INK, NOTE = "#1B1F24", "#3D434A"               # text; secondary text (about 10:1 on white, 8:1 on the pale fills)
SIZES = {"title": 10.5, "heading": 9.0, "text": 8.0, "note": 7.5, "step": 8.0}


def soft(theme: str) -> dict:
    """Diagram fills harmonized with the theme: pale tints of the method colour and its partner, two neutrals."""
    t = sf.THEMES.get(theme, sf.THEMES[sf.DEFAULT_THEME])
    return {"soft": sf.tint(t["ours"], 0.88), "mid": sf.tint(t["ours"], 0.55), "ink": "#2B2F36",
            "fills": [sf.tint(t["ours"], 0.9), sf.tint(t["partner"], 0.9), "#F3F1EC", "#EEF1F4"]}


ICONS = ("person", "network", "monitor", "images", "document", "database", "chart", "check", "cross", "magnifier",
         "gear", "cursor")


def text_width(s: str, size: float, weight: str = "normal", family: str | None = None) -> float:
    """Width of a one-line label in inches."""
    from matplotlib.font_manager import FontProperties
    from matplotlib.textpath import TextToPath
    fp = FontProperties(family=family or sf.TEXT_FONT, weight=weight, size=size)
    w, _, _ = TextToPath().get_text_width_height_descent(s, fp, ismath=False)
    return w / 72.0


def line_height(size: float, spacing: float = 1.25) -> float:
    """Height in inches of one line of a multi-line label (Inter's line box is 1.21 em)."""
    return size * 1.21 * spacing / 72.0


def wrap(s: str, width: float, size: float, weight: str = "normal", family: str | None = None) -> str:
    """Break a label into lines no wider than `width` inches (explicit line breaks are kept)."""
    out = []
    for para in s.split("\n"):
        line = ""
        for w in para.split():
            cand = f"{line} {w}".strip()
            if line and text_width(cand, size, weight, family) > 0.96 * width:      # rendering runs a little wider
                out.append(line)
                line = w
            else:
                line = cand
        out.append(line)
    return "\n".join(out)


class Region:
    def __init__(self, x, y, w, h, rect=None):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.rect = rect or (x, y, w, h)           # the drawn shape (for a panel: including its title)

    def center(self, dx: float = 0.0, dy: float = 0.0) -> tuple[float, float]:
        return self.x + self.w / 2 + dx, self.y + self.h / 2 + dy

    def left(self, dy: float = 0.0):
        return self.x, self.y + self.h / 2 + dy

    def right(self, dy: float = 0.0):
        return self.x + self.w, self.y + self.h / 2 + dy

    def top(self, dx: float = 0.0):
        return self.x + self.w / 2 + dx, self.y + self.h

    def bottom(self, dx: float = 0.0):
        return self.x + self.w / 2 + dx, self.y

    def inset(self, m: float = 0.1) -> tuple[float, float, float, float]:
        """(x, y, w, h) of the area `m` inches inside this region, to place a card in it."""
        return self.x + m, self.y + m, self.w - 2 * m, self.h - 2 * m

    def rows(self, n: int, gap: float = 0.08, m: float = 0.1) -> list[tuple[float, float, float, float]]:
        """n equal slots stacked top to bottom inside the region, `gap` apart and `m` from its edges."""
        x, y, w, h = self.inset(m)
        hh = (h - gap * (n - 1)) / n
        return [(x, y + h - (i + 1) * hh - i * gap, w, hh) for i in range(n)]

    def cols(self, n: int, gap: float = 0.08, m: float = 0.1) -> list[tuple[float, float, float, float]]:
        x, y, w, h = self.inset(m)
        ww = (w - gap * (n - 1)) / n
        return [(x + i * (ww + gap), y, ww, h) for i in range(n)]


class Canvas:
    def __init__(self, width="full", height: float = 2.2, theme: str | None = None):
        import matplotlib.pyplot as plt
        self.pal = sf.use(theme)
        self.soft = soft(theme or sf.theme_name())
        w = sf.WIDTHS.get(width, width) if isinstance(width, str) else float(width)
        self.W, self.H = float(w), float(height)
        self.fig = plt.figure(figsize=(self.W, self.H))
        self.fig._scriptorium_width = width if isinstance(width, str) else "custom"
        self.fig._scriptorium_kind = "diagram"
        # the kit sets case per label (case=None keeps one as is); saving also puts any plot drawn inside the
        # diagram (axis labels, ticks, legend, titles) in sentence case
        self.fig._scriptorium_case = True
        self.ax = self.fig.add_axes((0, 0, 1, 1))
        self.ax.set_xlim(0, self.W)
        self.ax.set_ylim(0, self.H)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.size = SIZES["text"]
        self.sizes = dict(SIZES)
        self.panels: list[tuple[tuple, object]] = []     # (x, y, w, h), title text: titles must fit their panel
        self.issues: list[str] = []                      # problems the kit can see itself; the lint reports them
        self.regions: list[tuple] = []                   # every panel and box: text inside one must stay inside it
        self.labels: list = []

    # -- text -----------------------------------------------------------------------------------------------------
    def text(self, x, y, s, size=None, color=None, ha="center", va="center", weight="normal", bg: str | None = None,
             case: str | None = "sentence", family: str | None = None, note: bool = False, **kw):
        """A label in sentence case. `bg` is the colour behind it when that is not white, so the lint measures contrast
        correctly; note=True sets it as secondary text (smaller, dark gray)."""
        if case == "sentence":
            s = "\n".join([sf.sentence(s.split("\n")[0])] + s.split("\n")[1:])
        if note:
            size, color = size or self.sizes["note"], color or NOTE
        kw.setdefault("linespacing", 1.25)
        if va in ("center", "center_baseline") and "\n" not in s:
            # centre the capitals on y (Inter's cap height is 0.73 em), so words with and without descenders
            # sit on one line and line up with the icons beside them
            va, y = "baseline", y - 0.365 * (size or self.size) / 72.0
        t = self.ax.text(x, y, s, fontsize=size or self.size, color=color or INK, ha=ha, va=va,
                         fontweight=weight, zorder=6, family=family or sf.TEXT_FONT, **kw)
        if bg:
            t.set_gid("bg:" + bg)
        self.labels.append(t)
        return t

    # -- containers -----------------------------------------------------------------------------------------------
    def panel(self, x, y, w, h, title: str = "", step: int | None = None, fill: str | None = None, k: int = 0):
        """A flat pastel panel with rounded corners, an optional title in the display face and a numbered step.
        Returns the area under the title."""
        from matplotlib.patches import FancyBboxPatch
        fill = fill or self.soft["fills"][k % len(self.soft["fills"])]
        self.regions.append((x, y, w, h))
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.09", fc=fill,
                                         ec="none", zorder=1))
        band = 0.0
        if title or step is not None:
            band = 0.36
            ty = y + h - 0.19
            if step is not None:
                self.step(x + 0.2, ty, step)
            if title:
                tx = x + (0.38 if step is not None else 0.14)
                size = self.sizes["title"]
                while size > 9.0 and text_width(sf.sentence(title), size, "semibold", sf.DISPLAY_FONT) > 0.94 * (
                        x + w - 0.1 - tx):
                    size -= 0.25                       # a long title shrinks a little before the kit flags it
                t = self.text(tx, ty, title, ha="left", va="center_baseline", size=size,
                              weight="semibold", family=sf.DISPLAY_FONT, bg=fill)
                self.panels.append(((x, y, w, h), t))
        return Region(x, y, w, h - band, rect=(x, y, w, h))

    def box(self, x, y, w, h, label: str = "", ours: bool = False, fill: str | None = None, edge: str | None = None,
            size=None, weight: str = "medium"):
        """A rounded box with a centred label. ours=True draws it in the accent (parts of our method that learn)."""
        from matplotlib.patches import FancyBboxPatch
        self.regions.append((x, y, w, h))
        if ours:
            fc, ec = self.soft["soft"], self.pal["ours"]
            tc = sf.readable(self.pal["ours"], fc, 7.0)
        else:
            fc, ec, tc = fill or "#FFFFFF", edge or self.pal["edge"], INK
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.06", fc=fc, ec=ec,
                                         lw=1.0, zorder=3))
        if label:
            self.text(x + w / 2, y + h / 2, wrap(label, w - 0.12, size or self.size, weight), color=tc, size=size,
                      bg=fc, weight=weight, ha="center", multialignment="center")
        return Region(x, y, w, h)

    def card(self, x, y, w, h, title: str, body: str = "", icon: str | None = None, ours: bool = False,
             fill: str | None = None, edge: str | None = None, layout: str = "auto"):
        """A white card: a title, a short body wrapped to the card's width and an optional icon, the block centred
        vertically. layout="inline" puts the icon on the title's line, so the body uses the full width (the default
        for narrow cards); layout="side" puts it left of the whole block (the default for wide, short cards)."""
        from matplotlib.patches import FancyBboxPatch
        self.regions.append((x, y, w, h))
        fc = fill or "#FFFFFF"
        ec = edge or (self.pal["ours"] if ours else self.pal["edge"])
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.07", fc=fc, ec=ec,
                                         lw=1.1 if ours else 0.9, zorder=3))
        if layout == "auto":
            layout = "side" if icon and w > 2.6 * h else "inline"
        hs, ns = self.sizes["heading"], self.sizes["note"]
        pad = 0.095
        bx = x + pad
        isz = 0.0
        if icon and layout == "side":
            isz = min(0.3, h * 0.55)
            bx = x + pad + isz + 0.09
        elif icon:
            isz = min(0.19, hs * 1.5 / 72)
        tx = bx + (isz + 0.06 if icon and layout == "inline" else 0)
        title = wrap(sf.sentence(title), x + w - pad - tx, hs, "semibold")
        body = wrap(sf.sentence(body), x + w - pad - bx, ns) if body else ""
        nt, nb = title.count("\n") + 1, (body.count("\n") + 1 if body else 0)
        lh_t, lh_b, sep = line_height(hs, 1.15), line_height(ns, 1.25), (0.045 if body else 0)
        block = nt * lh_t + nb * lh_b + sep
        top = y + h / 2 + block / 2
        tcol = sf.readable(self.pal["ours"], fc, 7.0) if ours else INK
        self.text(tx, top, title, ha="left", va="top", size=hs, weight="semibold", color=tcol, bg=fc, case=None,
                  linespacing=1.15)
        if body:
            self.text(bx, top - nt * lh_t - sep, body, ha="left", va="top", note=True, bg=fc, case=None,
                      linespacing=1.25)
        if icon and layout == "side":
            self.icon(icon, x + pad + isz / 2, y + h / 2, size=isz, ours=ours)
        elif icon:
            self.icon(icon, bx + isz / 2, top - lh_t / 2, size=isz, ours=ours)
        if block > h - 0.1:
            self.issues.append(f"the card '{title[:30]}' is too small for its text; enlarge it or shorten the text")
        return Region(x, y, w, h)

    def step(self, x, y, n: int, r: float = 0.105):
        from matplotlib.patches import Circle
        self.ax.add_patch(Circle((x, y), r, fc=self.pal["ours"], ec="none", zorder=5))
        self.text(x, y, str(n), color="#FFFFFF", size=self.sizes["step"], weight="semibold", bg=self.pal["ours"],
                  va="center_baseline", case=None)

    # -- connectors -----------------------------------------------------------------------------------------------
    def _color(self, color, ours):
        return color or (self.pal["ours"] if ours else self.soft["ink"])

    def _head(self, tip, u, width, c, scale=1.0):
        """A stealth head: a long point with a notched back, sized to the line width."""
        from matplotlib.patches import Polygon
        L = (0.055 + 0.02 * width) * scale
        hw = 0.5 * L
        n = (-u[1], u[0])
        back = (tip[0] - u[0] * L, tip[1] - u[1] * L)
        notch = (tip[0] - u[0] * L * 0.68, tip[1] - u[1] * L * 0.68)
        self.ax.add_patch(Polygon([tip, (back[0] + n[0] * hw, back[1] + n[1] * hw), notch,
                                   (back[0] - n[0] * hw, back[1] - n[1] * hw)], closed=True, fc=c, ec=c, lw=0.5,
                                  joinstyle="round", zorder=5))
        return notch

    def _shaft(self, pts, width, c, dashed=False):
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=c, lw=width, solid_capstyle="round", dash_capstyle="round",
                     solid_joinstyle="round", ls=(0, (2.5, 2)) if dashed else "-", zorder=4)

    def arrow(self, p0, p1, color: str | None = None, width: float = 1.8, label: str = "", ours: bool = False,
              curve: float = 0.0, gap: float = 0.0, dashed: bool = False, head: float = 1.0):
        """An arrow from p0 to p1 with a stealth head. curve bends it (a fraction of its length; positive bends
        left); gap leaves white space at both ends. Arrows must never cross labels."""
        c = self._color(color, ours)
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        d = math.hypot(dx, dy) or 1e-9
        if not curve and abs(dx) > 0.03 and abs(dy) > 0.03:
            self.issues.append(f"the arrow from ({p0[0]:.2f}, {p0[1]:.2f}) to ({p1[0]:.2f}, {p1[1]:.2f}) is diagonal; "
                               "use horizontal or vertical runs (d.elbow or d.route for a corner), or curve it")
        ux, uy = dx / d, dy / d
        p0 = (p0[0] + ux * gap, p0[1] + uy * gap)
        p1 = (p1[0] - ux * gap, p1[1] - uy * gap)
        if curve:
            n = (-uy, ux)
            ctrl = ((p0[0] + p1[0]) / 2 + n[0] * curve * d, (p0[1] + p1[1]) / 2 + n[1] * curve * d)
            pts = [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * ctrl[0] + t * t * p1[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * ctrl[1] + t * t * p1[1]) for t in
                   [k / 40 for k in range(41)]]
            tx, ty = p1[0] - ctrl[0], p1[1] - ctrl[1]
            tn = math.hypot(tx, ty) or 1e-9
            u = (tx / tn, ty / tn)
        else:
            pts, u = [p0, p1], (ux, uy)
        notch = self._head(p1, u, width, c, head)
        # end the shaft inside the head, at its notch
        pts = [p for p in pts if (p[0] - p1[0]) * u[0] + (p[1] - p1[1]) * u[1] < -(math.hypot(notch[0] - p1[0],
                                                                                          notch[1] - p1[1]))]
        self._shaft(pts + [notch], width, c, dashed)
        if label:
            mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            horiz = abs(dx) >= abs(dy)
            self.text(mx, my + (0.1 if horiz else 0), label, size=self.sizes["note"], color=NOTE,
                      ha="center" if horiz else "left", va="bottom" if horiz else "center")

    def route(self, points, radius: float = 0.08, **kw):
        """An arrow along horizontal and vertical runs through `points`, with rounded corners."""
        c = self._color(kw.get("color"), kw.get("ours", False))
        width = kw.get("width", 1.8)
        pts = [points[0]]
        for a, b, cc in zip(points[:-2], points[1:-1], points[2:]):
            la, lb = math.hypot(b[0] - a[0], b[1] - a[1]), math.hypot(cc[0] - b[0], cc[1] - b[1])
            r = min(radius, la / 2, lb / 2)
            pa = (b[0] - (b[0] - a[0]) / la * r, b[1] - (b[1] - a[1]) / la * r)
            pb = (b[0] + (cc[0] - b[0]) / lb * r, b[1] + (cc[1] - b[1]) / lb * r)
            pts.append(pa)
            pts += [((1 - t) ** 2 * pa[0] + 2 * (1 - t) * t * b[0] + t * t * pb[0],
                     (1 - t) ** 2 * pa[1] + 2 * (1 - t) * t * b[1] + t * t * pb[1]) for t in [k / 8 for k in
                                                                                            range(1, 8)]]
            pts.append(pb)
        self._shaft(pts, width, c, kw.get("dashed", False))
        self.arrow(pts[-1], points[-1], **kw)

    def elbow(self, p0, p1, via: str = "h", **kw):
        """Two straight runs meeting at a rounded right angle (horizontal first with via='h')."""
        mid = (p1[0], p0[1]) if via == "h" else (p0[0], p1[1])
        self.route([p0, mid, p1], **kw)

    def _badge(self, c, u, r, color):
        from matplotlib.patches import Circle
        self.ax.add_patch(Circle(c, r, fc=color, ec="none", zorder=5))
        L = r * 1.05
        p0 = (c[0] - u[0] * L * 0.55, c[1] - u[1] * L * 0.55)
        tip = (c[0] + u[0] * L * 0.6, c[1] + u[1] * L * 0.6)
        self.ax.plot([p0[0], tip[0] - u[0] * 0.03], [p0[1], tip[1] - u[1] * 0.03], color="#FFFFFF", lw=1.6,
                     solid_capstyle="round", zorder=6)
        n = (-u[1], u[0])
        a = 0.42 * r
        self.ax.plot([tip[0] - u[0] * a + n[0] * a, tip[0], tip[0] - u[0] * a - n[0] * a],
                     [tip[1] - u[1] * a + n[1] * a, tip[1], tip[1] - u[1] * a - n[1] * a], color="#FFFFFF", lw=1.6,
                     solid_capstyle="round", solid_joinstyle="round", zorder=6)

    def connect(self, a: Region, b: Region, at: float | None = None, gap: float = 0.05, style: str = "arrow",
                **kw):
        """Join two shapes. Side by side: a horizontal arrow through the middle of the height they share (or at
        y=at); stacked: a vertical arrow through the middle of the width they share. Otherwise a rounded elbow.
        style="badge" puts a round arrow badge in the middle of the gap instead."""
        ax_, ay, aw, ah = a.rect
        bx, by, bw, bh = b.rect
        ylo, yhi = max(ay, by), min(ay + ah, by + bh)
        xlo, xhi = max(ax_, bx), min(ax_ + aw, bx + bw)
        if yhi - ylo > 0.04 and (bx >= ax_ + aw - 1e-6 or ax_ >= bx + bw - 1e-6):
            y = (ylo + yhi) / 2 if at is None else at
            p0, p1 = ((ax_ + aw, y), (bx, y)) if bx >= ax_ + aw - 1e-6 else ((ax_, y), (bx + bw, y))
        elif xhi - xlo > 0.04:
            x = (xlo + xhi) / 2 if at is None else at
            p0, p1 = ((x, ay), (x, by + bh)) if by + bh <= ay + 1e-6 else ((x, ay + ah), (x, by))
        else:
            right = bx >= ax_ + aw
            p0 = (ax_ + aw + gap, ay + ah / 2) if right else (ax_ - gap, ay + ah / 2)
            p1 = (bx + bw / 2, by + bh + gap) if by + bh < ay else (bx + bw / 2, by - gap)
            self.elbow(p0, p1, via="h", **kw)
            return
        if style == "badge":
            dist = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            u = ((p1[0] - p0[0]) / dist, (p1[1] - p0[1]) / dist)
            r = min(0.13, dist / 2 + 0.06)
            self._badge(((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2), u, r, self._color(kw.get("color"),
                                                                                     kw.get("ours", False)))
            return
        self.arrow(p0, p1, gap=gap, **kw)

    def flow(self, shapes: list[Region], **kw):
        """Join a row (or column) of shapes left to right (top to bottom), every arrow at one common height (or x):
        the middle of the span all of them share."""
        rs = [s.rect for s in shapes]
        lo, hi = max(r[1] for r in rs), min(r[1] + r[3] for r in rs)
        horiz = hi - lo > 0.04
        if not horiz:
            lo, hi = max(r[0] for r in rs), min(r[0] + r[2] for r in rs)
        kw.setdefault("at", (lo + hi) / 2 if hi > lo else None)
        for a, b in zip(shapes[:-1], shapes[1:]):
            self.connect(a, b, **kw)

    # -- images -----------------------------------------------------------------------------------------------------
    def image(self, path, x, y, w, h, border: str | None = None):
        """A real image thumbnail (PNG/JPG from the repository), fitted into the box."""
        import matplotlib.image as mpimg
        from matplotlib.patches import Rectangle
        img = mpimg.imread(path)
        self.ax.imshow(img, extent=(x, x + w, y, y + h), zorder=3, interpolation="lanczos",
                       cmap="gray" if img.ndim == 2 else None)
        self.ax.add_patch(Rectangle((x, y), w, h, fill=False, ec=border or self.pal["edge"], lw=0.6, zorder=4))
        return Region(x, y, w, h)

    # -- icons ------------------------------------------------------------------------------------------------------
    def icon(self, name: str, x: float, y: float, size: float = 0.5, color: str | None = None, ours: bool = False):
        """Draw a simple flat icon centred at (x, y), `size` inches tall."""
        if name not in ICONS:
            raise ValueError(f"unknown icon {name!r}; choose from {', '.join(ICONS)}")
        c = color or (self.pal["ours"] if ours else self.soft["ink"])
        getattr(self, "_i_" + name)(x, y, size, c)
        return Region(x - size / 2, y - size / 2, size, size)

    def _p(self, patch):
        patch.set_zorder(5)
        self.ax.add_patch(patch)

    def _i_person(self, x, y, s, c):
        from matplotlib.patches import Circle, FancyBboxPatch
        self._p(Circle((x, y + 0.22 * s), 0.16 * s, fc=c, ec="none"))
        self._p(FancyBboxPatch((x - 0.3 * s, y - 0.48 * s), 0.6 * s, 0.45 * s,
                               boxstyle=f"round,pad=0,rounding_size={0.2 * s}", fc=c, ec="none"))

    def _i_network(self, x, y, s, c):
        from matplotlib.patches import Circle, FancyBboxPatch
        self._p(FancyBboxPatch((x - 0.5 * s, y - 0.4 * s), s, 0.8 * s, boxstyle=f"round,pad=0,rounding_size={0.1 * s}",
                               fc="#FFFFFF", ec=c, lw=1.0))
        cols = [(-0.28, (-0.18, 0.0, 0.18)), (0.0, (-0.24, -0.08, 0.08, 0.24)), (0.28, (-0.1, 0.1))]
        pts = [[(x + cx * s, y + cy * s) for cy in ys] for cx, ys in cols]
        for a, b in zip(pts[:-1], pts[1:]):
            for p in a:
                for q in b:
                    self.ax.plot([p[0], q[0]], [p[1], q[1]], color=c, lw=0.4, alpha=0.6, zorder=5)
        for col in pts:
            for p in col:
                self._p(Circle(p, 0.045 * s, fc=c, ec="none"))

    def _i_monitor(self, x, y, s, c):
        from matplotlib.patches import FancyBboxPatch, Rectangle
        self._p(FancyBboxPatch((x - 0.5 * s, y - 0.2 * s), s, 0.62 * s, boxstyle=f"round,pad=0,rounding_size={0.05 * s}",
                               fc="#FFFFFF", ec=c, lw=1.2))
        self._p(Rectangle((x - 0.05 * s, y - 0.36 * s), 0.1 * s, 0.16 * s, fc=c, ec="none"))
        self._p(Rectangle((x - 0.22 * s, y - 0.42 * s), 0.44 * s, 0.06 * s, fc=c, ec="none"))

    def _i_images(self, x, y, s, c):
        from matplotlib.patches import Polygon, Rectangle
        for k in (2, 1, 0):
            o = 0.09 * s * k
            self._p(Rectangle((x - 0.38 * s + o, y - 0.38 * s + o), 0.6 * s, 0.6 * s, fc="#FFFFFF", ec=c, lw=0.9))
        self._p(Polygon([(x - 0.32 * s, y - 0.32 * s), (x - 0.12 * s, y - 0.05 * s), (x + 0.02 * s, y - 0.2 * s),
                         (x + 0.16 * s, y - 0.32 * s)], closed=True, fc=self.soft["mid"], ec="none"))

    def _i_document(self, x, y, s, c):
        from matplotlib.patches import Polygon
        w, h, f = 0.62 * s, 0.82 * s, 0.18 * s
        x0, y0 = x - w / 2, y - h / 2
        self._p(Polygon([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h - f), (x0 + w - f, y0 + h), (x0, y0 + h)],
                        closed=True, fc="#FFFFFF", ec=c, lw=1.0))
        for k in range(4):
            yy = y0 + h - 0.3 * s - k * 0.13 * s
            self.ax.plot([x0 + 0.1 * s, x0 + w - 0.1 * s - (0.15 * s if k == 3 else 0)], [yy, yy], color=c, lw=0.8,
                         zorder=6)

    def _i_database(self, x, y, s, c):
        from matplotlib.patches import Ellipse, Rectangle
        w, h = 0.7 * s, 0.75 * s
        self._p(Rectangle((x - w / 2, y - h / 2), w, h, fc="#FFFFFF", ec="none"))
        self.ax.plot([x - w / 2, x - w / 2], [y - h / 2, y + h / 2], color=c, lw=1.0, zorder=6)
        self.ax.plot([x + w / 2, x + w / 2], [y - h / 2, y + h / 2], color=c, lw=1.0, zorder=6)
        for yy in (y - h / 2, y, y + h / 2):
            e = Ellipse((x, yy), w, 0.22 * s, fc="#FFFFFF" if yy == y + h / 2 else "none", ec=c, lw=1.0)
            e.set_zorder(6)
            self.ax.add_patch(e)

    def _i_chart(self, x, y, s, c):
        from matplotlib.patches import Rectangle
        for k, hh in enumerate((0.3, 0.55, 0.42, 0.75)):
            self._p(Rectangle((x - 0.38 * s + k * 0.2 * s, y - 0.38 * s), 0.14 * s, hh * s,
                              fc=c if k == 3 else self.soft["mid"], ec="none"))
        self.ax.plot([x - 0.42 * s, x + 0.42 * s], [y - 0.38 * s] * 2, color=c, lw=0.8, zorder=6)

    def _i_check(self, x, y, s, c):
        from matplotlib.patches import Circle
        self._p(Circle((x, y), 0.4 * s, fc=c, ec="none"))
        self.ax.plot([x - 0.18 * s, x - 0.04 * s, x + 0.2 * s], [y, y - 0.15 * s, y + 0.16 * s], color="#FFFFFF",
                     lw=2.0, solid_capstyle="round", zorder=6)

    def _i_cross(self, x, y, s, c):
        from matplotlib.patches import Circle
        self._p(Circle((x, y), 0.4 * s, fc=c, ec="none"))
        for sgn in (1, -1):
            self.ax.plot([x - 0.15 * s, x + 0.15 * s], [y - sgn * 0.15 * s, y + sgn * 0.15 * s], color="#FFFFFF",
                         lw=2.0, solid_capstyle="round", zorder=6)

    def _i_magnifier(self, x, y, s, c):
        from matplotlib.patches import Circle
        self._p(Circle((x - 0.08 * s, y + 0.08 * s), 0.26 * s, fc="#FFFFFF", ec=c, lw=1.6))
        self.ax.plot([x + 0.1 * s, x + 0.34 * s], [y - 0.1 * s, y - 0.34 * s], color=c, lw=2.6,
                     solid_capstyle="round", zorder=6)

    def _i_gear(self, x, y, s, c):
        from matplotlib.patches import Circle, Polygon
        n, r0, r1 = 8, 0.27 * s, 0.38 * s
        pts = []
        for k in range(2 * n):
            a = math.pi * k / n
            r = r1 if k % 2 == 0 else r0
            pts.append((x + r * math.cos(a), y + r * math.sin(a)))
        self._p(Polygon(pts, closed=True, fc=c, ec="none", joinstyle="round"))
        self._p(Circle((x, y), 0.12 * s, fc="#FFFFFF", ec="none"))

    def _i_cursor(self, x, y, s, c):
        from matplotlib.patches import Polygon
        pts = [(0, 0.4), (0, -0.22), (0.12, -0.1), (0.22, -0.34), (0.3, -0.3), (0.2, -0.06), (0.36, -0.06)]
        self._p(Polygon([(x - 0.15 * s + px * s, y + py * s) for px, py in pts], closed=True, fc=c, ec="#FFFFFF",
                        lw=0.8))

    # -- output -----------------------------------------------------------------------------------------------------
    def save(self, fid: str) -> None:
        self.fig.canvas.draw()
        r = self.fig.canvas.get_renderer()
        inv = self.ax.transData.inverted()
        for (x, y, w, h), t in self.panels:
            bb = t.get_window_extent(r)
            (x0, _), (x1, _) = inv.transform((bb.x0, bb.y0)), inv.transform((bb.x1, bb.y1))
            if x1 > x + w - 0.04:
                self.issues.append(f"the panel title '{t.get_text()[:30]}' runs to the panel's edge; shorten it or "
                                   "widen the panel")
        for t in self.labels:
            ax, ay = t.get_position()
            inside = [r for r in self.regions if r[0] <= ax <= r[0] + r[2] and r[1] <= ay <= r[1] + r[3]]
            if not inside:
                continue
            rx, ry, rw, rh = min(inside, key=lambda r: r[2] * r[3])          # the innermost container
            bb = t.get_window_extent(r)
            (x0, y0), (x1, y1) = inv.transform((bb.x0, bb.y0)), inv.transform((bb.x1, bb.y1))
            if x0 < rx - 0.02 or x1 > rx + rw + 0.02 or y0 < ry - 0.02 or y1 > ry + rh + 0.02:
                self.issues.append(f"the label '{t.get_text()[:30]}' runs past the edge of the box or panel it sits "
                                   "in; shorten it, wrap it onto two lines, or enlarge the box")
        self.fig._scriptorium_issues = list(dict.fromkeys(self.issues))
        sf.save(self.fig, fid)


def canvas(width="full", height: float = 2.2, theme: str | None = None) -> Canvas:
    return Canvas(width, height, theme)
