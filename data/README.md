# data

Functional and material test data for the 3DPLAM manifold. Every column of every file is documented in [`codebook.csv`](codebook.csv).

## Files

| File                         | Contents                                                                                                       |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `ecoli-quantification.csv`   | Raw *E. coli* colony counts: 3 manifolds x 8 sample sites x 3 replicates (72 rows)                             |
| `ecoli-summary.csv`          | Geometric mean per manifold/site, WHO risk category, and agreement with the steel reference manifold (24 rows) |
| `watertightness.csv`         | Leakage testing of 3 manifold prototypes (3 rows)                                                              |
| `heat-resistance.csv`        | 2-hour heat exposure of 6 manifold parts across 5 materials (30 rows)                                          |
| `uv-resistance.csv`          | 48-hour UV exposure of the assembled manifold across 5 materials (5 rows)                                      |
| `environmental-exposure.csv` | 14-day outdoor weathering of the assembled manifold across 5 materials (5 rows)                                |
| `environmental-weather.csv`  | Daily weather log for the 14-day outdoor exposure period (14 rows)                                             |
| `mechanical-fatigue.csv`     | Cyclic loading of the funnel (5 materials) and a reference PVC syringe (6 rows)                                |
| `codebook.csv`               | One row per column of every file above: name, type, observed values, description, unit                         |

## Headline result

Comparing the two 3D-printed manifolds (rPET, ABS) against the steel Millipore reference across 8 sample sites (16 comparisons total):

- **12 of 16** classifications match the reference's WHO risk category exactly, with **no tolerance** applied.
- **15 of 16** are acceptable once the **5 % boundary-tolerance rule** is applied (a geometric mean within 5 % of a WHO band boundary may be classified into either adjacent band).

These are two different counts for two different rules — always state which one is meant. See `ecoli-summary.csv` (`matches_reference` = the
12/16 figure, `acceptable_within_5pct` = the 15/16 figure) and `tools/risk.py` for the classification logic.

## Sample sites

| #     | Site                                                         | Location                                                       |
| ----- | ------------------------------------------------------------ | -------------------------------------------------------------- |
| 1     | Limmat, Platzspitz                                           | [47°22'54.2"N 8°32'23.3"E](https://maps.app.goo.gl/R5HYHXrchyp9zU4e9) |
| 2     | Sihl riverside steps                                         | [47°22'39.9"N 8°32'11.2"E](https://maps.app.goo.gl/t2w6ZBqyXtTheTvU8) |
| 3     | Lake of Zürich, Rentenwiese                                  | [47°21'48.2"N 8°32'13.6"E](https://maps.app.goo.gl/Xsy4nUzgeniSF7QS6) |
| 4     | Lake of Zürich, Reisbach viewpoint                           | [47°21'28.5"N 8°32'49.7"E](https://maps.app.goo.gl/RfrFR1WqzwqbAtgdA) |
| 5[^1] | Irchel Park pond                                             | [47°23'52.4"N 8°32'38.5"E](https://maps.app.goo.gl/xAfFDwxMpErPbqV17) |
| 6     | Zürichberg Resi Pond                                         | [47°23'31.9"N 8°33'10.4"E](https://maps.app.goo.gl/KXh66xjuwYgjUPYf7) |
| 7     | ETH Zürich, CLD Building, tap water + 25 mL fecal suspension | [47°22'43.6"N 8°32'45.2"E](https://maps.app.goo.gl/v8skA6kZncdn9hSt8) |
| 8     | ETH Zürich, CLA Building, tap water                          | [47°22'38.4"N 8°32'49.6"E](https://maps.app.goo.gl/57Mg5KN6icj9zju26) |

[^1]: Sample not fully drawn through the filter membrane. Filtration stalled at roughly the 20 mL mark of the 100 mL sample, so about 80 mL was actually filtered. The recorded CFU counts for sample 5 (`ecoli-quantification.csv`, `ecoli-summary.csv`) reflect this partial volume, not the full 100 mL.

