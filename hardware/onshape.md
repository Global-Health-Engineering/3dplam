# Source CAD

The 3DPLAM was designed in Onshape. The final release is **Version 1.3**.

| Release | Onshape document |
|---|---|
| **V1.3 — final** | https://cad.onshape.com/documents/9c3be81daa349a1904cb00f1/w/5660800de7ba8d6695e60895/e/a83cd824ff588ff52e4f649e |
| V1.2 | https://cad.onshape.com/documents/cc20d4ec22f9088750210c42/w/0e880b61cc5e7c90556c6865/e/dbc668c40067b012e6ab6d83 |
| V1.1 | https://cad.onshape.com/documents/f801fbb0321c453f9c16f913/w/61b23730d0b0da70c58e73fb/e/2103c2cb395ca177d83f17ff |
| V1 | https://cad.onshape.com/documents/11c201fe990ce71963c1da1f/w/9d105bc18fde2b3904227e07/e/3f871e498b6d1c555ab20b40 |
| V4 | https://cad.onshape.com/documents/24049122eabfba62501a99af/w/74a5825aa0f90a2ec52c1f36/e/ca44f4b7be708372fe5ca992 |
| V5 | https://cad.onshape.com/documents/599c0ab54dcc39d4fc071814/w/90ee3f322e9631dcc08f3d15/e/5e6778bb707451aec7bab47e |
| V6 | https://cad.onshape.com/documents/3b9ea3bf7c7b1278aed5f8f5/w/090c9d0f8b93f5252407cc8b/e/e49eef2a68eaec678b639688 |

## Re-exporting

**Set `Units` to `Millimeter`.** Onshape's original exports for this project
were in metres. STEP and 3MF record their units so they survive; STL does
not, and a metre-scale STL imports into any slicer 1000x too small.

| Format | Setting |
|---|---|
| STL | Binary · **Units: Millimeter** · Resolution: Fine (or Custom, chord tolerance 0.01 mm) |
| STEP | AP242 (AP214 for older tools) · **Units: Millimeter** |

Do not export 3MF from Onshape — `hardware/3mf/` files are generated in
Bambu Studio so they carry the print profile. See `hardware/print-profiles/`.

After any re-export, run:

```bash
python3 -m tools.verify_units "hardware/**/*.stl"
```
