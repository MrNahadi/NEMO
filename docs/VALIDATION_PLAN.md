# Validation Plan

## Baseline Validation

1. Build the baseline Fusion bracket with the documented user parameters.
2. Assign Aluminum 6061-T6.
3. Apply the 1471.5 N vertical load.
4. Fix the bolt-hole/base faces.
5. Solve the static stress study with a medium mesh.
6. Record mass, max stress, FOS, and max deflection.
7. Compare against the analytical baseline from `nemo evaluate`.

## Candidate Validation

If Fusion FEA automation works, validate the final automated optimum manually in Fusion.

If the project uses the analytical fallback, validate:

- the baseline design,
- the best feasible analytical design,
- the next 2-4 lightest feasible analytical candidates.

## Acceptance Criteria

- Final candidate satisfies FOS >= 2.5 in Fusion.
- Final candidate satisfies deflection <= 0.5 mm in Fusion.
- Report states the percent difference between analytical and Fusion values.
- Final claim uses this wording: "best design found within this parameterized search."
