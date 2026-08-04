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
competitor — the legend says so explicitly.

Usage:  python3 tools/plot_validation.py [out.svg]
   or:  python3 -m tools.plot_validation [out.svg]
"""
import csv
import os
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
# "regenerate the figure" with unchanged data is actually a no-op diff —
# see the metadata={"Date": None} in main() for the other source of
# run-to-run bytes (an embedded generation timestamp).
matplotlib.rcParams["svg.hashsalt"] = "3dplam-validation-figure"
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402

# Make the repository root importable so this file works both as a script
# (python3 tools/plot_validation.py) and as a module (python3 -m tools.…).
# Without this, direct script invocation fails with ModuleNotFoundError
# because tools/ — not the repo root — is what lands on sys.path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.risk import BANDS, THRESHOLDS  # noqa: E402

DEFAULT_OUT = "site/public/figures/validation.svg"
QUANTIFICATION_CSV = "data/ecoli-quantification.csv"
SUMMARY_CSV = "data/ecoli-summary.csv"

# Three stops from matplotlib's viridis colormap — perceptually uniform
# and colour-blind safe, which suits a scientific figure better than an
# arbitrary brand palette. Stops are taken from the dark half of the
# range (t=0.05, 0.30, 0.55) because viridis's top end is a bright
# yellow-green with poor contrast on white; all three chosen colours
# still clear WCAG's 3:1 minimum contrast ratio against white
# (13.53:1, 6.64:1 and 3.41:1 respectively — see the report for the
# derivation) while staying visually distinguishable from one another.
COLOURS = {"ft1": "#471365", "ft2": "#355f8d", "ft3": "#1e9c89"}

# ft3 is the commercial reference the two printed manifolds are checked
# against, not a third competitor being compared on equal footing — the
# label says so rather than leaving a reader to infer it.
LABELS = {
    "ft1": "3DPLAM (rPET, printed base + filter support, commercial funnel)",
    "ft2": "3DPLAM (ABS, fully printed incl. funnel)",
    "ft3": "Millipore EZ-Fit (steel, reference instrument)",
}
ORDER = ["ft1", "ft2", "ft3"]

# Ink colour optimized for white background (light mode primary design target).
# In dark theme, the figure sits on a white card via CSS, keeping text legible.
INK = "#3d444d"           # axis text, ticks, spines, titles, legend, footnote
GRID = "#9aa3ad"          # WHO threshold lines
BAND_FILL = "#8f97a3"     # risk-band shading (opacity increases with risk)
BAND_ALPHAS = [0.05, 0.10, 0.16, 0.22]
MISMATCH = "#d68a1d"      # the one classification that does not agree

# Sample 5's filtration stalled partway through and sample 7 is a spiked
# positive control, not a field sample — both need a flag on the figure
# itself (data/README.md carries the full explanation).
NOTES = {"5": "†", "7": "‡"}
FOOTNOTE = (
    "† sample 5: filtration stalled at roughly the 20 mL mark of the "
    "100 mL sample — counts reflect ~80 mL filtered, not the full volume.   "
    "‡ sample 7: tap water spiked with horse faecal suspension as a "
    "positive control, not a field sample — and (▲, below) the one "
    "case where a printed manifold's risk classification did not match the "
    "reference even with the 5% boundary-tolerance rule applied."
)

YMIN, YMAX = 0.3, 1500

# Display-label translations for the figure only — a presentation-layer
# mapping, not a change to the underlying data. Descriptive German words
# are translated to English for this English-language figure; genuine
# proper place names (Platzspitz, Rentenwiese) are left exactly as
# collected because they are not descriptive words to translate. Keyed on
# the tail string short_site() extracts (the part after the last comma
# in each CSV sample_site value), so data/*.csv itself is never touched.
SITE_LABEL_TRANSLATIONS = {
    "Treppen bei der Sihl": "Sihl riverside steps",
    "Aussichtspunkt Riesbach": "Riesbach viewpoint",
    "Ircheltuempel": "Irchel pond",
    "Resi-Weiher": "Resi pond",
}


def load(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def short_site(site):
    """The distinguishing part of a sample-site description, word-wrapped.

    Sites 1-6 are "River/lake, specific spot" — the text after the comma
    is what tells them apart. Sites 7-8 are ETH lab controls where the
    same wrap still works ("tap water ..."); NOTES/FOOTNOTE already carry
    the spiked/partial-filtration caveats so this label does not repeat
    them.
    """
    tail = site.split(",")[-1].strip()
    tail = SITE_LABEL_TRANSLATIONS.get(tail, tail)
    return "\n".join(textwrap.wrap(tail, width=18, break_long_words=False)[:2])


def style_axis(ax):
    ax.set_yscale("log")
    ax.set_ylim(YMIN, YMAX)
    ax.set_ylabel("CFU / 100 mL", color=INK, fontsize=9.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["left"].set_color(INK)
    ax.spines["bottom"].set_color(INK)
    ax.tick_params(colors=INK, labelsize=8.5)


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
        ax.text(1.012, y, name, transform=trans, va="center", fontsize=7.2,
                color=INK, alpha=0.85)


def main(out_path=DEFAULT_OUT):
    measurements = load(QUANTIFICATION_CSV)
    summary = load(SUMMARY_CSV)
    samples = sorted({m["sample_no"] for m in measurements}, key=int)
    x = np.arange(len(samples))

    # The single classification that disagrees with the reference even
    # after the 5% boundary-tolerance rule — computed from the data, not
    # hardcoded, so this stays true if the dataset is ever regenerated.
    hard_mismatches = {
        (r["manifold_id"], r["sample_no"])
        for r in summary
        if r["is_reference"] == "no" and r["acceptable_within_5pct"] == "no"
    }

    fig, (top, bot) = plt.subplots(
        2, 1, figsize=(11, 8.6), dpi=150, sharex=True,
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
                # across regenerations of the same data.
                xs.append(si + offset + (ri - 1) * 0.045)
                ys.append(float(m["cfu_per_100ml"]))
        top.scatter(xs, ys, s=24, color=COLOURS[mid], label=LABELS[mid],
                    alpha=0.9, edgecolors="none", zorder=3)
    top.legend(frameon=False, ncol=1, loc="upper left", fontsize=12,
               labelcolor=INK, handletextpad=0.5, borderaxespad=0.3)
    top.set_title("Individual plate counts (3 replicates × manifold × site)",
                  loc="left", fontsize=10.5, color=INK)

    # --- bottom panel: geometric means as grouped bars -------------------
    width = 0.27
    for i, mid in enumerate(ORDER):
        vals = [next(float(r["geometric_mean"]) for r in summary
                     if r["manifold_id"] == mid and r["sample_no"] == s)
                for s in samples]
        xs = x + (i - 1) * width
        bot.bar(xs, vals, width, bottom=YMIN, color=COLOURS[mid],
                label=LABELS[mid], zorder=3)
        for xi, s, v in zip(xs, samples, vals):
            if (mid, s) in hard_mismatches:
                bot.plot(xi, v * 1.35, marker="^", color=MISMATCH,
                         markersize=7, zorder=4)
    bot.set_title("Geometric mean per manifold", loc="left", fontsize=10.5,
                  color=INK)

    labels = []
    for s in samples:
        site = next(r["sample_site"] for r in summary if r["sample_no"] == s)
        mark = NOTES.get(s, "")
        labels.append(f"{s}{mark}\n{short_site(site)}")
    bot.set_xticks(x)
    bot.set_xticklabels(labels, rotation=0, ha="center", fontsize=8, color=INK)
    bot.tick_params(axis="x", length=0)

    fig.suptitle(
        "E. coli validation — 3DPLAM (rPET, ABS) vs Millipore EZ-Fit "
        "reference, 8 sites × 3 manifolds × 3 replicates",
        fontsize=12, color=INK, x=0.01, ha="left", y=0.995)
    fig.text(0.01, 0.012, FOOTNOTE, fontsize=7.3, color=INK, ha="left",
             va="bottom", wrap=True)

    fig.tight_layout(rect=(0, 0.045, 1, 0.965))
    dirname = os.path.dirname(out_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    fig.savefig(out_path, transparent=True, metadata={"Date": None})
    plt.close(fig)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT))
