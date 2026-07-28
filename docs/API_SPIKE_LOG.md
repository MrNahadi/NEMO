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

### Result - 2026-06-20

- Status: passed.
- Add-in path: `fusion_addin/NEMOBridge`.
- Handshake folder: `C:/Users/muigu/Documents/Projects/NEMO/data/runs/active`.
- Request file was detected by the add-in watcher.
- All six parameters were updated from `request.json`.
- Fusion recomputed the model.
- Mass was extracted through `rootComponent.getPhysicalProperties().mass`.
- `response.json` was written successfully with `status: "partial"`.
- Final bridge mass from iteration 4: `2.2010663662242984 kg`.
- Initial mass extraction failed because the active API exposed `physicalProperties` differently than expected; bridge was patched to support `rootComponent.getPhysicalProperties()`.
- A second failure occurred when Fusion was in Simulation workspace; bridge was patched to activate `FusionSolidEnvironment` before accessing `adsk.fusion.Design`.

### Parameter-Change Survival Check - 2026-06-20

- Tested parameters:
  - `baseplate_length = 180 mm`
  - `baseplate_width = 120 mm`
  - `baseplate_thickness = 10 mm`
  - `rib_height = 50 mm`
  - `rib_thickness = 7 mm`
  - `fillet_radius = 6 mm`
- Result: CAD geometry updated correctly.
- Simulation setup survived parameter change: yes.
- Loads still attached: yes.
- Constraints still attached: yes.
- Manual solve check: user confirmed everything is in order.

## Week 4 - FEA Automation Go/No-Go

- Goal: determine whether Fusion Simulation solve/result extraction is reliable enough for full automation.
- Attempted approach:
  - Existing FEA study manually created in Fusion.
  - Add-in updates parameters and recomputes geometry.
  - Try API or text-command routes to trigger solve and read stress/FOS/deflection.
- Decision rule:
  - Continue full automation only if solve and result extraction work repeatedly.
  - Switch to analytical optimization plus manual Fusion validation if not.

### Simulation API Inspection - 2026-06-20

- A Fusion script inspected `dir(adsk.fusion)` for names containing `sim`, `study`, `stress`, `result`, and `solve`.
- Result: no obvious Static Stress / Simulation study or result API objects were exposed.
- Returned names were limited to classes such as `Arrange3DResultEnvelope`, `ArrangeOccurrenceResult`, `AutoConstrainResult`, and `InterferenceResult`.
- Interpretation: the public Python API available in this Fusion install does not appear to expose direct Static Stress solve/result objects.
- Next action: probe `Application.executeTextCommand()` for any usable Simulation commands. If no stable text-command path is found, use analytical optimization plus manual Fusion validation.

### Text Command Probe - 2026-06-20

- `Application.executeTextCommand("TextCommands.List")` produced the available text-command list.
- Direct probes failed:
  - `Simulation.Solve`: no such command.
  - `Sim.Solve`: no such command.
  - `Solve`: no such command.
  - `Results`: no such command.
- Simulation-adjacent commands found were not sufficient for a full FEA loop:
  - `Commands.SetSimThermalFluxValue`: transcript helper for thermal flux inputs, not static stress solve/results.
  - `Commands.SimSetUnitsOverride`: transcript helper for Simulation units, not solve/results.
  - `Diagnostics.DownloadNastranSolverDialog`: dialog helper, not solve/results.
  - `SimPushProjectTools.PushProject`: cloud/project push helper, not local stress/FOS/deflection extraction.
  - `Options.SendOpenActionEvent`: testing hook for opening study types, not a documented solve/result API.
- Decision: do not build the project around undocumented text-command FEA automation. Use the proven CAD/mass bridge plus the analytical optimizer, then manually validate the baseline and top 3-5 optimizer candidates in Fusion FEA.

## Decision Memo

Date: 2026-06-20

Outcome: Week 3 external parameter-control bridge is proven. Week 4 FEA automation did not expose a reliable public Python API or stable text-command path for Static Stress solve/result extraction.

Evidence: `NEMOBridge.log` recorded request detection, Design workspace activation, parameter processing, mass extraction, and response writing for iteration 4. `TextCommandProbe.log` showed no usable commands for automated Static Stress solve, max stress, FOS, or deflection extraction.

Next action: continue with analytical optimization plus manual Fusion validation of the baseline and top 3-5 final candidates.

## Analytical Fallback Execution - 2026-06-20

- Generated `formal_sample_30` with 30 Latin-hypercube analytical evaluations.
- Ran `formal_optimize_baseline` from the configured baseline for 80 Nelder-Mead iterations.
- Ran `formal_optimize_best_sample` from the lightest feasible sample design for 80 Nelder-Mead iterations.
- Best aggressive analytical candidate:
  - source: `demos/bracket-proof-of-concept/validation/legacy-aggressive/validation_candidates.csv`
  - candidate: `candidate_01`
  - mass: `0.11259275115646929 kg`
  - analytical FOS: `2.596506012478061`
  - analytical deflection: `0.36109273930423197 mm`
- Conservative backup package generated:
  - source: `demos/bracket-proof-of-concept/validation/legacy-conservative/validation_candidates.csv`
  - lightest conservative candidate mass: `0.115923742767709 kg`
  - analytical FOS: `3.016074697852638`
  - analytical deflection: `0.27140845369979255 mm`
