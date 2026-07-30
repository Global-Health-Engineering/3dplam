# tools

Every derived artifact in this repository regenerates from these scripts.
No figure is a one-off screenshot.

| Script | Regenerates |
|---|---|
| `stl_units.py` | STL geometry primitives (library) |
| `verify_units.py` | CI gate — fails if any STL is not in millimetres |
| `risk.py` | WHO risk bands and the 5% threshold rule (library) |
| `tidy_data.py` | `data/*.csv` from the handover spreadsheets |
| `plot_validation.py` | `site/public/figures/validation.svg` |
| `render_parts.py` | `site/public/renders/*.png` (requires Blender) |

```bash
pip install -r requirements.txt
python3 -m pytest tools/tests -v
```
