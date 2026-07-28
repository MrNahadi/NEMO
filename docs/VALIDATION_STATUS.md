# Validation Status

This page records completed engineering-software checks separately from the
manual structural validation that remains. CAD success is not FEA compliance or
approval for manufacture.

## Evidence recorded on 2026-07-28

- Generator version: `2.4`.
- Offline suite: 27 passed, 3 Fusion-only cases skipped.
- Every recorded CAD vector produced positive volume, a STEP file, boundary
  metadata, and at least one face for every required semantic role.

| Part | Fusion run | CAD vectors | Result |
|---|---|---:|---|
| Bracket | `fusion_smoke_bracket_20260728_200138_794580` | 21/21 | Pytest Fusion case passed in 238.19 s. |
| Padeye | `fusion_smoke_padeye_20260728_192200_719655` | 21/21 | Pytest Fusion case passed in 157.19 s. |
| Stabilizer | `fusion_smoke_stabilizer_20260728_192450_494398` | 21/21 | Fusion completed all artifacts; the outer pytest process reached its 30-minute limit while reading the final response, so the directory was audited directly. |

The padeye metadata selected exactly one `fixed_support` face throughout its
sweep. The stabilizer metadata selected exactly one `fixed_support` face and one
`tip_monitor` face throughout. Each stabilizer pressure band selected 24--48
external positive-Y skin faces, with no empty pressure roles.

The run artifacts are under `data/runs/active/artifacts/` and are generated local
evidence. They are excluded from version control.

The corrected analytical models were then rerun with 60 seeded samples and
three bounded Nelder-Mead starts per part. Fresh baseline plus five-finalist
packages are available locally at:

- `reports/final_20260728_bracket_validation/`;
- `reports/final_20260728_padeye_validation/`; and
- `reports/final_20260728_stabilizer_validation/`.

All 18 package requests then completed with generator version `2.4`. Each
response has `partial` status, positive CAD mass and volume, and existing STEP
and boundary files. No required boundary role was empty. Padeye and stabilizer
support selections remained one face per candidate; stabilizer tip selections
remained one face, and its pressure bands contained 24--47 external positive-Y
skin faces. Fusion CAD masses are recorded in the three checklists.

## Remaining validation

- Re-import one baseline and one extreme STEP file for each part and confirm
  volume agreement within 0.5%.
- Manually create calibrated Fusion Static Stress studies for the baseline and
  at least three finalists per part.
- Record material, mesh size and element count, loads, supports, reaction
  balance, maximum von Mises stress, minimum FOS, maximum displacement, and
  pass/fail status in each validation checklist.
- Calibrate analytical assumptions against the recorded Fusion results.

Until those items are complete, use only the claim "best design found within
this parameterized search," and describe all analytical results as screening
estimates.

## Version-control decision

Timestamped validation packages, STEP files, boundary exports, and incomplete
checklists are reproducible working evidence and remain local. Commit a
validation package only after a qualified reviewer completes its Fusion FEA
records and the package is intentionally curated as project evidence.
