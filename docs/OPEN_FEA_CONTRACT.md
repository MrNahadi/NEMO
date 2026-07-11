# Open FEA Evaluator Contract

NEMO reserves `mode: "open_fea"` for a later Gmsh/CalculiX implementation. The
current evaluator returns a controlled failure for this mode instead of
fabricating structural results.

## Inputs

- Schema-v2 `EvaluationRequest` with `part_id` and unit-aware `parameters`.
- A STEP file exported from the same Fusion request.
- A `.boundaries.json` sidecar containing semantic roles, face signatures, and
  geometric selectors.
- The registered part material, load, and constraint definitions.

## Boundary Mapping

The meshing adapter must import STEP through Gmsh's OpenCASCADE interface and
match faces using centroid, area, normal, and bounding-box tolerances. Required
roles are:

- bracket: `fixed_support`, `equipment_load`;
- padeye: `fixed_support`, `pin_bearing`;
- stabilizer: `fixed_support`, `pressure_band_1..4`, `tip_monitor`.

Stabilizer pressures use relative weights `1.00, 0.93, 0.75, 0.40`. The adapter
must normalize pressure by the matched band areas so the total resultant is
11.808 kN.

## Output

The evaluator must return the existing schema-v2 `EvaluationResponse` fields:

- `volume_m3` and `mass_kg`;
- maximum von Mises stress in MPa;
- material-yield factor of safety;
- maximum monitored deflection in mm;
- the part-specific penalized objective;
- artifact paths for mesh, solver input, raw result, and diagnostic log.

Geometry, meshing, non-convergence, missing boundary matches, and solver errors
must return `status: "failed"` with objective `1e9` and must not terminate an
optimization run.
