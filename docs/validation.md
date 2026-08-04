# Validation

The 3DPLAM is an open-source, locally printable alternative route to the
same measurement the Millipore EZ-Fit™ manifold performs — it is not a
replacement for it. The Millipore served as the **reference instrument**
the 3DPLAM was validated against.

## Test scope

Water was collected from 8 sample sites (listed in
[`../data/README.md`](../data/README.md)) and filtered through 3 manifolds
— a 3DPLAM printed in rPET, a 3DPLAM printed in ABS, and the steel
Millipore reference — 3 times each. That is **8 sites × 3 manifolds × 3
filtrations = 72 filtrations**, recorded in
[`../data/ecoli-quantification.csv`](../data/ecoli-quantification.csv) and
summarised per manifold/site in
[`../data/ecoli-summary.csv`](../data/ecoli-summary.csv) (24 rows: 8 sites
× 3 manifolds).

The protocol is transcribed in full in [`operation.md`](operation.md).

## WHO risk bands

Each manifold/site geometric mean is classified into a WHO drinking-water
risk band: **low risk** (< 1 CFU/100 mL), **intermediate risk** (1–10
CFU/100 mL), **high risk** (11–100 CFU/100 mL), **very high risk** (101–1000
CFU/100 mL). Samples with no visible colonies are recorded as **0.5
CFU/100 mL** by convention, not zero.

The classifier ([`../tools/risk.py`](../tools/risk.py)) implements these as
half-open intervals cutting exactly at 1, 10 and 100 — for example, a
geometric mean of exactly 10.0 CFU/100 mL classifies as "high risk," not
"intermediate," even though WHO states the high band as starting at 11.
This is deliberate and load-bearing: it is what reproduces the published
counts below, and it is documented in the classifier itself so it is not
silently "corrected" back to the literal wording.

## The 5% boundary-tolerance rule

Two 3D-printed manifolds (rPET, ABS) are compared against the Millipore
reference at each of the 8 sites — 16 comparisons. Most land in the same
risk band as the reference outright. Four do not, on a strict band-to-band
comparison — but a geometric mean immediately either side of a band
boundary is a matter of measurement noise near a threshold, not a
disagreement about water quality. The rule: **a geometric mean within 5% of
the WHO boundary separating two bands may be classified into either
adjacent band.** The boundary that matters is the one between the two
specific bands the test and reference values fall into — being close to
some other threshold does not count.

Worked through the four raw mismatches:

| Sample | Manifold | Geometric mean | Band | Millipore | Band | Outcome |
|---|---|---|---|---|---|---|
| 4 | ABS | 9.97 | intermediate | 11.05 | high | Accepted — 9.97 is within 5% of the 10 boundary |
| 5 | rPET | 62.07 | high | 103.16 | very high | Accepted — Millipore is within 5% of the 100 boundary |
| 5 | ABS | 50.78 | high | 103.16 | very high | Accepted — same boundary |
| 7 | rPET | 3.66 | intermediate | 90.41 | high | **Mismatch** — neither value is within 5% of the 10 boundary |

(The Millipore geometric means for samples 5 and 7 are **103.16** and
**90.41** here — the values in the shipped data. The source spreadsheet
published 103.17 and 90.42; the difference is a last-decimal rounding
artefact explained in
[`../data/README.md`](../data/README.md), and it changes
none of the classifications or counts below.)

## The headline result

Two different counts, from two different rules — always state which one is
meant:

- **15 of 16** classifications are **accepted** once the 5% boundary
  tolerance is applied.
- **12 of 16** classifications **match** the reference risk band exactly,
  with **no tolerance** applied.

Recomputing directly from the data:

```bash
python3 -c "
import csv
rows = [r for r in csv.DictReader(open('data/ecoli-summary.csv')) if r['is_reference'] == 'no']
print('accepted', sum(1 for r in rows if r['acceptable_within_5pct'] == 'yes'), 'of', len(rows))
print('raw match', sum(1 for r in rows if r['matches_reference'] == 'yes'), 'of', len(rows))
"
```

gives `accepted 15 of 16` and `raw match 12 of 16` — see
`acceptable_within_5pct` and `matches_reference` in
[`../data/ecoli-summary.csv`](../data/ecoli-summary.csv). The sole
comparison that fails even with the tolerance applied is sample 7, rPET
(the row above) — the same sample that is a spiked positive control, not a
field sample (see the caveats in
[`../data/README.md`](../data/README.md)).

## Watertightness

Three prototypes were tested for leakage, in
[`../data/watertightness.csv`](../data/watertightness.csv): an rPET base
with a Millipore funnel (taped joint) leaked at the funnel–base connection
after ~5 minutes; an ABS base with an ABS funnel (also taped) and a 2GLAM
comparison unit both showed no leakage over 2.5 hours. That taped joint is
the one the published base's clamped-membrane seal replaces — see
[`design-history.md`](design-history.md). All three showed uniform filter
membrane colouration, i.e. even filtration across the membrane surface (the
source data records this as `unifrom`, a transcription typo carried through
unchanged — see the caveat in
[`../data/README.md`](../data/README.md)).

## Material and fatigue results

Full breakdown, by material, in [`printing.md`](printing.md). In short: ABS
and ASA showed no critical damage under 2 hours at 80 °C, 48 hours of UV,
or 14 days outdoors; PLA, PETG and rPET all showed critical dimensional
damage under the 80 °C heat test but not under UV or 14-day outdoor
exposure. Across all 5 materials, the printed funnel survived 25 cycles of
alcohol-wipe decontamination with no structural damage or leakage, and the
100 mL PVC syringe survived all 72 filtrations of this validation without
damage or leakage
([`../data/mechanical-fatigue.csv`](../data/mechanical-fatigue.csv)).

## Limitations

- **Particle-laden samples behave differently.** Samples 5 and 7 both
  needed non-standard handling (partial filtration and a spiked positive
  control respectively — see [`../data/README.md`](../data/README.md)),
  and both are implicated in the disagreements above.
- **The two 3D-printed manifolds were not printed identically.** The ABS
  manifold used a fully 3D-printed funnel; the rPET manifold's funnel was a
  commercial Millipore funnel mounted on a printed base (the base's top
  connection accepts either — see
  [`../hardware/README.md`](../hardware/README.md)). If a 3D-printed funnel
  traps bacteria more readily than a steel one, that would show up as the
  all-printed manifold reading systematically low — and it does: the ABS
  manifold returned the lowest count of the three manifolds at 6 of the 8
  sites (1–6). At site 7 the rPET manifold, with its commercial funnel,
  read lowest instead — and that is also the sole classification mismatch
  above. At site 8 all three manifolds recorded the 0.5 CFU/100 mL floor
  value, a three-way tie.
- **A single operator ran all 72 filtrations, in a single testing period.**
  Neither operator variability nor seasonal variation in source water is
  captured.
- **Filtration order was not randomised across manifolds.** The Millipore
  reference was filtered last at each site, so any sedimentation of the
  sample while earlier manifolds were run could inflate its counts
  relative to the two printed manifolds.
