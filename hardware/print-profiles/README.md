# Print profiles

At stock wall and shell counts, the printed manifold is porous. The syringe
then draws air through the material instead of pulling water through the
membrane, and filtration fails.

## Required settings

The author used these settings for the validated prints and confirmed them
as the final profile. The Bambu Studio process profiles in
this directory implement them exactly.

| Setting | Value | Changed from stock? |
|---|---|---|
| Base profile | `0.20mm Standard @BBL X1C` / `@BBL P2S` | n/a |
| Filament | ABS | n/a |
| Layer height | 0.20 mm | no |
| Wall loops | **6** | yes (stock 2) |
| Top shell layers | **6** | yes (stock 5) |
| Bottom shell layers | **6** | yes (stock 3) |
| Top / bottom surface pattern | Monotonic | n/a |
| Top / bottom surface density | 100 % | n/a |
| Sparse infill | 15 % grid | no |
| Nozzle | 0.4 mm | no |
| Supports | off | no |
| Brim | 5 mm auto-brim | no |

Everything else can stay at your slicer's defaults for the material.

## Any slicer

The requirement is geometric, so it applies in any slicer. Print at least
6 perimeter loops, and top and bottom shells of at least 6 solid layers
each.

| Bambu Studio | PrusaSlicer / OrcaSlicer | Cura |
|---|---|---|
| Wall loops = 6 | Perimeters = 6 | Wall Line Count = 6 |
| Top shell layers = 6 | Top solid layers = 6 | Top Layers = 6 |
| Bottom shell layers = 6 | Bottom solid layers = 6 | Bottom Layers = 6 |

## Printers used

The validated parts were all printed on the X1 Carbon. The P2S was used
only for tolerance test prints, so the P2S profile has not been checked
for gas-tightness. Before relying on the P2S profile, check one printed
base. Glue in the syringe tip, seal the top of the water channel, submerge
the base and push air in with the syringe. No bubbles should leave the
walls.

| Printer | Where | Notes |
|---|---|---|
| Bambu Lab X1 Carbon | ETH GHE lab | Enclosed, required for ABS and ASA. Used for the validated prints |
| Bambu Lab P2S | Author's own | Enclosed. Used for tolerance test prints only |

## Materials

| Material | Enclosure needed | Notes |
|---|---|---|
| **ABS** | Yes | Recommended. Best heat and mechanical performance |
| ASA | Yes | Equivalent to ABS; less widely available |
| PETG | No | Viable below ~80 °C. Widely available |
| rPET | No | Sustainable route; see [`../../docs/rpet.md`](../../docs/rpet.md). **Use the `rpet/` geometry** |
| PLA | No | Not recommended: 60 °C glass transition, and it absorbs water |

## Files

| File | Use |
|---|---|
| `3dplam-x1c-abs.json` | Bambu Studio process profile, X1 Carbon, ABS |
| `3dplam-p2s-abs.json` | Bambu Studio process profile, P2S, ABS |

Import a `.json` with *Preset → Process → Import*, then apply the
**3DPLAM gas-tight** process preset to each part before slicing.
