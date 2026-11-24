"""Diagram kit for paper/figures/*.py: flat pastel panels, rounded boxes, thick straight arrows, numbered steps and a
small set of vector icons drawn from simple shapes, so every diagram in a paper shares one look.

    import scriptorium_diagram as sd
    d = sd.canvas("full", height=2.2)                      # coordinates are inches from the bottom left
    p = d.panel(0.1, 0.1, 2.1, 2.0, "Annotate a case", step=1)
    d.icon("person", *p.center(dy=0.2), size=0.6)
    d.box(2.6, 0.8, 1.4, 0.6, "Model", ours=True)
    d.arrow((2.2, 1.1), (2.6, 1.1))
    d.save("teaser")                                       # paper/figures/teaser.{pdf,png} + layout for the lint

Rules the lint checks: text at least 6.2 pt at print size, no text overlapping other text or running off the figure,
readable contrast. Keep labels to one to three words; put notation in the caption, not the figure.
"""
from __future__ import annotations

import math

import scriptorium_fig as sf

def soft(theme: str) -> dict:
    """Diagram fills harmonized with the theme: pale tints of the method colour and its partner, two neutrals."""
    t = sf.THEMES.get(theme, sf.THEMES[sf.DEFAULT_THEME])
    return {"soft": sf.tint(t["ours"], 0.88), "mid": sf.tint(t["ours"], 0.55), "ink": "#2B2F36",
            "fills": [sf.tint(t["ours"], 0.9), sf.tint(t["partner"], 0.9), "#F3F1EC", "#EEF1F4"]}


ICONS = ("person", "network", "monitor", "images", "document", "database", "chart", "check", "cross", "magnifier",
         "gear", "cursor")


class Region:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

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
        self.ax = self.fig.add_axes((0, 0, 1, 1))
        self.ax.set_xlim(0, self.W)
        self.ax.set_ylim(0, self.H)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.size = 7.5
        self.panels: list[tuple[tuple, object]] = []     # (x, y, w, h), title text: titles must fit their panel
        self.issues: list[str] = []                      # problems the kit can see itself; the lint reports them
        self.regions: list[tuple] = []                   # every panel and box: text inside one must stay inside it
        self.labels: list = []

    # -- text -----------------------------------------------------------------------------------------------------
    def text(self, x, y, s, size=None, color=None, ha="center", va="center", weight="normal", bg: str | None = None,
             **kw):
        """A label. `bg` is the colour behind it when that is not white, so the lint measures contrast correctly."""
        t = self.ax.text(x, y, s, fontsize=size or self.size, color=color or self.pal["text"], ha=ha, va=va,
                         fontweight=weight, zorder=6, **kw)
        if bg:
            t.set_gid("bg:" + bg)
        self.labels.append(t)
        return t

    # -- containers -----------------------------------------------------------------------------------------------
    def panel(self, x, y, w, h, title: str = "", step: int | None = None, fill: str | None = None, k: int = 0):
        """A flat pastel panel with rounded corners, an optional plain title and a numbered step circle."""
        from matplotlib.patches import FancyBboxPatch
        fill = fill or self.soft["fills"][k % len(self.soft["fills"])]
        self.regions.append((x, y, w, h))
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.08", fc=fill,
                                         ec="none", zorder=1))
        if title:
            tx = x + 0.12 + (0.24 if step is not None else 0)
            t = self.text(tx, y + h - 0.14, title, ha="left", va="center", bg=fill)
            self.panels.append(((x, y, w, h), t))
        if step is not None:
            self.step(x + 0.17, y + h - 0.14, step)
        return Region(x, y, w, h - (0.3 if title else 0))

    def box(self, x, y, w, h, label: str = "", ours: bool = False, fill: str | None = None, edge: str | None = None,
            size=None):
        """A rounded box. ours=True draws it in the accent (parts of our method that learn)."""
        from matplotlib.patches import FancyBboxPatch
        self.regions.append((x, y, w, h))
        if ours:
            fc, ec = self.soft["soft"], self.pal["ours"]
            tc = sf.readable(self.pal["ours"], fc)
        else:
            fc, ec, tc = fill or "#FFFFFF", edge or self.pal["edge"], self.pal["text"]
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.06", fc=fc, ec=ec,
                                         lw=1.0, zorder=3))
        if label:
            self.text(x + w / 2, y + h / 2, label, color=tc, size=size, bg=fc)
        return Region(x, y, w, h)

    def step(self, x, y, n: int, r: float = 0.09):
        from matplotlib.patches import Circle
        self.ax.add_patch(Circle((x, y), r, fc=self.pal["ours"], ec="none", zorder=5))
        self.text(x, y - 0.005, str(n), color="#FFFFFF", size=self.size - 1, bg=self.pal["ours"])

    # -- connectors -----------------------------------------------------------------------------------------------
    def arrow(self, p0, p1, color: str | None = None, width: float = 2.2, label: str = "", ours: bool = False):
        """A thick straight arrow with a rounded tail. Route around text yourself: arrows must never cross labels."""
        from matplotlib.patches import FancyArrowPatch
        c = color or (self.pal["ours"] if ours else self.soft["ink"])
        dx, dy = abs(p1[0] - p0[0]), abs(p1[1] - p0[1])
        if dx > 0.03 and dy > 0.03:
            self.issues.append(f"the arrow from ({p0[0]:.2f}, {p0[1]:.2f}) to ({p1[0]:.2f}, {p1[1]:.2f}) is diagonal; "
                               "use horizontal or vertical runs (d.elbow for a corner)")
        self.ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=f"-|>,head_length={2.6 * width},head_width={1.9 * width}", mutation_scale=1,
                                          lw=width, color=c, capstyle="round", joinstyle="round", zorder=4,
                                          shrinkA=2, shrinkB=2))
        if label:
            mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            horiz = abs(p1[0] - p0[0]) >= abs(p1[1] - p0[1])
            self.text(mx, my + (0.11 if horiz else 0), label, size=self.size - 1,
                      ha="center" if horiz else "left", va="bottom" if horiz else "center")

    def elbow(self, p0, p1, via: str = "h", **kw):
        """Two straight segments meeting at a right angle (horizontal first with via='h')."""
        mid = (p1[0], p0[1]) if via == "h" else (p0[0], p1[1])
        self.ax.plot([p0[0], mid[0]], [p0[1], mid[1]], color=kw.get("color") or self.soft["ink"],
                     lw=kw.get("width", 2.2), solid_capstyle="round", zorder=4)
        self.arrow(mid, p1, **kw)

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
