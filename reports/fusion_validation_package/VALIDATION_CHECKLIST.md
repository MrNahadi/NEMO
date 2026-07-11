# Fusion Validation Checklist

Use these candidates for manual Fusion FEA validation after the analytical fallback optimization.

For each candidate:

1. Copy its request JSON into `data/runs/active/request.json`.
2. Let `NEMOBridge` update the CAD model and return mass.
3. Switch to Simulation and solve the existing Static Stress study manually.
4. Record Fusion mass, max stress, FOS, and max deflection in the table below.

| Candidate | Analytical mass kg | Analytical FOS | Analytical deflection mm | Fusion mass kg | Fusion max stress MPa | Fusion FOS | Fusion deflection mm | Pass? | Notes |
| :-- | --: | --: | --: | --: | --: | --: | --: | :-- | :-- |
| baseline | 0.418125 | 6.64547 | 0.195642 |  |  |  |  |  |  |
| candidate_01 | 0.112593 | 2.59651 | 0.361093 |  |  |  |  |  |  |
| candidate_02 | 0.112624 | 2.5434 | 0.380334 |  |  |  |  |  |  |
| candidate_03 | 0.11265 | 2.52086 | 0.379276 |  |  |  |  |  |  |
| candidate_04 | 0.112677 | 2.54773 | 0.384354 |  |  |  |  |  |  |
| candidate_05 | 0.112698 | 2.57399 | 0.366518 |  |  |  |  |  |  |

A candidate passes if Fusion confirms:

- factor of safety >= 2.5
- max deflection <= 0.5 mm

Use the final report wording: best design found within this parameterized search.
