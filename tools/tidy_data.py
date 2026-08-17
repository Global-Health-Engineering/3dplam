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
import sys

# Make the repository root importable so this file works both as a script
# (python3 tools/tidy_data.py) and as a module (python3 -m tools.…).
# Without this, direct script invocation fails with ModuleNotFoundError
# because tools/ — not the repo root — is what lands on sys.path.
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
# published CSVs are generated, so that every artifact downstream — the
# CSVs, data/README.md, the codebook and the validation figure — carries
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

    measurements: one row per (manifold, sample site, replicate) —
    72 rows = 3 manifolds x 8 sites x 3 replicates.
    summary: one row per (manifold, sample site) with the geometric mean
    of the 3 replicates, its WHO risk category, and — for the two
    3D-printed manifolds — whether that category matches the Millipore
    reference outright or is acceptable within the 5% boundary rule —
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
    rows = read_handover_csv(src)
    write_csv(dst, rows)


def main():
    ecoli_src = os.path.join(
        HANDOVER, "Functional Testing",
        "E. coli Quantification and Risk Classification.csv")
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
        copy_simple(os.path.join(HANDOVER, src), dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
