# AGENTS.md

This file applies to the entire repository. It is a working guide for coding
agents; `README.md` remains the user-facing setup and operating manual.

## Project intent and safety boundary

NEMO is a Python 3.10+ academic optimization tool for three marine structures:
`bracket`, `padeye`, and `stabilizer`. It combines first-order analytical
screening, bounded Nelder-Mead optimization, a file-based Autodesk Fusion 360
CAD bridge, validation-package generation, and a Streamlit results dashboard.

Treat all analytical results as screening estimates, not certified engineering
results. Do not describe a design as safe for manufacture or service based only
on this code. Preserve the documented requirement for appropriate design-code
checks, calibrated FEA, material and load verification, and qualified engineering
review. The defensible optimization claim is "best design found within this
parameterized search," not a global optimum.

## Repository map

- `src/nemo/`: installable Python package and CLI.
- `src/nemo/parts/definitions/*.json`: authoritative part parameters, units,
  bounds, baselines, materials, loads, constraints, and boundary roles.
- `src/nemo/parts/analytical.py`: first-order structural screening models.
- `fusion_addin/NEMOBridge/`: Fusion add-in, native CAD generators, and bridge
  configuration. This code runs inside Fusion's Python environment.
- `demos/bracket-proof-of-concept/`: preserved original bracket demonstration,
  including its historical brief, manual bridge probe, and curated validation
  requests. Its shared runtime remains under `src/nemo/` and `fusion_addin/`.
- `dashboard/app.py`: Streamlit viewer for generated `results.csv` and `run.json`.
- `tests/`: offline tests plus an explicitly enabled Fusion integration sweep.
- `data/runs/`: generated run data and the live Fusion handshake directory.
- `reports/`: report sources, validation packages, and generated deliverables.
- `docs/`: engineering assumptions, implementation status, and validation/FEA
  contracts.
- `build.bat`: Windows setup, checks, analytical pipelines, Fusion export, and
  dashboard launcher.

## Setup and routine commands

Use the repository virtual environment and run commands from the repository
root. On Windows PowerShell:

```powershell
.\build.bat setup
.\build.bat check
```

Equivalent direct commands:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m nemo.cli parts
.\.venv\Scripts\python.exe -m nemo.cli evaluate --part bracket
```

Run a focused test while iterating, then the full offline suite before handing
off a code change:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_parts.py
.\.venv\Scripts\python.exe -m pytest -q
```

The Fusion sweep is slow, mutates `data/runs/active`, and requires Autodesk
Fusion with NEMOBridge already running. Never enable it as an ordinary offline
check:

```powershell
$env:NEMO_FUSION_SMOKE = "1"
.\.venv\Scripts\python.exe -m pytest -q -m fusion
Remove-Item Env:NEMO_FUSION_SMOKE
```

If Fusion is unavailable, run the offline suite and explicitly state that the
Fusion-dependent check was not run. Fusion CAD tests do not perform FEA.

## Core implementation rules

- Keep behavior part-aware. Pass `part_id` through evaluation, logging,
  optimization, validation, and bridge requests; do not add new bracket-only
  assumptions to shared code.
- Treat each part-definition JSON file as the source of truth. Parameter names
  are exact contract keys. Respect each parameter's declared unit: most are
  millimetres, but percentage variables such as stabilizer spar positions are
  not lengths.
- Keep physical-unit conversion explicit. Analytical geometry converts
  millimetres to metres for SI calculations and reports stress in MPa,
  deflection in mm, volume in m^3, and mass in kg.
- Preserve schema-v1 request compatibility (`parameters_mm`, implicit bracket)
  unless a deliberate migration removes it. New payloads and responses use
  schema version 2 with `part_id`, `parameters`, and `artifact_formats`.
- Invalid inputs and unavailable evaluators must return controlled failed
  responses with objective `1e9`; do not let one bad candidate terminate an
  optimization run.
- `open_fea` is a reserved, deliberately unimplemented mode. Follow
  `docs/OPEN_FEA_CONTRACT.md` before implementing or changing it, and never
  fabricate solver results.
- Fusion CAD-only responses are intentionally partial: volume, mass, and
  artifacts may be present while stress, factor of safety, and deflection are
  absent. Do not present CAD mass as FEA validation.
- Write handshake JSON atomically and correlate responses by both `run_id` and
  `iteration`. `data/runs/active` is a single shared channel, so avoid concurrent
  CAD requests unless the protocol is redesigned for them.
- Preserve CSV column ordering and the one-part-per-log schema enforced by
  `nemo.logger`. The dashboard and validation package reader consume those
  fields.
- Optimizer coordinates are scaled to `[0, 1]`; keep conversion and clipping at
  the boundary rather than mixing scaled and physical values.

## Changing or adding a part

A part change usually spans more than one file. Check all relevant layers:

1. Update the manifest in `src/nemo/parts/definitions/`.
2. Update the hard-coded registry order in `src/nemo/parts/registry.py` when
   adding a new `part_id`.
3. Implement or update the analytical evaluator and its dispatch entry.
4. Implement or update Fusion generation, material assignment, and every
   semantic boundary selector required by the manifest.
5. Add tests for bounds, baseline feasibility, qualitative sensitivity (for
   example, thinner should normally be lighter and weaker), schema/log fields,
   and sampling/optimization behavior.
6. Update the README tables/workflow and the engineering or validation docs when
   loads, constraints, assumptions, units, or acceptance criteria change.
7. Run the baseline plus 20 seeded Latin-hypercube Fusion geometry sweep before
   claiming a CAD generator is robust.

The Fusion generator reads the same JSON definitions directly rather than
importing the `nemo` package. Keep the Python and Fusion sides of the request,
response, artifact, and boundary-tag contracts synchronized.

## Code and dependency conventions

- Match the existing Python style: four-space indentation, module docstrings,
  `from __future__ import annotations`, `pathlib.Path`, type hints, and small
  focused functions. Existing contract records use frozen dataclasses.
- Prefer explicit validation and useful error messages over silent coercion.
- Preserve deterministic seeds in tests and documented workflows.
- No formatter, linter, or static type checker is currently configured. Do not
  claim those checks ran unless configuration is added and the commands run.
- If runtime dependencies change, keep both `pyproject.toml` and
  `requirements.txt` synchronized. Avoid third-party imports in the Fusion
  add-in unless they are known to exist in Fusion's embedded environment.
- Use repository-relative configuration. Do not add developer-specific absolute
  paths, credentials, or machine settings.

## Generated files and reports

Do not treat these as source during normal code work:

- `data/runs/**`, including live `request.json`, `response.json`, logs, and CAD
  artifacts;
- `reports/figures/**` and `reports/screenshots/**`;
- Fusion exports such as STEP, STL, F3D, and F3Z files;
- LaTeX build intermediates such as `.aux`, `.log`, `.fls`, `.fdb_latexmk`,
  `.bbl`, `.blg`, `.lof`, `.lot`, `.out`, and `.toc`.

Only regenerate committed validation packages or report PDFs when the task calls
for updated evidence or deliverables. Edit report source in `main.tex`,
`structure/*.tex`, and `references.bib`, not compiler intermediates.

## Handoff checklist

Before declaring a change complete:

- Run the narrowest relevant tests and the full offline test suite.
- Confirm all registered baselines still evaluate successfully and feasibly when
  engineering inputs or analytical logic changed, or document an intentional
  exception.
- Exercise the affected CLI command when changing command behavior or output.
- State whether Fusion, dashboard, LaTeX, or manual FEA checks were actually run.
- Keep generated artifacts and unrelated working-tree changes out of the patch.
- Update user documentation when commands, schemas, inputs, outputs, assumptions,
  or limitations change.
