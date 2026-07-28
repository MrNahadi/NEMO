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
| candidate_01 | 0.115924 | 3.01607 | 0.271408 |  |  |  |  |  |  |
| candidate_02 | 0.117184 | 3.06595 | 0.257521 |  |  |  |  |  |  |
| candidate_03 | 0.117782 | 3.17877 | 0.246631 |  |  |  |  |  |  |
| candidate_04 | 0.117839 | 3.10555 | 0.257342 |  |  |  |  |  |  |
| candidate_05 | 0.11887 | 3.38513 | 0.221948 |  |  |  |  |  |  |

A candidate passes if Fusion confirms:

- factor of safety >= 3.0
- max deflection <= 0.4 mm

Use the final report wording: best design found within this parameterized search.
