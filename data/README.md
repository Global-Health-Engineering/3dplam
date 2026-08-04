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
| 2 | Sihl, Treppen bei der Sihl | not available in the source material carried into this release |
| 3 | Lake of Zurich, Rentenwiese | not available in the source material carried into this release |
| 4 | Lake of Zurich, Aussichtspunkt Riesbach | not available in the source material carried into this release |
| 5 | Irchel Campus, Ircheltuempel | not available in the source material carried into this release |
| 6 | Zurichberg, Resi-Weiher | not available in the source material carried into this release |
| 7 | ETH Zurich CLD, tap water + fecal suspension | positive control, not a field site — see caveat below |
| 8 | ETH Zurich CLA, tap water | lab tap, not a field site |

Sites 2-6 are outdoor sampling locations in and around Zurich; no Google
Maps link for them was carried forward into this release's source
material. If precise coordinates are needed, confirm with the thesis
author rather than guessing from the site name.

## Known data caveats

1. **Sample 1 map link is disputed.** The handover README gives
   `https://maps.app.goo.gl/R5HYHXrchyp9zU4e9`; the thesis Table 1 gives
   `https://maps.app.goo.gl/P6ut9wVUvfRmA4wv7`. Both are labelled "Limmat,
   Platzspitz". This has not been resolved — **pending confirmation from
   the author** — and neither link has been silently preferred over the
   other.

2. **Sample 5 was not fully drawn through the filter membrane.**
   Filtration stalled at roughly the 20 mL mark of the 100 mL sample, so
   only about 80 mL was actually filtered. The recorded CFU counts for
   sample 5 (`ecoli-quantification.csv`, `ecoli-summary.csv`) reflect
   this partial volume, not the full 100 mL.

3. **Sample 7 is a positive control, not a field sample.** It is 1,250 mL
   of ETH Zurich CLD tap water spiked with 25 mL of horse faecal
   suspension, used to confirm the assay could detect a heavily
   contaminated sample. Treat it differently from the other seven,
   genuinely environmental, sites.

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
   values** (103.16, 90.41); `codebook.csv`'s stated range for
   `geometric_mean` (`0.5-103.17`) mirrors the brief's original worked
   example and cites the older, published upper bound — the actual
   maximum present in the shipped data is 103.16.

5. **`watertightness.csv`'s `Uniform Filter Membrane Coloration` column
   contains a typo: `unifrom`** (transposed letters, meant to read
   "uniform"). This is the student's raw recorded value in all three
   rows and has been carried through unchanged rather than silently
   corrected. If you are filtering or searching this column for the
   string `"uniform"`, you will get **zero rows** — search for
   `"unifrom"` instead, or match on a substring that tolerates the typo.
