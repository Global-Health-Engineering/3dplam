# Operating the manifold

This page gives the complete *E. coli* membrane-filtration protocol used for
the validation reported in [`validation.md`](validation.md). The protocol
comes from our lab documentation (`Functional Testing/E. coli Quantification_README.txt`
in the project handover; reproduced in the thesis, Appendix B). It assumes
the manifold is already built, so read [`assembly.md`](assembly.md) first.

## Consumables

| Item | Spec / supplier |
|---|---|
| Membrane filter | 47 mm, 0.45 µm nitrocellulose mixed-ester (MCE), ADVANTEC A045H047Y |
| Culture plate | Compact Dry™ ECO, Shimadzu Diagnostics |
| Sample-pull syringe | 100 mL PVC |
| Forceps | for membrane handling |
| Disinfecting wipes | 70 % isopropyl alcohol, 60 × 30 mm |
| Disinfectant | 70 % ethanol (hands, forceps) |

Step 7 also uses a sterile 1 mL disposable syringe to draw the plate
inoculum out of the funnel.

## Filtration workflow

1. Disinfect hands using 70 % ethanol.
2. Sterilize the upper surface of the filter support and the inner surface
   of the funnel using a 70 % isopropyl alcohol wipe (60 mm x 30 mm).
3. Disinfect the forceps using pure ethanol and a flame (a 70 % isopropyl
   alcohol wipe can also be used for this step).
4. Place the filter membrane, gridded side up, on top of the filter support
   using the forceps.
5. Lock the funnel onto the base.
6. Shake the sample thoroughly and fill the funnel up to the 100 mL mark.
7. Extract 1 mL of the sample from the funnel using a sterile 1 mL
   disposable syringe and inoculate the Compact Dry™ ECO plate.
8. Operate the 100 mL syringe to pull the entire water sample through the
   filter membrane.
9. Remove the funnel.
10. Disinfect the forceps again (repeating step 3).
11. Transfer the filter membrane using the forceps, placing it gridded side
    up onto the same Compact Dry™ ECO plate.
12. Dry the funnel, filter support, and any remaining wet surfaces using a
    paper towel.

## Incubation and reading

Incubate the inoculated Compact Dry™ ECO plate for **24 h at 37 °C**, then
count colonies. [`validation.md`](validation.md) describes how those counts
become a WHO risk classification. That page covers the 0.5 CFU/100 mL
convention for "no colonies," the risk bands, and the 5 % boundary-tolerance
rule.

## Notes from the source protocol

Two of the eight validation samples needed special handling. Sample 5
stalled at roughly the 20 mL mark of step 8 (~80 mL actually pulled
through). Sample 7 is a positive control (1,250 mL of tap water spiked with
25 mL of a faecal suspension) and not a field sample. Both notes carry
through unchanged into [`data/README.md`](../data/README.md).
