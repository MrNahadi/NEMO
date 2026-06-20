# Fusion API Spike Log

Use this file during Weeks 1-4 to record evidence, failures, and decisions.

## Week 1 - API Smoke Test

- Goal: run a trivial Fusion Script/Add-in.
- Evidence to capture: screenshot, script path, Fusion version, whether it ran from the repository or copied add-in folder.

## Week 3 - Parameter Update Test

- Goal: prove `request.json` can update all six named user parameters.
- Required user parameter names:
  - `baseplate_length`
  - `baseplate_width`
  - `baseplate_thickness`
  - `rib_height`
  - `rib_thickness`
  - `fillet_radius`
- Evidence to capture: before/after parameter table, mass change, `response.json`.

## Week 4 - FEA Automation Go/No-Go

- Goal: determine whether Fusion Simulation solve/result extraction is reliable enough for full automation.
- Attempted approach:
  - Existing FEA study manually created in Fusion.
  - Add-in updates parameters and recomputes geometry.
  - Try API or text-command routes to trigger solve and read stress/FOS/deflection.
- Decision rule:
  - Continue full automation only if solve and result extraction work repeatedly.
  - Switch to analytical optimization plus manual Fusion validation if not.

## Decision Memo

Date:

Outcome:

Evidence:

Next action:
