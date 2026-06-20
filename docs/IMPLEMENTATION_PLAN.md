# NEMO Implementation Plan

This repository implements the project scaffold for the 13-week NEMO plan.

## Current Implementation State

- External Python package scaffold is in `src/nemo`.
- Analytical fallback evaluator is implemented.
- Pure-Python bounded Nelder-Mead is implemented.
- CSV logging and JSON handshake helpers are implemented.
- Streamlit dashboard is implemented.
- Fusion add-in bridge scaffold is implemented for parameter updates, recompute, and mass extraction.

## Remaining Fusion Work

- Build the actual Fusion CAD model.
- Add exact user parameters with the names listed in `docs/API_SPIKE_LOG.md`.
- Create the manual FEA study template.
- Test whether Simulation solve/result extraction can be automated.
- Validate final candidates in Fusion.
