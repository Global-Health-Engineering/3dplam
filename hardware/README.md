# hardware

Licensed **CERN-OHL-S v2** (see `../LICENSE-CERN-OHL-S-2.0.md`).

## What to print

Three parts make one manifold. All print **without support structures**.

| Part | File | Envelope | Material used |
|---|---|---|---|
| Base | `stl/base-v1.3.stl` | 77.0 × 77.0 × 38.7 mm | 39.7 cm³ solid |
| Funnel | `stl/funnel-v6.1.stl` | 71.8 × 71.7 × 55.5 mm | 16.0 cm³ solid |
| Filter support | `stl/filter-support-v5.stl` | 37.3 × 37.3 × 2.9 mm | 1.4 cm³ solid |

In ABS at the recommended settings the set costs about **$0.80**, weighs
about **32 g**, and prints in about **100 minutes**.

**Print settings are not optional.** The manifold must be gas-tight or the
syringe cannot pull a vacuum. See [`print-profiles/`](print-profiles/).

## Variants

| Variant | When to use it |
|---|---|
| `stl/filter-support-v5.stl` | **Default.** In-air printed strand mesh, layers rotated 120°. Uses 35% less material than V1.2 |
| `stl/filter-support-v1.2.stl` | Hexagonal hole pattern. More forgiving — no in-air bridging. Use if V5 prints poorly |
| `stl/funnel-v6.1.stl` | **Default.** Seals against the base by clamping the membrane |
| `stl/funnel-v6.1-tape-fit.stl` | Bore ~0.1 mm larger, for a base joint sealed with electrical tape |
| `rpet/*.stl` | **Required** when printing in recycled PET — shrinkage-compensated geometry |

The base needs no rPET compensation: the rPET base file in the source CAD
is byte-identical to the standard one, so `stl/base-v1.3.stl` is correct for
every material.

The base's top connection also accepts **commercial Millipore Microfil
funnels**, so an existing kit can be retrofitted with a printed base.

## Formats

| Directory | Contents |
|---|---|
| `stl/` | Printable meshes, **millimetres** |
| `step/` | Editable B-rep, for modification |
| `rpet/` | Shrinkage-compensated variants (STEP + STL) |
| `assembly/` | Reference assembly — not a printable part |
| `print-profiles/` | Slicer settings for a gas-tight print (pending) |

`hardware/3mf/` (Bambu Studio project files with the print profile embedded)
is not part of this release — generating it requires the Bambu Studio GUI
and has been deferred.

## Units

Every STL here is in millimetres and is checked in CI:

```bash
python3 -m tools.verify_units "hardware/**/*.stl"
```

STEP files declare `SI_UNIT(.METRE.)` and are handled correctly by CAD
tools without modification.
