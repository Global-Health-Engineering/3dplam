# hardware

Licensed **CERN-OHL-S v2** (see `../LICENSE-CERN-OHL-S-2.0.md`).

## Printable parts

Three parts make one manifold. All print **without support structures**.

| Part           | File                                 | Envelope                    | Solid volume   |
| -------------- | ------------------------------------ | --------------------------- | -------------- |
| Base           | `stl/base.stl`                       | 77.0 mm x 77.0 mm × 38.7 mm | 39.7 cm³ solid |
| Funnel         | `stl/funnel.stl`                     | 71.8 mm × 71.8 mm × 55.5 mm | 16.0 cm³ solid |
| Filter support | `stl/filter-support-strand-mesh.stl` | 37.3 mm × 37.3 mm × 2.9 mm  | 1.4 cm³ solid  |

In ABS at the recommended settings, the set costs about $1.30 and weighs about 52 g. The set prints in about 100 minutes.

A part sliced at default settings looks correct but is not gas-tight. The syringe cannot pull a vacuum through it, and filtration fails. The required
settings are **6 wall loops, 6 top shell layers, and 6 bottom shell layers, at a 0.20 mm layer height**. The joint tolerances assume these settings. Importable Bambu Studio profiles for the X1 Carbon and P2S are in [`print-profiles/`](print-profiles/), along with the full requirement and cross-slicer equivalents.

## Filter support variants

Two designs are current, and they are alternatives to each other.

| File                             | Use it when |
| -------------------------------- | ----------- |
| `filter-support-strand-mesh.stl` | **Default.** Parallel in-air printed strands, each layer rotated 120°. Uses 35 % less material, and gave uniform filtration in testing. This is the design used for the *E. coli* validation |
| `filter-support-hex-hole.stl`    | Hexagonal hole pattern. More forgiving to print, because it needs no in-air bridging. Filtration is not uniform. In an ink test, water passed only through the membrane above the holes, in a hexagonal pattern. The smaller effective area would make colonies denser and harder to count. Use only if the strand mesh prints poorly on your machine |

## Funnel variants

| File                  | Use it when                                                                                                        |
| --------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `funnel.stl`          | **Default.** Seals against the base by clamping the membrane between the base's raised edge and the funnel's slope |
| `funnel-tape-fit.stl` | Bore ~0.1 mm larger, for a base joint sealed with electrical tape instead |

## Printing in recycled PET

Recycled-PET funnels and filter supports are printed from `rpet/`. Their geometry there is shrinkage-compensated and is not interchangeable with `stl/`.

There is no rPET base. The base needs no compensation, so `stl/base.stl` is correct for every material. Take the base from `stl/`, and the funnel and filter support from `rpet/`.

See [`../docs/rpet.md`](../docs/rpet.md) for producing filament from PET bottles.

## Retrofitting a commercial funnel

The base's top connection also accepts commercial Millipore Microfil funnels, so an existing kit can be used with a printed base.

## Directories

| Directory         | Contents                                                     |
| ----------------- | ------------------------------------------------------------ |
| `stl/`            | Printable meshes, millimetres                                |
| `step/`           | Editable B-rep: modify the design here                      |
| `rpet/`           | Shrinkage-compensated variants for recycled PET (STL + STEP) |
| `assembly/`       | Reference assembly: **not** a printable part                |
| `print-profiles/` | Slicer settings for a gas-tight print                        |

## Versions

Filenames carry no version numbers. These files are the current release, and git records their history. The shipped revisions are base V1.3, funnel V6.1, and filter supports V5 (strand mesh) and V1.2 (hex hole). [`../docs/design-history.md`](../docs/design-history.md) records these revisions and what changed between them.

Source CAD lives in Onshape and is public. [Open the design](https://cad.onshape.com/documents/85e843dab749166d5c0b6f2d/w/d2011a4cf432978d33b486bf/e/728e4b207954dc08243541f4) and use *Make a copy* to get your own editable document. See [`onshape.md`](onshape.md) for every version and for the export settings that keep units in millimetres.

## Units

Every STL here is in millimetres. CI checks the units with:

```bash
python3 tools/verify_units.py "hardware/**/*.stl"
# or: python3 -m tools.verify_units "hardware/**/*.stl"
```

STEP files declare `SI_UNIT(.MILLI.,.METRE.)` and need no conversion.
