# Printing

Which files to print, and how to choose a filter support, funnel variant or
material, are owned by [`../hardware/README.md`](../hardware/README.md),
start there for the parts table and envelopes. This page covers the print
settings requirement, orientation guidance, and how the five printable
materials compare under testing.

## Print settings

A manifold sliced at default settings is porous: the syringe pulls air
through the plastic instead of pulling water through the membrane, and
filtration fails.

The authoritative settings, importable Bambu Studio profiles, and
cross-slicer equivalents live in
[`../hardware/print-profiles/README.md`](../hardware/print-profiles/README.md).
Read that page before slicing anything; it is not repeated here.

## Orientation

Print the filter support **in its normal upright position**, the way it
sits in the base, with the bayonet slots opening on the bottom side. The
bottom of the mesh is then the side exposed to the heat of the print bed,
where the strands may deform slightly; the top of the mesh prints precise
and uniform, and that is the side the water reaches first. (Earlier
filter-support versions had a sloped side; the current ones do not.) Print
the filter support **as its own job**, separately from the base and
funnel, for the best surface quality on the side that sat on the bed.

## Materials

Five materials were tested: 2 hours at 80 °C (heat), 48 hours in a UV
chamber, 14 days of outdoor weathering, and 25 cycles of alcohol-wipe
decontamination (funnel only). Full per-specimen notes are in the source
CSVs; this is the summary.

| Material | Heat, 80 °C / 2 h | UV, 48 h | Outdoor, 14 days | 25 sterilisation cycles | Verdict |
|---|---|---|---|---|---|
| PLA | **Critical damage**: warping and shrinkage across base, funnel and filter support; parts no longer fit together | No structural damage; visible whitening vs. an unexposed part | No critical damage; no UV discolouration; brim bent | No damage or leakage | Not recommended: 60 °C glass transition, absorbs water |
| PETG | **Critical damage**: connection diameters shrank, parts no longer fit | No structural damage; no visible discolouration | No critical damage; no UV discolouration | No damage or leakage | Viable below ~80 °C; no enclosure needed |
| rPET | **Critical damage**: connection diameters shrank, parts no longer fit | No structural damage; discolouration not determined | No critical damage; no UV discolouration | No damage or leakage | Sustainable route: see [`rpet.md`](rpet.md). Use the [`../hardware/rpet/`](../hardware/rpet/) geometry |
| **ABS** | No critical damage: all parts still fit | No structural damage; visible whitening vs. an unexposed part | No critical damage; no UV discolouration | No damage or leakage | **Recommended**: needs an enclosed printer |
| ASA | No critical damage: all parts still fit | No structural damage; visible whitening vs. an unexposed part | No critical damage; no UV discolouration; brim bent | No damage or leakage | Equivalent to ABS; less widely available |

Source data: [`../data/heat-resistance.csv`](../data/heat-resistance.csv),
[`../data/uv-resistance.csv`](../data/uv-resistance.csv),
[`../data/environmental-exposure.csv`](../data/environmental-exposure.csv),
[`../data/mechanical-fatigue.csv`](../data/mechanical-fatigue.csv). The
Verdict column matches the materials table in
[`../hardware/print-profiles/README.md`](../hardware/print-profiles/README.md);
it is not restated differently here.

The mechanical-fatigue result is not limited to the printed funnel: the
100 mL PVC syringe used throughout the *E. coli* validation ran for all 72
filtrations (see [`validation.md`](validation.md)) without structural
damage or leakage.

A timelapse of the final base (V1.3) being printed in rPET is on the project site
(`site/public/video/base-printing-timelapse.gif`).
