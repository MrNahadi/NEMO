# Fusion Validation Checklist: Marine equipment mounting bracket

For each candidate:

1. Place its request JSON at `data/runs/active/request.json`.
2. Let `NEMOBridge` generate/update the native model and export STEP.
3. Confirm the named boundary faces, solve the Static Stress study manually, and record results.

| Candidate | Analytical mass kg | Analytical FOS | Analytical deflection mm | Fusion mass kg | Fusion max stress MPa | Fusion FOS | Fusion deflection mm | Pass? | Notes |
| :-- | --: | --: | --: | --: | --: | --: | --: | :-- | :-- |
| baseline | 0.418125 | 6.64547 | 0.195642 |  |  |  |  |  |  |
| candidate_01 | 0.126545 | 2.55302 | 0.475838 |  |  |  |  |  |  |
| candidate_02 | 0.126626 | 2.53653 | 0.480823 |  |  |  |  |  |  |
| candidate_03 | 0.126946 | 2.56253 | 0.480507 |  |  |  |  |  |  |
| candidate_04 | 0.127181 | 2.6659 | 0.441799 |  |  |  |  |  |  |
| candidate_05 | 0.127457 | 2.68296 | 0.43842 |  |  |  |  |  |  |

Pass criteria: FOS >= 2.5 and max deflection <= 0.5 mm.

Report wording: best design found within this parameterized search.
