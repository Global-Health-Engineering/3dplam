import pytest
from tools.tidy_data import read_handover_csv, tidy_ecoli

SRC = ("../2026-bsc-thesis-mgabri/data/raw_data/tables (csv)/"
       "Functional Testing/E. coli Quantification and Risk Classification.csv")

import os
pytestmark = pytest.mark.skipif(
    not os.path.exists(SRC),
    reason="handover source directory not available (e.g. in CI)")


def test_reader_strips_bom_from_first_header():
    rows = read_handover_csv(SRC)
    assert "Name" in rows[0]
    assert not any(k.startswith("﻿") for k in rows[0])


def test_reader_drops_empty_rows():
    rows = read_handover_csv(SRC)
    assert all(any(v.strip() for v in r.values()) for r in rows)


def test_tidy_ecoli_yields_72_measurements():
    measurements, _ = tidy_ecoli(SRC)
    assert len(measurements) == 72          # 8 samples x 3 manifolds x 3 reps


def test_tidy_ecoli_yields_24_summary_rows():
    _, summary = tidy_ecoli(SRC)
    assert len(summary) == 24               # 8 samples x 3 manifolds


def test_derived_summary_row_is_excluded():
    measurements, summary = tidy_ecoli(SRC)
    names = {m["manifold_name"] for m in measurements}
    assert not any("Wrongly assigned" in n for n in names)
    assert len(names) == 3


def test_recomputed_geometric_means_match_the_source():
    _, summary = tidy_ecoli(SRC)
    row = next(r for r in summary
               if r["manifold_id"] == "ft1" and r["sample_no"] == "1")
    assert float(row["geometric_mean"]) == pytest.approx(27.56, abs=0.01)


def test_headline_counts_are_reproduced():
    _, summary = tidy_ecoli(SRC)
    tested = [r for r in summary if r["is_reference"] == "no"]
    assert len(tested) == 16
    assert sum(1 for r in tested if r["matches_reference"] == "yes") == 12
    assert sum(1 for r in tested if r["acceptable_within_5pct"] == "yes") == 15
