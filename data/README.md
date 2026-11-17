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

The two 3D-printed manifolds (rPET, ABS) were compared against the steel Millipore reference across 8 sample sites, giving 16 comparisons in total.

- **12 of 16** classifications match the reference's WHO risk category exactly, with no tolerance applied.
- **15 of 16** are acceptable once the 5 % boundary-tolerance rule is applied (a geometric mean within 5 % of a WHO band boundary may be classified into either adjacent band).

The two counts come from two different rules, so always state which one is meant. See `ecoli-summary.csv` (`matches_reference` = the
12/16 figure, `acceptable_within_5pct` = the 15/16 figure) and `tools/risk.py` for the classification logic.

## Sample sites

Site names are in English. They are the exact `sample_site` values in
`ecoli-quantification.csv` and `ecoli-summary.csv`, and the validation
figure uses the same strings as axis labels. Four names were translated
from the German of the handover record, as noted below the table.

| #     | `sample_site`                                | Location                                                       |
| ----- | -------------------------------------------- | -------------------------------------------------------------- |
| 1     | Limmat, Platzspitz                           | [47°22'54.2"N 8°32'23.3"E](https://maps.app.goo.gl/R5HYHXrchyp9zU4e9) |
| 2     | Sihl riverside steps                         | [47°22'39.9"N 8°32'11.2"E](https://maps.app.goo.gl/t2w6ZBqyXtTheTvU8) |
| 3     | Lake of Zurich, Rentenwiese                  | [47°21'48.2"N 8°32'13.6"E](https://maps.app.goo.gl/Xsy4nUzgeniSF7QS6) |
| 4     | Lake of Zurich, Riesbach viewpoint           | [47°21'28.5"N 8°32'49.7"E](https://maps.app.goo.gl/RfrFR1WqzwqbAtgdA) |
| 5[^1] | Irchel Campus, Irchel pond                   | [47°23'52.4"N 8°32'38.5"E](https://maps.app.goo.gl/xAfFDwxMpErPbqV17) |
| 6     | Zurichberg, Resi pond                        | [47°23'31.9"N 8°33'10.4"E](https://maps.app.goo.gl/KXh66xjuwYgjUPYf7) |
| 7[^2] | ETH Zurich CLD, tap water + fecal suspension | [47°22'43.6"N 8°32'45.2"E](https://maps.app.goo.gl/v8skA6kZncdn9hSt8) |
| 8     | ETH Zurich CLA, tap water                    | [47°22'38.4"N 8°32'49.6"E](https://maps.app.goo.gl/57Mg5KN6icj9zju26) |

**Translated from the handover record.** The original German descriptions
are kept here so that any published value can be traced back to what was
written down in the field.

| # | As collected              | As published            |
| - | ------------------------- | ----------------------- |
| 2 | Sihl, Treppen bei der Sihl | Sihl riverside steps    |
| 4 | Aussichtspunkt Riesbach   | Riesbach viewpoint      |
| 5 | Ircheltuempel             | Irchel pond             |
| 6 | Resi-Weiher               | Resi pond               |

Only descriptive words were translated, and proper place names were kept.
Platzspitz and Rentenwiese are place names, so they were left as they are.
Resi-Weiher keeps Resi, while *-Weiher* (pond) is translated. Site 2 loses
its "Sihl, " prefix because the German named the river twice. The
translation is defined in `SITES` in
[`../tools/tidy_data.py`](../tools/tidy_data.py), the only place where
these CSVs are generated.

[^1]: The sample was not fully drawn through the filter membrane. Filtration stalled at roughly the 20 mL mark of the 100 mL sample, so about 80 mL was actually filtered. The recorded colony-forming unit (CFU) counts for sample 5 (`ecoli-quantification.csv`, `ecoli-summary.csv`) reflect this partial volume, not the full 100 mL.

[^2]: This sample was tap water spiked with 25 mL of horse fecal suspension. It served as a positive control and is not a field sample.

