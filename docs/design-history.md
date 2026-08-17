# Design history

The files in [`../hardware/`](../hardware/) carry no version numbers: they
are the current release, and git records their history from here on. This
page records the version history that predates this repository: what the
shipped parts were called during development, and what changed.

## Shipped revisions

| Part | Shipped revision | Byte-identical since |
|---|---|---|
| Base | V1.3 |, (the part that kept changing) |
| Funnel | V6.1 | V1.1 |
| Filter support, strand mesh | V5 | V1.1 |
| Filter support, hex hole | V1.2 | V1.1 |

**Only the base changed after V1.1.** The funnel and both filter supports
reached their shipped form by V1.1 and have been byte-identical in every
release since. Source Onshape documents for each labelled version are
linked from [`../hardware/onshape.md`](../hardware/onshape.md).

## Base revision V1.2 to V1.3

The *E. coli* validation reported in [`validation.md`](validation.md) was
performed with **base V1.2**, its funnel joint sealed with electrical tape
(two layers, per the watertightness testing notes; see
[`../data/watertightness.csv`](../data/watertightness.csv)) rather than the
clamped-membrane seal described in [`assembly.md`](assembly.md).

The published base is **V1.3**. It replaces the taped joint with the
clamped-membrane seal, and adds a bottom brim, three legs, and four
mounting holes. This revision targets **leak-tightness and rigidity**, 
how the base seals to the funnel and sits on a surface, not the
filtration path itself. The funnel and filter support are unchanged
between the validated and published configurations. The validation carries
to the published device as a matter of what actually changed, not as a
caveat on the headline result.

## Earlier iterations

Two earlier full-assembly design rounds, labelled "Version 1" and "Version
4" in the handover's own notes (a separate, coarser numbering than the
per-part V1.1/V1.2/V5/V6.1 labels above), are documented there:

- **Version 1** shipped a hex-hole filter support, and its base connection
  was compatible with commercial Millipore Microfil funnels as well as the
  printed one.
- **Version 4** replaced the hex-hole filter support with the strand-mesh
  design (later finalised as filter support V5) and reworked the base for
  watertightness. The author's own printing note from this round is the
  source of the orientation guidance in [`printing.md`](printing.md): print
  the filter support on its smaller-diameter side, and print it
  separately, so bed adhesion does not distort the mesh's top layer.

Versions between and after these (V1.1 through V1.3, V5, V6 and V6.1) are
recorded only as the Onshape documents linked from
[`../hardware/onshape.md`](../hardware/onshape.md), the detailed
part-by-part rationale for each of those individual steps was not carried
into the handover as prose, so it is not reconstructed here.

## Converging the funnel–base fit

The funnel-to-base joint's tolerance was converged empirically: a series of
test rings was printed in **0.01 mm increments**, sweeping inner diameter
from **48.75 to 48.85 mm** and outer diameter from **52.6 to 52.925 mm**,
to find the clearance that seals without binding. Those test-ring files are
not shipped in this repository; they are prototyping artifacts, not part
of the product, but the method is recorded here so it can be repeated if
the fit ever needs re-tuning for a different printer or material.
