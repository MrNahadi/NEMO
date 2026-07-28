# Analytical Baseline Screening Results

Regenerated and verified on 2026-07-28 using schema version 2.

These values are first-order analytical screening estimates. They are not
certified engineering results and do not replace calibrated FEA, design-code
checks, verified loads and materials, or qualified engineering review.

| Part | Mass (kg) | Max stress (MPa) | FOS | Max deflection (mm) | Volume (m³) |
| :-- | --: | --: | --: | --: | --: |
| Bracket | 0.418125 | 41.532074 | 6.645466 | 0.195642 | 0.000154861 |
| Padeye | 8.847625 | 46.107000 | 5.964387 | 0.013429 | 0.001127086 |
| Stabilizer | 19.655593 | 86.985255 | 3.172952 | 3.336750 | 0.007279849 |

Regenerate the current values from the repository root:

```powershell
.\.venv\Scripts\nemo.exe evaluate --part bracket
.\.venv\Scripts\nemo.exe evaluate --part padeye
.\.venv\Scripts\nemo.exe evaluate --part stabilizer
```
