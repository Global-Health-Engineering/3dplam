# data

Functional and material test data for the 3DPLAM manifold, tidied from the
handover spreadsheets. Every column of every file is documented in
[`codebook.csv`](codebook.csv).

## Files

| File | Contents |
|---|---|
| `ecoli-quantification.csv` | Raw *E. coli* colony counts: 3 manifolds x 8 sample sites x 3 replicates (72 rows) |
| `ecoli-summary.csv` | Geometric mean per manifold/site, WHO risk category, and agreement with the steel reference manifold (24 rows) |
| `watertightness.csv` | Leakage testing of 3 manifold prototypes (3 rows) |
| `heat-resistance.csv` | 2-hour heat exposure of 6 manifold parts across 5 materials (30 rows) |
| `uv-resistance.csv` | 48-hour UV exposure of the assembled manifold across 5 materials (5 rows) |
| `environmental-exposure.csv` | 14-day outdoor weathering of the assembled manifold across 5 materials (5 rows) |
| `environmental-weather.csv` | Daily weather log for the 14-day outdoor exposure period (14 rows) |
| `mechanical-fatigue.csv` | Cyclic loading of the funnel (5 materials) and a reference PVC syringe (6 rows) |
| `codebook.csv` | One row per column of every file above: name, type, observed values, description, unit |

## Headline result

Comparing the two 3D-printed manifolds (rPET, ABS) against the steel
Millipore reference across 8 sample sites (16 comparisons total):

- **12 of 16** classifications match the reference's WHO risk category
  exactly, with **no tolerance** applied.
- **15 of 16** are acceptable once the **5% boundary-tolerance rule** is
  applied (a geometric mean within 5% of a WHO band boundary may be
  classified into either adjacent band).

These are two different counts for two different rules — always state
which one is meant. See `ecoli-summary.csv` (`matches_reference` = the
12/16 figure, `acceptable_within_5pct` = the 15/16 figure) and
`tools/risk.py` for the classification logic.

## Sample sites

| # | Site | Google Maps |
|---|---|---|
| 1 | Limmat, Platzspitz | **Conflicting sources — see caveat below** |
| 2 | Sihl, "Treppen bei der Sihl" | https://maps.app.goo.gl/t2w6ZBqyXtTheTvU8 |
| 3 | Lake of Zürich, Rentenwiese | https://maps.app.goo.gl/Xsy4nUzgeniSF7QS6 |
| 4 | Lake of Zürich, "Aussichtspunkt Riesbach" | https://maps.app.goo.gl/RfrFR1WqzwqbAtgdA |
| 5 | Irchel Campus, "Ircheltümpel" | https://maps.app.goo.gl/xAfFDwxMpErPbqV17 |
| 6 | Zürichberg, "Resi-Weiher" | https://maps.app.goo.gl/KXh66xjuwYgjUPYf7 |
| 7 | ETH Zürich, CLD Building — tap water + 25 mL faecal suspension | https://maps.app.goo.gl/v8skA6kZncdn9hSt8 |
| 8 | ETH Zürich, CLA Building — tap water | https://maps.app.goo.gl/57Mg5KN6icj9zju26 |

For sites 2–8, the handover README and thesis Table 1 give **identical**
links — no discrepancy. Only site 1 differs between the two sources; see
the caveat below. Sites 7 and 8 are lab controls at ETH Zurich, not
outdoor field sites (see caveats 2 and 3 below for what they represent).

## Known data caveats

1. **The map link for sample 1 is disputed; no other site's link is.** For
   sites 2–8, the handover README and thesis Table 1 give byte-identical
   Google Maps links (reproduced in the table above), which is why only
   site 1 is called out here rather than every site individually. For
   site 1 specifically, the two sources disagree:
   - handover README: `https://maps.app.goo.gl/R5HYHXrchyp9zU4e9`
   - thesis Table 1: `https://maps.app.goo.gl/P6ut9wVUvfRmA4wv7`

   Both are labelled "Limmat, Platzspitz". This has not been resolved —
   **pending confirmation from the author** — and neither link has been
   silently preferred over the other.

2. **Sample 5 was not fully drawn through the filter membrane.**
   Filtration stalled at roughly the 20 mL mark of the 100 mL sample, so
   only about 80 mL was actually filtered. The recorded CFU counts for
   sample 5 (`ecoli-quantification.csv`, `ecoli-summary.csv`) reflect
   this partial volume, not the full 100 mL.

3. **Sample 7 is a positive control, not a field sample.** It is 1,250 mL
   of ETH Zurich CLD tap water spiked with 25 mL of horse faecal
   suspension, used to confirm the assay could detect a heavily
   contaminated sample. It should be treated differently from the other
   seven, genuinely environmental, sites.

4. **Two geometric means differ from the source spreadsheet's own
   published values in the last decimal**, for the steel reference
   manifold (`ecoli-summary.csv`, `is_reference = yes`):
   - Sample 5: source spreadsheet publishes 103.17; recomputed from the
     three raw replicates in `ecoli-quantification.csv` it is 103.16.
   - Sample 7: source spreadsheet publishes 90.42; recomputed it is
     90.41.

   These are rounding artefacts in the original spreadsheet (its published
   figure was evidently rounded from slightly different intermediate
   precision). No risk category and neither of the headline counts above
   is affected either way. **The shipped CSVs carry the recomputed
   values** (103.16, 90.41), and so does `codebook.csv`'s stated range for
   `geometric_mean` (`0.5-103.16`) — it describes the data that is
   actually in the file, not the source spreadsheet's originally
   published 103.17. The 103.17 and 90.42 figures above are the source
   spreadsheet's values, kept here only to explain the discrepancy; they
   do not appear anywhere in the shipped CSVs or in the codebook.

5. **`watertightness.csv`'s `Uniform Filter Membrane Coloration` column
   contains a typo: `unifrom`** (transposed letters, meant to read
   "uniform"). This is the student's raw recorded value in all three
   rows and has been carried through unchanged rather than silently
   corrected. If you are filtering or searching this column for the
   string `"uniform"`, you will get **zero rows** — search for
   `"unifrom"` instead, or match on a substring that tolerates the typo.
