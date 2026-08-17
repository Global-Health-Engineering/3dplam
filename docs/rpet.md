# Filament from PET bottles

rPET (recycled PET, from used drinking-water bottles) is one of the five
materials the manifold was tested in; see the materials matrix in
[`printing.md`](printing.md) and its role in the *E. coli* validation in
[`validation.md`](validation.md). This page covers turning bottles into
filament.

## Credit

The filament-making machine used is a rebuild of **Petamentor2**, an
open-source PET-bottle-to-filament machine designed by **Ondřej Šraitr**:
<https://petamentor2.com/>. The author of this project built a Petamentor2
himself; he did not design the machine. Its design files are Šraitr's
work and are deliberately **not** redistributed in this repository; build
your own from the upstream project.

## The route: bottle to filament

A clean PET bottle is fed into the machine, which cuts it into a single
continuous strand and draws that strand through a heated nozzle (roughly
**185 °C**) to re-form it at filament gauge, winding the output onto a
spool turning at roughly **1 rpm**.

**Splicing strands together is unreliable in practice.** Joining the end
of one bottle's strand to the next tends to produce a weak point that
snaps under tension later, mid-print. The practical approach: feed a
single strand from a single bottle, and let the print stop (the printer's
filament runout sensor will pause it) rather than trying to splice a
second strand in to continue. Restart with the next bottle's strand once
the previous spool runs out.

## Print settings

rPET's shrinkage and thermal behaviour differ enough from ABS that the
gas-tight profile in
[`../hardware/print-profiles/README.md`](../hardware/print-profiles/README.md)
does not directly carry over. Print settings for rPET come from
**Sustainable Design Studio**:
<https://www.sustainabledesign.studio/filamentmaker-printsettings>; use
that page as the source for slicer settings when printing in rPET, rather
than the ABS profile shipped here.

## rPET geometry

rPET parts are printed from [`../hardware/rpet/`](../hardware/rpet/), not
[`../hardware/stl/`](../hardware/stl/). rPET shrinks differently during
cooling than ABS or PLA, so the funnel and filter support geometry in
`rpet/` is dimensionally compensated for that shrinkage; the standard STL
printed in rPET will not fit. There is no separate rPET base: the base
needs no compensation, so the same [`base.stl`](../hardware/stl/base.stl)
is correct in every material, including rPET.
