# NEMO Implementation Plan

This repository implements the multi-part NEMO pipeline for the 13-week plan.

## Current Implementation State

- External Python package scaffold is in `src/nemo`.
- Part registry and analytical evaluators are implemented for bracket, padeye,
  and stabilizer.
- Pure-Python bounded Nelder-Mead is implemented.
- CSV logging and JSON handshake helpers are implemented.
- Streamlit dashboard is implemented.
- Fusion add-in native generators are implemented for all three registered
  parts, including STEP/STL export and semantic boundary metadata.

## Completed Fusion CAD Reliability Work

- The bracket, padeye, and stabilizer generators each completed a baseline plus
  20-vector seeded geometry campaign with STEP and boundary metadata.
- The padeye generator now creates one explicitly joined solid, preserves the
  pin bore, applies deterministic lug-root fillets, and avoids tangent-only
  gusset contacts.
- The stabilizer generator now applies the root fillet before hollowing and
  limits fixed, pressure, and tip boundaries to their intended faces.
- The shared Fusion channel is serialized. Atomic response replacement retries
  transient Windows file locks, and timeouts report request/response state.

See `docs/VALIDATION_STATUS.md` for the recorded run identifiers and caveats.

## Remaining Interactive Fusion Work

- Re-import representative STEP files and compare volume within 0.5%.
- Create and manually solve the part-specific FEA studies.
- Confirm or reapply loads through the exported semantic boundary selectors.
- Validate the baseline and at least three finalists for each new part.

The future Gmsh/CalculiX interface is specified in
`docs/OPEN_FEA_CONTRACT.md`; it is not implemented in this stage.
