# Validation

The 3DPLAM is an open-source, locally printable alternative route to the
same measurement that the Millipore EZ-Fit™ manifold performs. The 3DPLAM
does not replace the Millipore, which served as the reference instrument
in this validation.

## Test scope

Water was collected from 8 sample sites, listed in
[`../data/README.md`](../data/README.md). Each sample was filtered 3 times
through each of 3 manifolds (a 3DPLAM printed in rPET, a 3DPLAM printed in
ABS, and the steel Millipore reference). This gives 8 sites × 3 manifolds
× 3 filtrations = 72 filtrations, recorded in
[`../data/ecoli-quantification.csv`](../data/ecoli-quantification.csv).
[`../data/ecoli-summary.csv`](../data/ecoli-summary.csv) summarises them per
manifold/site (24 rows: 8 sites × 3 manifolds). All samples were collected
on 31 May 2026. Sites 1–4 were filtered on 1 June and sites 5–8 on 2 June.

The protocol is transcribed in full in [`operation.md`](operation.md).

## WHO risk bands

Each manifold/site geometric mean is classified into a WHO drinking-water
risk band: **low risk** (< 1 CFU/100 mL), **intermediate risk** (1–10
CFU/100 mL), **high risk** (11–100 CFU/100 mL), **very high risk** (101–1000
CFU/100 mL). By convention, samples with no visible colonies are recorded
as 0.5 CFU/100 mL instead of zero.

The classifier ([`../tools/risk.py`](../tools/risk.py)) implements these
bands as half-open intervals that cut exactly at 1, 10 and 100. For
example, a geometric mean of exactly 10.0 CFU/100 mL classifies as "high
risk" and not "intermediate", even though WHO states that the high band
starts at 11. This choice is deliberate, because it reproduces the
published counts below. The classifier documents the choice in its own
code so that nobody silently "corrects" it back to the literal wording.

## The 5 % boundary-tolerance rule

Two 3D-printed manifolds (rPET, ABS) are compared against the Millipore
reference at each of the 8 sites, which gives 16 comparisons. Twelve of
them fall in the same risk band as the reference without any tolerance.
The other four differ on a strict band-to-band comparison. When a
geometric mean sits immediately either side of a band boundary, that
difference reflects measurement noise near the threshold and does not
indicate a disagreement about water quality. The tolerance rule states
that **a geometric mean within 5 % of the WHO boundary separating two bands
may be classified into either adjacent band.** Only the boundary between
the two specific bands that the test and reference values fall into
counts. Closeness to any other threshold does not.

The table below works through the four raw mismatches.

| Sample | Manifold | Geometric mean | Band | Millipore | Band | Outcome |
|---|---|---|---|---|---|---|
| 4 | ABS | 9.97 | intermediate | 11.05 | high | Accepted: 9.97 is within 5 % of the 10 boundary |
| 5 | rPET | 62.07 | high | 103.16 | very high | Accepted: Millipore is within 5 % of the 100 boundary |
| 5 | ABS | 50.78 | high | 103.16 | very high | Accepted: same boundary |
| 7 | rPET | 3.66 | intermediate | 90.41 | high | **Mismatch**: neither value is within 5 % of the 10 boundary |

(The Millipore geometric means for samples 5 and 7 are 103.16 and 90.41
here, as in the shipped data. The source spreadsheet published 103.17 and
90.42. The difference comes from rounding in the last decimal, and it
changes none of the classifications or counts below.)

## The headline result

The headline result consists of two counts from two different rules, so
always state which one is meant.

- **15 of 16** classifications are accepted once the 5 % boundary
  tolerance is applied.
- **12 of 16** classifications match the reference risk band exactly,
  with no tolerance applied.

To recompute both counts directly from the data, run:

```bash
python3 -c "
import csv
rows = [r for r in csv.DictReader(open('data/ecoli-summary.csv')) if r['is_reference'] == 'no']
print('accepted', sum(1 for r in rows if r['acceptable_within_5pct'] == 'yes'), 'of', len(rows))
print('raw match', sum(1 for r in rows if r['matches_reference'] == 'yes'), 'of', len(rows))
"
```

The script prints `accepted 15 of 16` and `raw match 12 of 16`. The
underlying columns are `acceptable_within_5pct` and `matches_reference` in
[`../data/ecoli-summary.csv`](../data/ecoli-summary.csv). The only
comparison that fails even with the tolerance applied is sample 7, rPET
(the last row of the table above). Sample 7 is the spiked positive control
and is not a field sample (see the notes in
[`../data/README.md`](../data/README.md)).

## Watertightness

Three prototypes were tested for leakage, with results in
[`../data/watertightness.csv`](../data/watertightness.csv). An rPET base
with a Millipore funnel (taped joint) leaked at the funnel–base connection
after ~5 minutes. An ABS base with an ABS funnel (also taped) and a 2GLAM
comparison unit both showed no leakage over 2.5 hours. The clamped-membrane
seal of the published base takes the place of this taped joint (see
[`design-history.md`](design-history.md)). All three prototypes showed
uniform colouration of the filter membrane, which indicates even
filtration across the membrane surface.

## Material and fatigue results

[`printing.md`](printing.md) gives the full breakdown by material. ABS and
ASA showed no critical damage under 2 hours at 80 °C, 48 hours of UV, or
14 days outdoors. PLA, PETG and rPET all showed critical dimensional
damage in the 80 °C heat test, but not under UV or 14-day outdoor
exposure. Across all 5 materials, the printed funnel survived 25 cycles of
alcohol-wipe decontamination with no structural damage or leakage. The
100 mL PVC syringe survived all 72 filtrations of this validation without
damage or leakage. Both fatigue results are in
[`../data/mechanical-fatigue.csv`](../data/mechanical-fatigue.csv).

## Limitations

- **Particle-laden samples behave differently.** Samples 5 and 7 both
  needed non-standard handling (partial filtration and a spiked positive
  control, respectively; see [`../data/README.md`](../data/README.md)).
  Both samples are involved in the disagreements above.
- **The two 3D-printed manifolds were not printed identically.** The ABS
  manifold used a fully 3D-printed funnel. The rPET manifold used a
  commercial Millipore funnel mounted on a printed base (the top connection
  of the base accepts either funnel; see
  [`../hardware/README.md`](../hardware/README.md)). If a 3D-printed funnel
  traps bacteria more readily than a steel one, the all-printed manifold
  would read systematically low. The ABS manifold did return the lowest
  count of the three manifolds at 6 of the 8 sites (sites 1–6). At site 7,
  the rPET manifold with its commercial funnel read lowest instead, and
  this comparison is also the only classification mismatch above. At site 8, all
  three manifolds recorded the floor value of 0.5 CFU/100 mL, a three-way
  tie.
- **A single operator ran all 72 filtrations, in a single testing period.**
  The data therefore capture neither operator variability nor seasonal
  variation in source water.
- **Filtration order was not randomised across manifolds.** The manifolds
  were run in blocks. On each test day, all 12 filtrations of that day's
  four samples were done on the rPET manifold first, then on the ABS
  manifold, then on the Millipore reference. Particles could settle, or
  growth could occur during storage, while the printed manifolds were run
  first. Either effect could inflate the reference counts relative to the
  printed manifolds. A time trend alone does not explain the ABS manifold
  reading lowest, because it ran after the rPET manifold.
- **Samples were stored before filtration, and counting was not blinded.**
  All samples were collected on 31 May 2026 and stored in dim light
  without refrigeration until filtration 1 to 2 days later. The funnels of all
  three manifolds, including the commercial Millipore funnels, were
  reused after an alcohol wipe. Plates were read once, at 24 h, by the
  operator, who knew which manifold each plate came from. Small colonies
  on plates with particles or algae were hard to tell apart.
