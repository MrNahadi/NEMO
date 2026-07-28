# Validation Plan

## Multi-Part Baseline Validation

1. Build the baseline Fusion bracket with the documented user parameters.
2. Assign Aluminum 6061-T6.
3. Apply the 1471.5 N vertical load.
4. Fix the bolt-hole/base faces.
5. Solve the static stress study with a medium mesh.
6. Record mass, max stress, FOS, and max deflection.
7. Compare against the analytical baseline from `nemo evaluate`.

Repeat the process with `--part padeye` and `--part stabilizer`, using each
part's generated validation checklist and boundary metadata. The padeye applies
14.715 kN at `pin_bearing`; the stabilizer applies 11.808 kN across four
pressure bands and monitors `tip_monitor`.

## Candidate Validation

If Fusion FEA automation works, validate the final automated optimum manually in Fusion.

If the project uses the analytical fallback, validate:

- the baseline design,
- the best feasible analytical design,
- the next 2-4 lightest feasible analytical candidates.

Generated packages:

- `demos/bracket-proof-of-concept/validation/legacy-aggressive`: original
  bracket candidates selected with analytical FOS >= 2.5 and deflection
  <= 0.5 mm.
- `demos/bracket-proof-of-concept/validation/legacy-conservative`: original
  bracket backup candidates selected with analytical FOS >= 3.0 and deflection
  <= 0.4 mm.

Use the aggressive package first. If Fusion shows the analytical model is optimistic and the lightest candidates fail, validate the conservative package next.

## Acceptance Criteria

- Every final candidate satisfies FOS >= 2.5 in Fusion.
- Bracket and padeye candidates satisfy deflection <= 0.5 mm in Fusion.
- Stabilizer candidates satisfy tip deflection <= 5.0 mm in Fusion.
- Report states the percent difference between analytical and Fusion values.
- Final claim uses this wording: "best design found within this parameterized search."

## CAD Generator Acceptance

- Generate the baseline and 20 seeded Latin-hypercube vectors per registered
  part.
- Require a healthy Fusion timeline, positive volume, and successful STEP plus
  boundary-sidecar export for every vector.
- Re-import one baseline and one extreme candidate per part; require volume
  agreement within 0.5%.
- Because the generator rebuilds its component to ensure all values affect the
  solid, verify or reapply simulation references before every manual solve.
