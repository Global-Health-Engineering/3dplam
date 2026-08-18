#!/usr/bin/env python3
"""Regenerate the validation figure from the tidy datasets.

Top panel:    individual plate counts, log y-axis, WHO risk bands shaded.
Bottom panel: geometric means as grouped bars, same log axis and bands, so
              a reader can trace one sample from its raw replicates above
              to its manifold-level summary below.

Samples 5 and 7 needed non-standard handling during collection (see NOTES
below) and are flagged in the figure so it does not mislead. ft3 is the
commercial Millipore EZ-Fit reference instrument the two 3D-printed
manifolds (ft1 rPET, ft2 ABS) are validated against, not a third
competitor; the legend says so explicitly.

Usage:  python3 tools/plot_validation.py [out.svg]
   or:  python3 -m tools.plot_validation [out.svg]
"""
import csv
import os
import re
import sys
import textwrap

import matplotlib

matplotlib.use("Agg")
# Keep text as real <text> elements rather than vector outlines (the
# matplotlib default for the SVG backend). This keeps the file small and
# its labels selectable/searchable in a browser, and it is what lets this
# script's own verification step (see the report) grep the output for
# site and manifold names instead of trusting the plotting code blindly.
matplotlib.rcParams["svg.fonttype"] = "none"
# matplotlib salts every clip-path/gid it emits with uuid.uuid4() by
# default, so two runs over identical data produce byte-different SVGs.
# svg.hashsalt swaps that per-run randomness for a fixed string, so
# "regenerate the figure" with unchanged data is actually a no-op diff,
# see the metadata={"Date": None} in main() for the other source of
# run-to-run bytes (an embedded generation timestamp).
matplotlib.rcParams["svg.hashsalt"] = "3dplam-validation-figure"
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402

# Make the repository root importable so this file works both as a script
# (python3 tools/plot_validation.py) and as a module (python3 -m tools.…).
# Without this, direct script invocation fails with ModuleNotFoundError
# because tools/ (not the repo root) is what lands on sys.path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.risk import BANDS, THRESHOLDS  # noqa: E402

DEFAULT_OUT = "site/public/figures/validation.svg"
QUANTIFICATION_CSV = "data/ecoli-quantification.csv"
SUMMARY_CSV = "data/ecoli-summary.csv"

# Character-for-character the `--sans` stack in site/src/styles/global.css,
# so the figure's labels are set in the same face as the page's body copy
# instead of matplotlib's DejaVu Sans. Every entry is a system font or a
# generic: the page embeds this SVG with <img src=…>, and an <img>-embedded
# SVG is an independent document that cannot reach the parent page's CSS or
# load a webfont, so a stack that depended on one would silently fall back.
# Keep this in sync with global.css if that stack ever changes.
SITE_FONT_STACK = (
    "ui-sans-serif, system-ui, -apple-system, 'Inter', 'Segoe UI', sans-serif"
)

# matplotlib's SVG backend emits shorthand `font: <size>px <family list>`
# inside a style attribute; nothing else in the file matches this shape.
_FONT_SHORTHAND = re.compile(r"(font: [\d.]+px )[^;\"]+")


def retarget_font_family(path):
    """Rewrite every font declaration in `path` to SITE_FONT_STACK.

    Deliberately a post-processing pass rather than an rcParams change:
    matplotlib measures text with a font it can actually load, and those
    measurements drive tight_layout's margins, the legend box and the
    wrapped footnote. Naming the site stack in rcParams would not give it
    those fonts to measure with (`system-ui` is a CSS generic, not a font
    file), so it would fall back to DejaVu for metrics anyway, and on a
    machine that happened to have "Inter" installed it would silently
    measure with a *different* font than on one that did not, making the
    committed SVG depend on the author's font book.

    Leaving the metrics on DejaVu Sans keeps the file reproducible on any
    machine, and errs in the safe direction: DejaVu is wider than the UI
    sans fonts this stack resolves to, so the rendered text comes out
    slightly narrower than the space reserved for it, never wider.
    """
    with open(path, encoding="utf-8") as f:
        svg = f.read()
    svg, n = _FONT_SHORTHAND.subn(rf"\g<1>{SITE_FONT_STACK}", svg)
    if not n:
        raise SystemExit(
            f"{path}: no font declarations found to retarget, matplotlib's "
            "SVG output format has changed, so the figure would silently ship "
            "in DejaVu Sans. Update _FONT_SHORTHAND.")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return n

# Three stops from matplotlib's viridis colormap, perceptually uniform
# and colour-blind safe, which suits a scientific figure better than an
# arbitrary brand palette. Stops are taken from the dark half of the
# range (t=0.05, 0.30, 0.55) because viridis's top end is a bright
# yellow-green with poor contrast on white; all three chosen colours
# still clear WCAG's 3:1 minimum contrast ratio against white
# (13.53:1, 6.64:1 and 3.41:1 respectively; see the report for the
# derivation) while staying visually distinguishable from one another.
COLOURS = {"ft1": "#471365", "ft2": "#355f8d", "ft3": "#1e9c89"}

# ft3 is the commercial reference the two printed manifolds are checked
# against, not a third competitor being compared on equal footing, the
# label says so rather than leaving a reader to infer it.
LABELS = {
    "ft1": "3DPLAM (rPET, printed base + filter support, commercial funnel)",
    "ft2": "3DPLAM (ABS, fully printed incl. funnel)",
    "ft3": "Millipore EZ-Fit (steel, reference instrument)",
}
ORDER = ["ft1", "ft2", "ft3"]

# The legend spells each manifold out in full; a hover readout has no room
# for that and the reader has already met the long form.
SHORT_LABELS = {
    "ft1": "3DPLAM (rPET)",
    "ft2": "3DPLAM (ABS)",
    "ft3": "Millipore EZ-Fit",
}

# Ink colour optimized for the white background the site always uses (the
# page is light-only; there is no dark theme to also satisfy).
INK = "#3d444d"           # axis text, ticks, spines, titles, legend, footnote
GRID = "#9aa3ad"          # WHO threshold lines
BAND_FILL = "#8f97a3"     # risk-band shading (opacity increases with risk)
BAND_ALPHAS = [0.05, 0.10, 0.16, 0.22]
MISMATCH = "#d68a1d"      # the one classification that does not agree
MARKER_EDGE = "#000000"   # outline on every plotted marker

# Type sizes, in points, against the FIG_W × FIG_H figure below. Only the
# ratio to FIG_W matters on screen: the site displays this SVG scaled to
# fit its 800 px content column, so a 10.5 in figure is shown at ~760 px
# and every point here renders at ~0.75 CSS px × 96/72 ≈ 1 px. Sizes are
# chosen against the page's 16 px body copy, tick labels land near 13 px
# and the footnote near 11 px, where before they were 8 px and 7 px and
# were the smallest type on the page by a wide margin.
FS_SUPTITLE = 18
FS_PANEL_TITLE = 15.5
FS_AXIS_LABEL = 15
FS_TICK = 13.5
FS_XTICK = 11.5
FS_LEGEND = 14
FS_BAND = 11.5
FS_FOOTNOTE = 11

FIG_W, FIG_H = 10.5, 9.0

# Sample 5's filtration stalled partway through and sample 7 is a spiked
# positive control, not a field sample, both need a flag on the figure
# itself (data/README.md carries the full explanation).
NOTES = {"5": "†", "7": "‡"}
FOOTNOTE = (
    "† sample 5: filtration stalled at roughly the 20 mL mark of the "
    "100 mL sample: counts reflect ~80 mL filtered, not the full volume.   "
    "‡ sample 7: tap water spiked with horse faecal suspension as a "
    "positive control, not a field sample. It is also (▲, below) the one "
    "case where a printed manifold's risk classification did not match the "
    "reference even with the 5 % boundary-tolerance rule applied."
)

# YMAX is headroom, not data range: the highest count in the dataset is
# ~120 CFU/100 mL. The extra decade above it is what the in-axes legend
# occupies, at the larger FS_LEGEND its three rows need about a third of
# the panel height, and at the old 1500 ceiling the bottom row grazed the
# sample-5 markers.
YMIN, YMAX = 0.3, 2500

def load(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def short_site(site):
    """The distinguishing part of a sample-site description, word-wrapped.

    Most sites are "River/lake, specific spot", the text after the comma
    is what tells them apart. Sites 7-8 are ETH lab controls where the
    same wrap still works ("tap water ..."); NOTES/FOOTNOTE already carry
    the spiked/partial-filtration caveats so this label does not repeat
    them. A value with no comma (site 2) is used whole.

    The names arrive already in English. This function used to also hold
    a German-to-English lookup, which is gone: the translation now happens
    once, in tools/tidy_data.py, so the CSVs, the codebook, data/README.md
    and this figure all read the same name for a site.

    The wrap width and the line cap are tied to FS_XTICK: eight labels
    share the panel width, so a line longer than ~12 characters at that
    type size runs into its neighbour. The cap is 3 lines rather than 2
    because the narrower wrap pushes the longest labels ("tap water +
    fecal suspension") onto a third line; a lower cap would silently
    truncate them.
    """
    tail = site.split(",")[-1].strip()
    return "\n".join(textwrap.wrap(tail, width=12, break_long_words=False)[:3])


def style_axis(ax):
    ax.set_yscale("log")
    ax.set_ylim(YMIN, YMAX)
    ax.set_ylabel("CFU / 100 mL", color=INK, fontsize=FS_AXIS_LABEL)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["left"].set_color(INK)
    ax.spines["bottom"].set_color(INK)
    ax.tick_params(colors=INK, labelsize=FS_TICK)


def shade_bands(ax, label=False):
    """Shade the 4 WHO risk bands and mark their boundaries.

    Shading uses one neutral grey at increasing opacity (never a hue) so
    it reads as background structure, not a fourth data series, on both a
    light and a dark page.
    """
    n = len(BANDS)
    for i, (name, lo, hi) in enumerate(BANDS):
        lo = YMIN if lo <= 0 else lo
        hi = YMAX if i == n - 1 else hi
        ax.axhspan(lo, hi, color=BAND_FILL, alpha=BAND_ALPHAS[i], lw=0, zorder=0)
    for t in THRESHOLDS:
        ax.axhline(t, color=GRID, lw=0.8, ls=(0, (1, 2.2)), zorder=1)
    if not label:
        return
    trans = blended_transform_factory(ax.transAxes, ax.transData)
    for i, (name, lo, hi) in enumerate(BANDS):
        lo = YMIN if lo <= 0 else lo
        hi = YMAX if i == n - 1 else hi
        y = (lo * hi) ** 0.5  # geometric centre of the band, log-scale-correct
        ax.text(1.012, y, name, transform=trans, va="center",
                fontsize=FS_BAND, color=INK, alpha=0.85)


# --- hover layer ---------------------------------------------------------
#
# The published SVG is inlined into the page (see Performance.astro), which
# is what lets it respond to a pointer at all: an <img>-embedded SVG is an
# inert picture, so no amount of markup inside it would ever fire an event.
#
# matplotlib draws no hit targets of its own, and its painted marks are far
# too small to aim at (a point is ~8 pt across). So each mark's position is
# measured here, at plot time, and written out afterwards as a transparent
# shape in a layer of its own. Two things fall out of doing it this way:
# the hit target can be as large as it needs to be (24 pt across for a
# point, per the interaction spec) without changing how the figure looks,
# and the values ride along in data attributes, so the page needs no second
# request and no copy of the dataset.
HIT_RADIUS_PT = 12.0

# Marks are located in figure-relative coordinates (0..1 on each axis)
# rather than pixels. That is deliberate: matplotlib renders SVG at 72 dpi
# regardless of the figure's own dpi setting, so a pixel measurement taken
# here would be wrong by the ratio of the two. A fraction of the figure is
# the same number in both.
def fig_fraction(fig, ax, x, y):
    """Data coordinates to figure fraction, origin bottom left."""
    return fig.transFigure.inverted().transform(ax.transData.transform((x, y)))


def to_svg_xy(frac, w_pt, h_pt):
    """Figure fraction to SVG user units, origin top left."""
    return frac[0] * w_pt, (1.0 - frac[1]) * h_pt


def esc(text):
    """Escape for an XML attribute value."""
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def inject_hit_layer(path, hits, w_pt, h_pt):
    """Append the transparent hover targets to the finished SVG.

    Every shape carries a <title> as well as its data attributes: with
    JavaScript unavailable the browser still shows the title natively, so
    the figure degrades to a slower tooltip rather than to nothing.
    """
    parts = ['<g id="figure-hits" fill="none" pointer-events="all">']
    for h in hits:
        attrs = (f'class="hit hit-{h["kind"]}" '
                 f'data-value="{esc(h["value"])}" '
                 f'data-label="{esc(h["label"])}" '
                 f'data-detail="{esc(h["detail"])}"')
        title = f'<title>{esc(h["label"])}: {esc(h["value"])}</title>'
        if h["kind"] == "point":
            parts.append(
                f'<circle cx="{h["cx"]:.2f}" cy="{h["cy"]:.2f}" '
                f'r="{HIT_RADIUS_PT:.2f}" {attrs}>{title}</circle>')
        else:
            parts.append(
                f'<rect x="{h["x"]:.2f}" y="{h["y"]:.2f}" '
                f'width="{h["w"]:.2f}" height="{h["h"]:.2f}" '
                f'{attrs}>{title}</rect>')
    parts.append("</g>")
    layer = "\n".join(parts) + "\n</svg>"

    with open(path, encoding="utf-8") as f:
        svg = f.read()
    if "</svg>" not in svg:
        raise SystemExit(f"{path}: no closing </svg> to insert the hit layer before.")
    svg = svg.replace("</svg>", layer)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return len(hits)


def main(out_path=DEFAULT_OUT):
    measurements = load(QUANTIFICATION_CSV)
    summary = load(SUMMARY_CSV)
    samples = sorted({m["sample_no"] for m in measurements}, key=int)
    x = np.arange(len(samples))

    # The single classification that disagrees with the reference even
    # after the 5 % boundary-tolerance rule, computed from the data, not
    # hardcoded, so this stays true if the dataset is ever regenerated.
    hard_mismatches = {
        (r["manifold_id"], r["sample_no"])
        for r in summary
        if r["is_reference"] == "no" and r["acceptable_within_5pct"] == "no"
    }

    site_of = {r["sample_no"]: r["sample_site"] for r in summary}
    gm_of = {(r["manifold_id"], r["sample_no"]): r["geometric_mean"]
             for r in summary}
    # Collected while plotting, written into the SVG afterwards.
    hits = []

    fig, (top, bot) = plt.subplots(
        2, 1, figsize=(FIG_W, FIG_H), dpi=150, sharex=True,
        gridspec_kw={"height_ratios": [1.15, 1]})
    fig.patch.set_alpha(0.0)

    for ax in (top, bot):
        style_axis(ax)
    shade_bands(top, label=True)
    shade_bands(bot, label=True)

    # --- top panel: individual replicates, dodged per manifold ----------
    for i, mid in enumerate(ORDER):
        offset = (i - 1) * 0.24
        xs, ys = [], []
        for si, sample in enumerate(samples):
            reps = [m for m in measurements
                    if m["manifold_id"] == mid and m["sample_no"] == sample]
            reps.sort(key=lambda m: m["replicate"])
            for ri, m in enumerate(reps):
                # A small deterministic spread across the 3 replicates
                # (not random jitter) keeps the figure byte-identical
                # across regenerations of the same data. The spread is
                # sized against the marker: at s=64 a point is ~8 pt
                # across and 0.06 data units is ~5 pt here, so replicates
                # read as a tight triplet that still stays clear of the
                # neighbouring manifold's group 0.24 units away.
                px = si + offset + (ri - 1) * 0.06
                py = float(m["cfu_per_100ml"])
                xs.append(px)
                ys.append(py)
                hits.append({
                    "kind": "point", "ax": top, "x": px, "y": py,
                    "value": f"{m['cfu_per_100ml']} CFU/100 mL",
                    "label": SHORT_LABELS[mid],
                    "detail": (f"Site {sample}, {site_of[sample]} "
                               f"(replicate {m['replicate']})"),
                })
        # Black outline keeps each point readable where the three viridis
        # stops overlap, and against the shaded risk bands behind them.
        top.scatter(xs, ys, s=64, color=COLOURS[mid], label=LABELS[mid],
                    alpha=0.9, edgecolors=MARKER_EDGE, linewidths=0.7,
                    zorder=3)
    top.legend(frameon=False, ncol=1, loc="upper left", fontsize=FS_LEGEND,
               labelcolor=INK, handletextpad=0.5, borderaxespad=0.3)
    top.set_title("Individual plate counts (3 replicates × manifold × site)",
                  loc="left", fontsize=FS_PANEL_TITLE, color=INK)

    # --- bottom panel: geometric means as grouped bars -------------------
    width = 0.27
    for i, mid in enumerate(ORDER):
        vals = [next(float(r["geometric_mean"]) for r in summary
                     if r["manifold_id"] == mid and r["sample_no"] == s)
                for s in samples]
        xs = x + (i - 1) * width
        bars = bot.bar(xs, vals, width, bottom=YMIN, color=COLOURS[mid],
                       label=LABELS[mid], edgecolor=MARKER_EDGE,
                       linewidth=0.7, zorder=3)
        for rect, xi, s, v in zip(bars, xs, samples, vals):
            reps = sorted(
                (r for r in measurements
                 if r["manifold_id"] == mid and r["sample_no"] == s),
                key=lambda r: r["replicate"])
            shown = ", ".join(r["cfu_per_100ml"] for r in reps)
            hits.append({
                "kind": "bar", "ax": bot, "rect": rect,
                "value": f"{gm_of[(mid, s)]} CFU/100 mL",
                "label": f"{SHORT_LABELS[mid]}, geometric mean",
                "detail": (f"Site {s}, {site_of[s]}. "
                           f"Replicates: {shown} CFU/100 mL"),
            })
            if (mid, s) in hard_mismatches:
                bot.plot(xi, v * 1.4, marker="^", color=MISMATCH,
                         markersize=12, markeredgecolor=MARKER_EDGE,
                         markeredgewidth=0.9, zorder=4)
    bot.set_title("Geometric mean per manifold", loc="left",
                  fontsize=FS_PANEL_TITLE, color=INK)

    labels = []
    for s in samples:
        site = next(r["sample_site"] for r in summary if r["sample_no"] == s)
        mark = NOTES.get(s, "")
        labels.append(f"{s}{mark}\n{short_site(site)}")
    bot.set_xticks(x)
    bot.set_xticklabels(labels, rotation=0, ha="center", fontsize=FS_XTICK,
                        color=INK)
    bot.tick_params(axis="x", length=0)

    # Two lines, not one: at FS_SUPTITLE the single-line version overran
    # the figure width and was clipped by the SVG canvas.
    fig.suptitle(
        "E. coli validation: 3DPLAM (rPET, ABS) vs Millipore EZ-Fit reference\n"
        "8 sites × 3 manifolds × 3 replicates",
        fontsize=FS_SUPTITLE, color=INK, x=0.01, ha="left", y=0.995,
        va="top")
    fig.text(0.01, 0.012, FOOTNOTE, fontsize=FS_FOOTNOTE, color=INK,
             ha="left", va="bottom", wrap=True)

    # Only the bottom margin is reserved by hand, for the wrapped footnote
    # (a free-floating fig.text that tight_layout does not measure). The
    # top stays at 1.0 because tight_layout already subtracts the
    # suptitle's own height; reserving for it here too left a visible band
    # of empty space between the title and the first panel.
    fig.tight_layout(rect=(0, 0.085, 1, 1.0))
    dirname = os.path.dirname(out_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    # Positions are read only now: tight_layout has moved both axes since
    # the marks were drawn, so anything measured earlier would be stale.
    fig.canvas.draw()
    w_pt, h_pt = FIG_W * 72.0, FIG_H * 72.0
    for h in hits:
        if h["kind"] == "point":
            h["cx"], h["cy"] = to_svg_xy(
                fig_fraction(fig, h["ax"], h["x"], h["y"]), w_pt, h_pt)
        else:
            rect = h["rect"]
            x0, y0 = to_svg_xy(fig_fraction(
                fig, h["ax"], rect.get_x(), rect.get_y()), w_pt, h_pt)
            x1, y1 = to_svg_xy(fig_fraction(
                fig, h["ax"], rect.get_x() + rect.get_width(),
                rect.get_y() + rect.get_height()), w_pt, h_pt)
            h["x"], h["w"] = min(x0, x1), abs(x1 - x0)
            h["y"], h["h"] = min(y0, y1), abs(y1 - y0)

    fig.savefig(out_path, transparent=True, metadata={"Date": None})
    plt.close(fig)
    if out_path.lower().endswith(".svg"):
        n = retarget_font_family(out_path)
        k = inject_hit_layer(out_path, hits, w_pt, h_pt)
        print(f"wrote {out_path} ({n} font declarations set to the site "
              f"stack, {k} hover targets)")
    else:
        # A raster preview bakes in whatever font matplotlib measured with,
        # so it cannot carry the site stack, only the shipped SVG can.
        print(f"wrote {out_path} (raster: font is matplotlib's, not the site's)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT))
