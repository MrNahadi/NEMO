# NEMO - Nelder-Mead Marine Optimizer

NEMO is a student project scaffold for optimizing a parametric marine equipment mounting bracket. It combines:

- an external Python optimization pipeline,
- an analytical structural fallback model,
- a file-based JSON handshake for Fusion 360,
- a Fusion add-in bridge scaffold,
- CSV logging and a Streamlit results dashboard.

The code in this repository can run without Fusion using the analytical model. Fusion integration is isolated in `fusion_addin/NEMOBridge` and is intended for the Week 3/4 API spike.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

If you do not install the package, run commands with:

```powershell
$env:PYTHONPATH="src"
python -m nemo.cli evaluate
```

## Common Commands

Evaluate the baseline bracket analytically:

```powershell
nemo evaluate
```

Run a 30-design random sample:

```powershell
nemo sample --count 30
```

Run Nelder-Mead optimization from the baseline:

```powershell
nemo optimize --max-iter 80
```

Open the dashboard:

```powershell
streamlit run dashboard/app.py
```

## Fusion Add-In Bridge

The Fusion add-in scaffold lives in `fusion_addin/NEMOBridge`.

It currently supports:

- polling for `request.json`,
- updating exact named Fusion user parameters,
- calling `Design.computeAll()`,
- reading design mass from physical properties,
- writing a `response.json`.

FEA solve/result extraction is deliberately left as the Week 4 spike because Fusion Simulation automation is the major technical risk.

## Project Constants

- Material: Aluminum 6061-T6
- Density: 2700 kg/m^3
- Yield strength: 276 MPa
- Elastic modulus: 68.9 GPa
- Design load: 50 kg x 9.81 m/s^2 x 3 = 1471.5 N
- Minimum FOS: 2.5
- Maximum deflection: 0.5 mm

## Repository Layout

```text
fusion_addin/       Fusion 360 bridge scaffold
src/nemo/           Python package for optimization and logging
data/runs/          Generated run folders and CSV logs
dashboard/          Streamlit results dashboard
docs/               Assumptions, validation plan, API spike notes
reports/            Report figures and screenshots
tests/              Local tests for non-Fusion code
```
