"""Tiny diagram builder that follows the diagram-design editorial system.

Each diagram is authored as data (nodes with explicit grid coordinates, orthogonal edges) and
rendered to a self-contained HTML file (inline SVG, Google Fonts only). PNGs are rendered from a
frame-only HTML with headless Chrome so the same image works in Markdown and in video slides.

Canvas: slide-16x9 preset (viewBox 1280 x 720) with the presentation type ramp:
node name 16, sublabel 12, arrow label 12, tag 8.
"""

from __future__ import annotations

import html
import os
import subprocess
from dataclasses import dataclass, field

PAPER = "#f5f5f5"
PAPER2 = "#ececec"
INK = "#2d3142"
MUTED = "#4f5d75"
SOFT = "#7a8399"
ACCENT = "#eb6c36"
LINK = "#2e5aa8"
RULE = "rgba(45,49,66,0.12)"

W, H = 1280, 720
FONTS = (
    "https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600"
    "&family=Geist+Mono:wght@400;500;600&display=swap"
)

KINDS = {
    #          fill                         stroke                       dash
    "step": ("#ffffff", INK, None),
    "focal": ("rgba(235,108,54,0.08)", ACCENT, None),
    "store": ("rgba(45,49,66,0.05)", MUTED, None),
    "external": ("rgba(45,49,66,0.03)", "rgba(45,49,66,0.30)", None),
    "input": ("rgba(79,93,117,0.10)", SOFT, None),
    "optional": ("rgba(45,49,66,0.02)", "rgba(45,49,66,0.20)", "4,3"),
    "boundary": ("rgba(235,108,54,0.05)", "rgba(235,108,54,0.50)", "4,4"),
}
LEGEND_NAMES = {
    "step": "Step / component",
    "focal": "Focal (key idea)",
    "store": "File / state",
    "external": "External system",
    "input": "Input / user",
    "optional": "Optional / deprecated",
    "boundary": "Trap / watch out",
}
EDGE_COLORS = {"default": (MUTED, "arrow"), "accent": (ACCENT, "arrow-accent"), "link": (LINK, "arrow-link")}


def esc(s: str) -> str:
    return html.escape(s, quote=True)


@dataclass
class Node:
    id: str
    x: int
    y: int
    w: int
    h: int
    name: str
    sub: str | None = None
    tag: str | None = None
    kind: str = "step"
    sub2: str | None = None

    def port(self, side: str, frac: float = 0.5) -> tuple[float, float]:
        if side == "l":
            return self.x, self.y + self.h * frac
        if side == "r":
            return self.x + self.w, self.y + self.h * frac
        if side == "t":
            return self.x + self.w * frac, self.y
        return self.x + self.w * frac, self.y + self.h  # "b"


@dataclass
class Edge:
    src: str
    dst: str
    s: str = "r"  # source side l/r/t/b
    d: str = "l"  # dest side
    label: str | None = None
    style: str = "default"
    dashed: bool = False
    sf: float = 0.5  # attach fraction along source side
    df: float = 0.5  # attach fraction along dest side
    mid: float | None = None  # coordinate of the middle segment (x for h-v-h, y for v-h-v)
    label_seg: int | None = None  # which segment carries the label (default: longest)
    label_side: str = "above"  # above/below for horizontal, right/left for vertical


@dataclass
class Zone:
    x: int
    y: int
    w: int
    h: int
    label: str


@dataclass
class Diagram:
    slug: str
    title: str
    eyebrow: str
    desc: str
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    zones: list[Zone] = field(default_factory=list)
    notes: list[tuple[int, int, str]] = field(default_factory=list)  # italic serif asides (x, y, text)
    height: int = H

    def node(self, *a, **k) -> Node:
        n = Node(*a, **k)
        self.nodes.append(n)
        return n

    def edge(self, *a, **k) -> Edge:
        e = Edge(*a, **k)
        self.edges.append(e)
        return e

    def zone(self, *a, **k) -> Zone:
        z = Zone(*a, **k)
        self.zones.append(z)
        return z

    # ------------------------------------------------------------------ routing
    def _points(self, e: Edge) -> list[tuple[float, float]]:
        a = self.by_id[e.src].port(e.s, e.sf)
        b = self.by_id[e.dst].port(e.d, e.df)
        horiz_start = e.s in "lr"
        horiz_end = e.d in "lr"
        if horiz_start and horiz_end:
            if abs(a[1] - b[1]) < 0.5:
                return [a, b]
            mx = e.mid if e.mid is not None else (a[0] + b[0]) / 2
            return [a, (mx, a[1]), (mx, b[1]), b]
        if not horiz_start and not horiz_end:
            if abs(a[0] - b[0]) < 0.5:
                return [a, b]
            my = e.mid if e.mid is not None else (a[1] + b[1]) / 2
            return [a, (a[0], my), (b[0], my), b]
        if horiz_start:  # h then v
            return [a, (b[0], a[1]), b]
        return [a, (a[0], b[1]), b]  # v then h

    @staticmethod
    def _path(pts: list[tuple[float, float]], r: float = 8) -> str:
        d = f"M {pts[0][0]:.1f},{pts[0][1]:.1f}"
        for i in range(1, len(pts) - 1):
            p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
            l1 = abs(p1[0] - p0[0]) + abs(p1[1] - p0[1])
            l2 = abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])
            rr = min(r, l1 / 2, l2 / 2)
            ux1 = ((p1[0] - p0[0]) / l1, (p1[1] - p0[1]) / l1) if l1 else (0, 0)
            ux2 = ((p2[0] - p1[0]) / l2, (p2[1] - p1[1]) / l2) if l2 else (0, 0)
            b1 = (p1[0] - ux1[0] * rr, p1[1] - ux1[1] * rr)
            b2 = (p1[0] + ux2[0] * rr, p1[1] + ux2[1] * rr)
            d += f" L {b1[0]:.1f},{b1[1]:.1f} Q {p1[0]:.1f},{p1[1]:.1f} {b2[0]:.1f},{b2[1]:.1f}"
        d += f" L {pts[-1][0]:.1f},{pts[-1][1]:.1f}"
        return d

    # ------------------------------------------------------------------ render
    def svg(self) -> str:
        self.by_id = {n.id: n for n in self.nodes}
        hgt = self.height
        out = [
            f'<svg viewBox="0 0 {W} {hgt}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-labelledby="{self.slug}-title {self.slug}-desc">',
            f'<title id="{self.slug}-title">{esc(self.title)}</title>',
            f'<desc id="{self.slug}-desc">{esc(self.desc)}</desc>',
            "<defs>",
            f'<marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker>',
            f'<marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{ACCENT}"/></marker>',
            f'<marker id="arrow-link" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{LINK}"/></marker>',
            "</defs>",
            f'<rect width="100%" height="100%" fill="{PAPER}"/>',
        ]
        # zones first
        for z in self.zones:
            out.append(
                f'<rect x="{z.x}" y="{z.y}" width="{z.w}" height="{z.h}" rx="8" fill="{PAPER2}" fill-opacity="0.6" '
                f'stroke="{RULE}" stroke-width="1"/>'
            )
            out.append(
                f'<text x="{z.x + 16}" y="{z.y + 22}" fill="{SOFT}" font-size="8" font-family="\'Geist Mono\', monospace" '
                f'letter-spacing="0.14em">{esc(z.label.upper())}</text>'
            )
        # edges, then labels
        labels = []
        for e in self.edges:
            pts = self._points(e)
            color, marker = EDGE_COLORS[e.style]
            dash = ' stroke-dasharray="5,4"' if e.dashed else ""
            out.append(
                f'<path d="{self._path(pts)}" fill="none" stroke="{color}" stroke-width="1.4"{dash} marker-end="url(#{marker})"/>'
            )
            if e.label:
                segs = list(zip(pts[:-1], pts[1:]))
                if e.label_seg is not None:
                    seg = segs[e.label_seg]
                else:
                    seg = max(segs, key=lambda s: abs(s[1][0] - s[0][0]) + abs(s[1][1] - s[0][1]))
                labels.append(self._label(e.label, seg, e.label_side))
        out.extend(labels)
        # nodes
        for n in self.nodes:
            out.append(self._node(n))
        for (x, y, t) in self.notes:
            out.append(
                f'<text x="{x}" y="{y}" fill="{MUTED}" font-size="16" font-style="italic" '
                f'font-family="\'Instrument Serif\', serif">{esc(t)}</text>'
            )
        # legend
        kinds = []
        for n in self.nodes:
            if n.kind not in kinds:
                kinds.append(n.kind)
        styles = []
        for e in self.edges:
            key = ("dashed" if e.dashed else e.style)
            if key not in styles:
                styles.append(key)
        ly = hgt - 36
        out.append(f'<line x1="40" y1="{ly - 16}" x2="{W - 40}" y2="{ly - 16}" stroke="{RULE}" stroke-width="0.8"/>')
        out.append(
            f'<text x="40" y="{ly + 4}" fill="{MUTED}" font-size="8" font-family="\'Geist Mono\', monospace" letter-spacing="0.14em">LEGEND</text>'
        )
        lx = 120
        for k in kinds:
            fill, stroke, dash = KINDS[k]
            dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
            out.append(f'<rect x="{lx}" y="{ly - 6}" width="20" height="12" rx="2" fill="{fill}" stroke="{stroke}"{dash_attr}/>')
            out.append(
                f'<text x="{lx + 28}" y="{ly + 4}" fill="{MUTED}" font-size="10" font-family="\'Geist\', sans-serif">{LEGEND_NAMES[k]}</text>'
            )
            lx += 40 + 7 * len(LEGEND_NAMES[k])
        names = {"default": "Flow", "accent": "Key path", "link": "ROS 2 / network", "dashed": "Optional / async"}
        for st in styles:
            color = {"default": MUTED, "accent": ACCENT, "link": LINK, "dashed": MUTED}[st]
            marker = {"default": "arrow", "accent": "arrow-accent", "link": "arrow-link", "dashed": "arrow"}[st]
            dash = ' stroke-dasharray="5,4"' if st == "dashed" else ""
            out.append(
                f'<line x1="{lx}" y1="{ly}" x2="{lx + 28}" y2="{ly}" stroke="{color}" stroke-width="1.4"{dash} marker-end="url(#{marker})"/>'
            )
            out.append(
                f'<text x="{lx + 36}" y="{ly + 4}" fill="{MUTED}" font-size="10" font-family="\'Geist\', sans-serif">{names[st]}</text>'
            )
            lx += 48 + 7 * len(names[st])
        out.append("</svg>")
        return "\n".join(out)

    def _label(self, text: str, seg, side: str) -> str:
        (x0, y0), (x1, y1) = seg
        tw = 7.4 * len(text) + 12
        th = 16
        if abs(y1 - y0) < 0.5:  # horizontal segment: mask above (or below) with 8px gap
            cx = (x0 + x1) / 2
            ry = y0 - 8 - th if side == "above" else y0 + 8
            return (
                f'<rect x="{cx - tw / 2:.1f}" y="{ry:.1f}" width="{tw:.1f}" height="{th}" rx="2" fill="{PAPER}"/>'
                f'<text x="{cx:.1f}" y="{ry + 12:.1f}" fill="{SOFT}" font-size="12" font-family="\'Geist Mono\', monospace" '
                f'text-anchor="middle" letter-spacing="0.04em">{esc(text)}</text>'
            )
        cy = (y0 + y1) / 2
        rx = x0 + 8 if side != "left" else x0 - 8 - tw
        return (
            f'<rect x="{rx:.1f}" y="{cy - th / 2:.1f}" width="{tw:.1f}" height="{th}" rx="2" fill="{PAPER}"/>'
            f'<text x="{rx + tw / 2:.1f}" y="{cy + 4:.1f}" fill="{SOFT}" font-size="12" font-family="\'Geist Mono\', monospace" '
            f'text-anchor="middle" letter-spacing="0.04em">{esc(text)}</text>'
        )

    def _node(self, n: Node) -> str:
        fill, stroke, dash = KINDS[n.kind]
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        cx = n.x + n.w / 2
        parts = [
            f'<rect x="{n.x}" y="{n.y}" width="{n.w}" height="{n.h}" rx="6" fill="{PAPER}"/>',
            f'<rect x="{n.x}" y="{n.y}" width="{n.w}" height="{n.h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1"{dash_attr}/>',
        ]
        lines = [s for s in (n.sub, n.sub2) if s]
        block = 18 + 16 * len(lines)
        top = n.y + n.h / 2 - block / 2 + 14
        if n.tag:
            tw = 7 * len(n.tag) + 10
            parts.append(
                f'<rect x="{n.x + 8}" y="{n.y + 7}" width="{tw}" height="13" rx="2" fill="none" stroke="{stroke}" stroke-opacity="0.45" stroke-width="0.8"/>'
                f'<text x="{n.x + 8 + tw / 2}" y="{n.y + 16.5}" fill="{stroke}" fill-opacity="0.85" font-size="8" '
                f'font-family="\'Geist Mono\', monospace" text-anchor="middle" letter-spacing="0.08em">{esc(n.tag)}</text>'
            )
            top += 5
        parts.append(
            f'<text x="{cx}" y="{top:.1f}" fill="{INK}" font-size="16" font-weight="600" '
            f'font-family="\'Geist\', sans-serif" text-anchor="middle">{esc(n.name)}</text>'
        )
        for i, s in enumerate(lines):
            parts.append(
                f'<text x="{cx}" y="{top + 19 + 16 * i:.1f}" fill="{MUTED}" font-size="12" '
                f'font-family="\'Geist Mono\', monospace" text-anchor="middle">{esc(s)}</text>'
            )
        return "\n".join(parts)

    # ------------------------------------------------------------------ files
    def page(self) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(self.title)}</title>
<link href="{FONTS}" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Geist', system-ui, sans-serif; background: {PAPER}; color: {INK};
       display: flex; justify-content: center; padding: 3rem 2rem; }}
.frame {{ max-width: 1280px; width: 100%; }}
.eyebrow {{ font-family: 'Geist Mono', monospace; font-size: 0.66rem; font-weight: 500; letter-spacing: 0.18em;
           text-transform: uppercase; color: {MUTED}; margin-bottom: 0.5rem; }}
h1 {{ font-family: 'Instrument Serif', serif; font-size: 2rem; font-weight: 400; letter-spacing: -0.02em;
     margin-bottom: 1.5rem; }}
svg {{ width: 100%; min-width: 900px; display: block; }}
.colophon {{ font-family: 'Geist Mono', monospace; font-size: 0.66rem; color: {SOFT}; margin-top: 1rem;
            border-top: 1px solid {RULE}; padding-top: 0.75rem; }}
</style>
</head>
<body>
<div class="frame">
<p class="eyebrow">{esc(self.eyebrow)}</p>
<h1>{esc(self.title)}</h1>
{self.svg()}
<p class="colophon">Isaac Sim 6.1 learning resource · learning_resource/diagrams/{self.slug}.html</p>
</div>
</body>
</html>
"""

    def frame_page(self) -> str:
        """SVG only, sized for a 2x PNG."""
        return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><link href="{FONTS}" rel="stylesheet">
<style>html,body{{margin:0;padding:0;background:{PAPER}}} svg{{display:block;width:{W * 2}px;height:{self.height * 2}px}}</style>
</head><body>{self.svg()}</body></html>"""

    def write(self, out_dir: str, png: bool = True) -> str:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"{self.slug}.html")
        with open(path, "w") as f:
            f.write(self.page())
        if png:
            render_png(self.frame_page(), os.path.join(out_dir, f"{self.slug}.png"), W * 2, self.height * 2)
        return path


def render_png(page_html: str, png_path: str, width: int, height: int) -> None:
    tmp = png_path + ".frame.html"
    with open(tmp, "w") as f:
        f.write(page_html)
    subprocess.run(
        [
            "google-chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-sandbox",
            f"--window-size={width},{height}", "--virtual-time-budget=8000",
            f"--screenshot={os.path.abspath(png_path)}", "file://" + os.path.abspath(tmp),
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    os.remove(tmp)
