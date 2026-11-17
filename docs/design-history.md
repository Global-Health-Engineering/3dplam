# Design history

The files in [`../hardware/`](../hardware/) carry no version numbers. They
are the current release, and git records their history from here on. This
page records the version history that predates this repository, including
the names the shipped parts had during development and what changed.

## Shipped revisions

| Part | Shipped revision | Unchanged since |
|---|---|---|
| Base | V1.3 | (the part that kept changing) |
| Funnel | V6.1 | V1.1 |
| Filter support, strand mesh | V5 | V1.1 |
| Filter support, hex hole | V1.2 | V1.1 |

Only the base changed after V1.1. The funnel and both filter supports
reached their shipped form by V1.1, and their files have not changed in
any release since. Source Onshape documents for each labelled version are
linked from [`../hardware/onshape.md`](../hardware/onshape.md).

## Corrections in v1.0.1

The strand-mesh filter support released in v1.0.0 had been exported
without the four slots of its bayonet lock, so it could not lock into the
base. Release v1.0.1 replaces it, and the assembly that contains it, with
the design as printed and tested. Release v1.0.1 also corrects the layer
height in the print profiles to 0.20 mm. The validated parts were printed
at this layer height, and the joint tolerances assume it. The same release
corrects the mass of a printed set to about 52 g.

## Base revision V1.2 to V1.3

The *E. coli* validation reported in [`validation.md`](validation.md) was
performed with base V1.2. Its funnel joint was sealed with electrical tape
instead of the clamped-membrane seal described in
[`assembly.md`](assembly.md). The tape was applied in two layers, per the
watertightness testing notes (see
[`../data/watertightness.csv`](../data/watertightness.csv)).

The published base is V1.3. It replaces the taped joint with the
clamped-membrane seal, and adds a bottom brim, three legs, and four
mounting holes. This revision targets leak-tightness and rigidity, meaning
how the base seals to the funnel and sits on a surface. It leaves the
filtration path itself unchanged. The funnel and filter support are the
same in the validated and published configurations, so the validation
carries over to the published device.

## Earlier iterations

The handover's own notes document two earlier full-assembly design rounds,
labelled "Version 1" and "Version 4". These labels follow a separate,
coarser numbering than the per-part V1.1/V1.2/V5/V6.1 labels above.

- **Version 1** shipped a hex-hole filter support, and its base connection
  was compatible with commercial Millipore Microfil funnels as well as the
  printed one.
- **Version 4** replaced the hex-hole filter support with the strand-mesh
  design (later finalised as filter support V5) and reworked the base for
  watertightness. The filter support of this round still had a sloped
  side. The author's printing note from this round said to print the
  support on its smaller-diameter side, separately from the other parts.
  Later versions dropped the slope, and the current orientation guidance
  is in [`printing.md`](printing.md).

Versions between and after these (V1.1 through V1.3, V5, V6 and V6.1) are
recorded only as the Onshape documents linked from
[`../hardware/onshape.md`](../hardware/onshape.md). The handover did not
include a written part-by-part rationale for each of those steps, so this
page does not reconstruct one.

## Converging the funnel–base fit

The tolerance of the funnel-to-base joint was found empirically. A series
of test rings was printed in steps of 0.02 to 0.05 mm, with the inner
diameter swept from 48.75 to 48.85 mm and the outer diameter from 52.6 to
52.925 mm. The aim was to find the clearance that seals without binding.
The test-ring files are prototyping artifacts and are not shipped in this
repository. This page records the method so that it can be repeated if the
fit needs re-tuning for a different printer or material.
