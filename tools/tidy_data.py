#!/usr/bin/env python3
"""Convert the handover spreadsheets into tidy, documented CSVs.

Handover files are semicolon-delimited with a UTF-8 BOM. The E. coli file is
in wide format with one block of five columns per sample site, plus a
derived summary row that is not data.

Usage:  python3 tools/tidy_data.py
   or:  python3 -m tools.tidy_data
"""
import csv
import os
import re
import sys

# Make the repository root importable so this file works both as a script
# (python3 tools/tidy_data.py) and as a module (python3 -m tools.…).
# Without this, direct script invocation fails with ModuleNotFoundError
# because tools/ (not the repo root) is what lands on sys.path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.risk import geometric_mean, classify, is_acceptable  # noqa: E402

HANDOVER = "../2026-bsc-thesis-mgabri/data/raw_data/tables (csv)"

# Sample-site descriptions, from the handover README's "Sample List"
# (data/raw_data/tables (csv)/Functional Testing/
# E. coli Quantification_README.txt). Keys are the sample numbers used as
# column-name prefixes in the source spreadsheet (e.g. "1_Platzspitz_a").
#
# These are given in English. The handover names four sites with German
# descriptive words; those are translated here, at the one point where the
# published CSVs are generated, so that every artifact downstream
# (the CSVs, data/README.md, the codebook and the validation figure) carries
# one name per site and no translation layer of its own. The figure used
# to hold a second, private mapping to do this at plot time; it does not
# any more.
#
# Only descriptive words are translated. Genuine proper place names are
# left exactly as collected, because they are names rather than words:
# Platzspitz and Rentenwiese stay, and "Resi-Weiher" keeps Resi while
# -Weiher (pond) is translated. The German original of each translated
# name is recorded here so the published value can always be traced back
# to the handover:
#
#     2  Treppen bei der Sihl      -> Sihl riverside steps
#     4  Aussichtspunkt Riesbach   -> Riesbach viewpoint
#     5  Ircheltuempel             -> Irchel pond
#     6  Resi-Weiher               -> Resi pond
#
# Site 2 is deliberately a single-part name: the German was "Sihl,
# Treppen bei der Sihl", which names the river twice, and "Sihl, Sihl
# riverside steps" would carry that redundancy into English for no gain.
SITES = {
    "1": "Limmat, Platzspitz",
    "2": "Sihl riverside steps",
    "3": "Lake of Zurich, Rentenwiese",
    "4": "Lake of Zurich, Riesbach viewpoint",
    "5": "Irchel Campus, Irchel pond",
    "6": "Zurichberg, Resi pond",
    "7": "ETH Zurich CLD, tap water + fecal suspension",
    "8": "ETH Zurich CLA, tap water",
}

# The Millipore Microfil manifold (steel), the commercial reference device
# the two 3D-printed manifolds (rPET, ABS) are evaluated against.
REFERENCE_ID = "ft3"


# Free text in the handover was typed during testing and carries two
# habits the published CSVs do not: a quantity written hard against its
# unit ("~5min", "34.75mm"), and one misspelled word repeated across the
# three watertightness rows. Both are corrected here, at the point of
# generation, rather than by hand afterwards, so that re-running this
# script reproduces the shipped files instead of undoing the corrections.
# Nothing else about the text changes: wording, capitalisation and the
# measurements themselves pass through exactly as recorded.
#
# The key below is the misspelling as it appears in the source. It has to
# be spelled out to be matched and replaced; it does not reach any
# published file.
SPELLING_FIXES = {"unifrom": "uniform"}

# A space is inserted between a number and the unit that follows it. The
# unit list is explicit and deliberately excludes bare "m" and "s", which
# would match inside part codes and version strings; longer units come
# first so "mm" and "min" are not shortened to a leading "m" match.
_UNIT = re.compile(r"(\d)\s*(mm|min|cm|µm|mL|ml|kg|h|g|%|°C)\b")


def normalise_text(value):
    """Apply the spelling fixes and unit spacing to one field."""
    if not value:
        return value
    for wrong, right in SPELLING_FIXES.items():
        value = value.replace(wrong, right)
        value = value.replace(wrong.capitalize(), right.capitalize())
    return _UNIT.sub(r"\1 \2", value)


# Two heat-resistance rows give a before/after measurement with the unit
# left off the numbers ("decreased from 42.90 to 42.10"), while every
# comparable sentence in the same column writes it out. The unit is not in
# doubt: the column records millimetre dimensions throughout, and the same
# sentence in row hr3.5 continues "from 35.15 mm to 43.10 mm".
#
# Supplying it is an edit to the recorded text, so it is listed here
# explicitly, one entry per change, rather than inferred by a rule that
# would guess units elsewhere too. apply_editorial() fails loudly if an
# entry stops matching, so a future handover revision cannot silently skip
# one of these.
EDITORIAL = [
    ("hr3.4", "decreased from 42.90 to 42.10",
     "decreased from 42.90 mm to 42.10 mm"),
    ("hr3.5", "decreased from 43.15 to 42.50",
     "decreased from 43.15 mm to 42.50 mm"),
]


def apply_editorial(rows):
    """Apply the EDITORIAL corrections, verifying each one lands."""
    applied = set()
    for row in rows:
        row_id = row.get("id")
        for entry_id, old, new in EDITORIAL:
            if row_id != entry_id:
                continue
            for key, value in row.items():
                if value and old in value:
                    row[key] = value.replace(old, new)
                    applied.add(entry_id)
    return applied


def normalise_rows(rows):
    """Normalise every field and every column name in a list of dict rows.

    Column names are included because the handover heads two columns
    "... (2h)" and "... (48h)", which are quantities with units like any
    other and are published as "(2 h)" and "(48 h)".

    Runs of spaces inside free text are collapsed to one; the handover has
    a couple of double spaces from typing, and they are not data.
    """
    out = []
    for row in rows:
        out.append({
            re.sub(r" {2,}", " ", normalise_text(k)):
                re.sub(r" {2,}", " ", normalise_text(v)) if v else v
            for k, v in row.items()
        })
    return out


def read_handover_csv(path):
    """Read a semicolon-delimited, BOM-prefixed handover CSV.

    Decodes with utf-8-sig so a leading BOM is stripped from the first
    header key, then drops rows where every field is blank (the source
    files end in several trailing all-empty rows).
    """
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    return [r for r in rows
            if any((v or "").strip() for v in r.values())]


def tidy_ecoli(path):
    """Return (measurements, summary) for the E. coli dataset.

    measurements: one row per (manifold, sample site, replicate),
    72 rows = 3 manifolds x 8 sites x 3 replicates.
    summary: one row per (manifold, sample site) with the geometric mean
    of the 3 replicates, its WHO risk category, and, for the two
    3D-printed manifolds, whether that category matches the Millipore
    reference outright or is acceptable within the 5 % boundary rule,
    24 rows = 3 manifolds x 8 sites.

    The source file's own "Wrongly assigned per sample" row is derived
    (a per-site count of misclassifications), not a manifold measurement;
    it carries id "-" and is excluded here, along with any other row
    lacking a real manifold id.
    """
    rows = [r for r in read_handover_csv(path)
            if (r.get("id") or "").strip() not in ("", "-")]

    measurements, by_manifold = [], {}
    for row in rows:
        mid = row["id"].strip()
        by_manifold[mid] = row
        for no, site in SITES.items():
            prefix = next(k for k in row
                          if k.startswith(f"{no}_") and k.endswith("_a"))
            stem = prefix[:-2]
            for rep in ("a", "b", "c"):
                measurements.append({
                    "manifold_id": mid,
                    "manifold_name": row["Name"].strip(),
                    "material": row["Material"].strip(),
                    "sample_no": no,
                    "sample_site": site,
                    "replicate": rep,
                    "cfu_per_100ml": row[f"{stem}_{rep}"].strip(),
                })

    summary = []
    for no, site in SITES.items():
        means = {}
        for mid in by_manifold:
            vals = [float(m["cfu_per_100ml"]) for m in measurements
                    if m["manifold_id"] == mid and m["sample_no"] == no]
            means[mid] = geometric_mean(vals)
        ref = means[REFERENCE_ID]
        for mid, gm in means.items():
            is_ref = mid == REFERENCE_ID
            summary.append({
                "manifold_id": mid,
                "material": by_manifold[mid]["Material"].strip(),
                "sample_no": no,
                "sample_site": site,
                "geometric_mean": f"{gm:.2f}",
                "risk_category": classify(gm),
                "is_reference": "yes" if is_ref else "no",
                "matches_reference":
                    "" if is_ref else
                    ("yes" if classify(gm) == classify(ref) else "no"),
                "acceptable_within_5pct":
                    "" if is_ref else
                    ("yes" if is_acceptable(gm, ref) else "no"),
            })
    return measurements, summary


def write_csv(path, rows):
    """Write rows as comma-delimited UTF-8 (no BOM), header from the first row."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {len(rows):>3} rows  {path}")


def copy_simple(src, dst):
    """Re-delimit a flat (non-wide) handover CSV to comma-separated UTF-8."""
    rows = normalise_rows(read_handover_csv(src))
    applied = apply_editorial(rows)
    write_csv(dst, rows)
    return applied


def main():
    ecoli_src = os.path.join(
        HANDOVER, "Functional Testing",
        "E. coli Quantification and Risk Classification.csv")
    applied = set()
    measurements, summary = tidy_ecoli(ecoli_src)
    write_csv("data/ecoli-quantification.csv", measurements)
    write_csv("data/ecoli-summary.csv", summary)

    for src, dst in [
        ("Functional Testing/Watertightness Testing.csv",
         "data/watertightness.csv"),
        ("Material Testing/Heat Resistance Testing.csv",
         "data/heat-resistance.csv"),
        ("Material Testing/UV Resistance Testing.csv",
         "data/uv-resistance.csv"),
        ("Material Testing/Overall Environmental Resistance Testing- "
         "Structural Testing.csv", "data/environmental-exposure.csv"),
        ("Material Testing/Mechanical Fatigue Testing(Funnel+Syringe).csv",
         "data/mechanical-fatigue.csv"),
    ]:
        applied |= copy_simple(os.path.join(HANDOVER, src), dst)

    missed = {entry_id for entry_id, _, _ in EDITORIAL} - applied
    if missed:
        raise SystemExit(
            f"editorial corrections did not match any row: {sorted(missed)}. "
            "The handover text for those rows has changed, so the published "
            "CSV would silently lose the correction. Update EDITORIAL.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
