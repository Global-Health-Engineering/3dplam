# Print profiles

At stock wall and shell counts the printed manifold is porous: the syringe
draws air through the material instead of pulling water through the
membrane, and filtration fails.

## Required settings

These values are transcribed directly from the author's Bambu Studio
screenshot of the profile used for the validated prints (a file named
*"Bambu Studio Settings for airtight print"*). They are pending final
confirmation from the author, but are stated here plainly because they are
what was actually printed and tested — not a paraphrase.

| Setting | Value | Changed from stock? |
|---|---|---|
| Base profile | `0.20mm Standard @BBL X1C` / `@BBL P2S` | — |
| Filament | ABS | — |
| Layer height | 0.2 mm | no |
| Wall loops | **6** | yes (stock 2) |
| Top shell layers | 5 | **no — stock default** |
| Top shell thickness | **1.3 mm** | yes |
| Bottom shell layers | **6** | yes (stock 3) |
| Bottom shell thickness | **1.3 mm** | yes |
| Top / bottom surface pattern | Monotonic | — |
| Top / bottom surface density | 100% | — |
| Sparse infill | 15% grid | no |
| Nozzle | 0.4 mm | no |
| Supports | off | no |
| Brim | 5 mm auto-brim | no |

### Layer count and thickness

Bambu Studio treats shell **layer count** (`top_shell_layers` /
`bottom_shell_layers`) and shell **thickness**
(`top_shell_thickness` / `bottom_shell_thickness`) as independent
constraints, and slices whichever one demands more material at the current
layer height. At 0.2 mm layers, a thickness of 1.3 mm forces roughly 7
solid layers regardless of what the layer-count field says — which is why
`top_shell_layers` is left at its stock value of 5 and the thickness field
does the real work.

This also reconciles the thesis, which describes the requirement in prose
as *"a wall and shell thickness of 6 layers."* That is a paraphrase of a
setting that was actually authored as a millimetre thickness, not a raw
layer count. The screenshot is the primary source; the numbers above are
transcribed from it.

Everything else can stay at your slicer's defaults for the material.

## Any slicer

The requirement is geometric, not vendor-specific: at least 6 perimeter
loops, and a top/bottom shell of at least ~1.3 mm (about 6–7 layers at
0.2 mm layer height).

| Bambu Studio | PrusaSlicer / OrcaSlicer | Cura |
|---|---|---|
| Wall loops = 6 | Perimeters = 6 | Wall Line Count = 6 |
| Top shell thickness = 1.3 mm (layers stay at 5) | Top minimum shell thickness = 1.3 mm | Top Thickness = 1.3 mm |
| Bottom shell layers = 6, thickness = 1.3 mm | Bottom solid layers = 6 (or bottom minimum shell thickness = 1.3 mm) | Bottom Layers = 6 (or Bottom Thickness = 1.3 mm) |

If your slicer only exposes a layer-count field and no thickness field,
round up: use 7 top layers and 7 bottom layers at 0.2 mm to guarantee at
least 1.3 mm of solid shell.

## Printers used

Both machines produced working parts: the design is not tied to a single
printer.

| Printer | Where | Notes |
|---|---|---|
| Bambu Lab X1 Carbon | ETH GHE lab | Enclosed — required for ABS and ASA. Used for the validated prints |
| Bambu Lab P2S | Author's own | Enclosed |

## Materials

| Material | Enclosure needed | Notes |
|---|---|---|
| **ABS** | Yes | Recommended. Best heat and mechanical performance |
| ASA | Yes | Equivalent to ABS; less widely available |
| PETG | No | Viable below ~80 °C. Widely available |
| rPET | No | Sustainable route — see [`../../docs/rpet.md`](../../docs/rpet.md). **Use the `rpet/` geometry** |
| PLA | No | Not recommended: 60 °C glass transition, and it absorbs water |

## Files

| File | Use |
|---|---|
| `3dplam-x1c-abs.json` | Bambu Studio process profile, X1 Carbon, ABS |
| `3dplam-p2s-abs.json` | Bambu Studio process profile, P2S, ABS |

Import a `.json` with *Preset → Process → Import*. See
[Generating ready-to-slice 3MF projects](#generating-ready-to-slice-3mf-projects)
below for a bundled alternative — not yet shipped.

## Generating ready-to-slice 3MF projects

Not yet shipped. To add them:

1. *Preset → Process → Import* → `3dplam-x1c-abs.json`
2. For each part in `../stl/`: open it, apply the **3DPLAM gas-tight**
   process preset, confirm the object measures in tens of millimetres, then
   *File → Export → Export Project* to `../3mf/<same-name>.3mf`
3. Verify each export carries its settings — geometry-only exports are the
   defect this repository exists to avoid:

```bash
for f in hardware/3mf/*.3mf; do
  n=$(unzip -l "$f" | grep -c "project_settings.config")
  echo "$n  $f"
done
```

Every line must read `1`. A `0` means it was exported as geometry, not a
project, and carries no print settings.
