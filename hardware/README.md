# hardware

Licensed **CERN-OHL-S v2** (see `../LICENSE-CERN-OHL-S-2.0.md`).

## Printable parts

Three parts make one manifold. All print **without support structures**.

| Part | File | Envelope | Material |
|---|---|---|---|
| Base | `stl/base.stl` | 77.0 × 77.0 × 38.7 mm | 39.7 cm³ solid |
| Funnel | `stl/funnel.stl` | 71.8 × 71.8 × 55.5 mm | 16.0 cm³ solid |
| Filter support | `stl/filter-support-strand-mesh.stl` | 37.3 × 37.3 × 2.9 mm | 1.4 cm³ solid |

In ABS at the recommended settings the set costs about **$0.80**, weighs
about **32 g**, and prints in about **100 minutes**.

A part sliced at default settings looks correct but is not gas-tight: the
syringe cannot pull a vacuum through it, and filtration fails. The required
settings are **6 wall loops, 6 bottom shell layers, and 1.3 mm top and
bottom shell thickness at 0.2 mm layer height**. Importable Bambu Studio
profiles for the X1 Carbon and P2S are in
[`print-profiles/`](print-profiles/), along with the full requirement and
cross-slicer equivalents.

## Filter support variants

Two designs are current; they are alternatives, not revisions.

| File | Use it when |
|---|---|
| `filter-support-strand-mesh.stl` | **Default.** Parallel in-air printed strands, each layer rotated 120°. Uses 35% less material, and gave uniform filtration in testing. This is the design used for the *E. coli* validation |
| `filter-support-hex-hole.stl` | Hexagonal hole pattern. More forgiving to print — no in-air bridging. Use if the strand mesh prints poorly on your machine |

## Funnel variants

| File | Use it when |
|---|---|
| `funnel.stl` | **Default.** Seals against the base by clamping the membrane between the base's raised edge and the funnel's slope |
| `funnel-tape-fit.stl` | Bore ~0.1 mm larger, for a base joint sealed with electrical tape instead |

## Printing in recycled PET

Recycled-PET parts are printed from `rpet/` in full; the geometry there is
shrinkage-compensated and is not interchangeable with `stl/`.

There is no rPET base: the base needs no compensation, so `stl/base.stl` is
correct for every material. The base is taken from `stl/`, and the funnel
and filter support from `rpet/`.

See [`../docs/rpet.md`](../docs/rpet.md) for producing filament from PET
bottles.

## Retrofitting a commercial funnel

The base's top connection also accepts **commercial Millipore Microfil
funnels**, so an existing kit can be used with a printed base.

## Directories

| Directory | Contents |
|---|---|
| `stl/` | Printable meshes, millimetres |
| `step/` | Editable B-rep — modify the design here |
| `rpet/` | Shrinkage-compensated variants for recycled PET (STL + STEP) |
| `assembly/` | Reference assembly — **not** a printable part |
| `print-profiles/` | Slicer settings for a gas-tight print |

`hardware/3mf/` — Bambu Studio projects with the profile embedded — is not
part of this release; generating those requires the Bambu Studio GUI.

## Versions

Filenames carry no version numbers: these files are the current release, and
git records their history. The shipped revisions are base V1.3, funnel V6.1,
and filter supports V5 (strand mesh) and V1.2 (hex hole) — recorded in
[`../docs/design-history.md`](../docs/design-history.md) along with what
changed between them.

Source CAD lives in Onshape; see [`onshape.md`](onshape.md).

## Units

Every STL here is in millimetres, checked in CI:

```bash
python3 tools/verify_units.py "hardware/**/*.stl"
# or: python3 -m tools.verify_units "hardware/**/*.stl"
```

STEP files declare `SI_UNIT(.MILLI.,.METRE.)` and need no conversion.
