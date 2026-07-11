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

## Remaining Interactive Fusion Work

- Run the baseline and 20-vector geometry sweep for padeye and stabilizer.
- Re-import representative STEP files and compare volume within 0.5%.
- Create and manually solve the part-specific FEA studies.
- Confirm or reapply loads through the exported semantic boundary selectors.
- Validate the baseline and at least three finalists for each new part.

The future Gmsh/CalculiX interface is specified in
`docs/OPEN_FEA_CONTRACT.md`; it is not implemented in this stage.
