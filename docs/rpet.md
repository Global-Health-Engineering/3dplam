# Filament from PET bottles

rPET (recycled PET, from used drinking-water bottles) is one of the five
materials the manifold was tested in. The materials matrix in
[`printing.md`](printing.md) compares it with the other materials, and
[`validation.md`](validation.md) describes its role in the *E. coli*
validation. This page covers turning bottles into filament.

## Credit

The filament-making machine used is a rebuild of Petamentor2, an
open-source PET-bottle-to-filament machine designed by Ondřej Šraitr
(<https://petamentor2.com/>). We built a Petamentor2 ourselves and did not
design the machine. Its design files are Šraitr's work, and this repository
deliberately does not redistribute them. To build your own, start from the
upstream project.

## The route: bottle to filament

A clean PET bottle is fed into the machine, which cuts it into a single
continuous strand. The machine draws that strand through a heated nozzle
(roughly **185 °C**) to re-form it at filament gauge. The output winds onto
a spool turning at roughly **1 rpm**.

Splicing strands together is unreliable in practice. Joining the end of one
bottle's strand to the next tends to produce a weak point, which later
snaps under tension mid-print. Instead, feed a single strand from a single
bottle and let the print stop (the printer's filament runout sensor will
pause it). Do not try to splice a second strand in to continue. Restart
with the next bottle's strand once the previous spool runs out.

## Print settings

rPET's shrinkage and thermal behaviour differ enough from ABS that the
gas-tight profile in
[`../hardware/print-profiles/README.md`](../hardware/print-profiles/README.md)
does not directly carry over. Print settings for rPET come from Sustainable
Design Studio (<https://www.sustainabledesign.studio/filamentmaker-printsettings>).
When printing in rPET, use that page as the source for slicer settings
instead of the ABS profile shipped here.

## rPET geometry

rPET parts are printed from [`../hardware/rpet/`](../hardware/rpet/), not
[`../hardware/stl/`](../hardware/stl/). rPET shrinks differently during
cooling than ABS or PLA. The funnel and filter support geometry in `rpet/`
is therefore dimensionally compensated for that shrinkage, and the standard
STL printed in rPET will not fit. There is no separate rPET base. The base
needs no compensation, so the same [`base.stl`](../hardware/stl/base.stl)
is correct in every material, including rPET.
