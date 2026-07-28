# Bracket Proof of Concept

This folder preserves NEMO's original bracket demonstration. It is the first
case study used to prove that Python could propose bracket dimensions,
communicate with Autodesk Fusion through NEMOBridge, rebuild native CAD from
parameters, and compare progressively lighter candidates.

The bracket remains a supported NEMO part. It is not a discarded prototype.
The shared implementation lives in the normal application folders so that the
demo exercises the same maintained code as the rest of the project.

## What the demonstration contains

| Item | Location | Purpose |
| :-- | :-- | :-- |
| Original project brief | `PROJECT_BRIEF.md` | Records the initial project intent and 13-week plan. |
| Manual bridge probe | `manual_fusion_handshake.py` | Changes one bracket dimension, submits a Fusion CAD request, and waits for the matching response. |
| Current finalist package | `validation/schema-v2-finalists/` | Six bracket candidates using the current schema-v2 CAD request contract. |
| Legacy aggressive package | `validation/legacy-aggressive/` | Original schema-v1 bracket candidates selected at the normal analytical limits. |
| Legacy conservative package | `validation/legacy-conservative/` | Original schema-v1 backup candidates selected with larger analytical margins. |
| Bracket definition | `../../src/nemo/parts/definitions/bracket.json` | Authoritative parameters, bounds, material, load, and constraints. |
| Analytical model and optimizer | `../../src/nemo/parts/analytical.py` and `../../src/nemo/optimizers.py` | Screening calculations and bounded Nelder-Mead search. |
| Fusion generator and bridge | `../../fusion_addin/NEMOBridge/` | Creates the bracket as native Fusion geometry and exchanges request/response files. |

## What the proof of concept demonstrates

The maintained demonstration can:

1. generate bounded bracket candidates;
2. estimate mass, stress, factor of safety, and deflection analytically;
3. run a multi-start Nelder-Mead search for the best design found in the
   parameterized search;
4. write every evaluated candidate to CSV and JSON;
5. select finalists;
6. send those finalists through NEMOBridge;
7. generate a new native bracket component in Fusion; and
8. export STEP geometry and semantic boundary-face metadata.

The original project brief proposed solving Fusion FEA automatically during
every optimization iteration. That automation was not completed. The current
optimizer uses the analytical screening model, then NEMOBridge generates the
finalist CAD models for manual Fusion Static Stress validation. Do not present
the analytical optimum as a certified or globally optimal design.

## Prerequisites

Run commands from the repository root.

```powershell
.\build.bat setup
.\build.bat check
```

For CAD generation, Autodesk Fusion must be open with the
`fusion_addin\NEMOBridge` add-in installed and running. Create or activate a
blank Hybrid Design before submitting a request. See the root
[`README.md`](../../README.md#autodesk-fusion-setup) for the full setup.

## Demo 1: one visible CAD update

This is the shortest live demonstration of the original handshake. It starts
from the bracket baseline, changes `baseplate_length` from 150 mm to 160 mm,
writes a schema-v2 request, and waits for NEMOBridge.

```powershell
.\.venv\Scripts\python.exe demos\bracket-proof-of-concept\manual_fusion_handshake.py
```

Watch Fusion create the generated bracket. The terminal then prints the matching
response, including CAD mass and artifact paths. Structural metrics are absent
because this request performs CAD generation, not automated FEA.

## Demo 2: complete bracket workflow

With NEMOBridge running:

```powershell
.\build.bat fusion bracket
```

The launcher runs offline checks, evaluates the baseline, samples the bracket
design space, performs three analytical Nelder-Mead starts, selects finalists,
and sends the validation candidates to Fusion for CAD export.

For a shorter live demonstration:

```powershell
$env:NEMO_SAMPLE_COUNT = "10"
$env:NEMO_MAX_ITER = "20"
.\build.bat fusion bracket
Remove-Item Env:NEMO_SAMPLE_COUNT
Remove-Item Env:NEMO_MAX_ITER
```

The shortened run proves the software workflow but is not suitable for a final
engineering or optimization claim.

## Preserved local results

Historical bracket results remain in the generated-data area:

```text
data/runs/*bracket*/
data/runs/active/artifacts/*bracket*/
```

At the time this demo folder was organized, the workspace contained ten bracket
run folders, 55 bracket STEP exports, and 56 bracket boundary-tag JSON files.
These generated files are intentionally ignored by Git and remain local to this
computer. The curated request packages under this demo folder are tracked.

Do not delete the bracket run folders or bracket artifacts before a planned
demo unless a separate backup has been made.
