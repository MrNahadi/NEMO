I’ll assume:

- You are at the Windows desktop.
- NEMO already exists at `C:\Users\muigu\Documents\Projects\NEMO`.
- Python and Autodesk Fusion are installed.
- No terminal and no Fusion window are open.
- We are demonstrating the `bracket`.

You can replace `bracket` with `padeye` or `stabilizer`.

# Part 1: Prepare NEMO without PowerShell

## 1. Open the project

1. Open **File Explorer**.
2. Browse to:

```text
C:\Users\muigu\Documents\Projects\NEMO
```

3. Confirm that you can see:

```text
build.bat
README.md
src
fusion_addin
tests
```

Do not move this project folder after connecting NEMOBridge to Fusion.

## 2. Set up the Python environment

1. Double-click `build.bat`.
2. A black NEMO Project Launcher window will open.
3. Press `1` for:

```text
Set up or repair the Python environment
```

4. Wait for it to create `.venv` and install the dependencies.
5. When it says the operation completed, press a key to close the window.

This setup is normally needed only once.

## 3. Run the offline checks

1. Double-click `build.bat` again.
2. Press `2` for:

```text
Run offline checks and tests
```

3. Wait for the tests to finish.
4. The expected result is:

```text
27 passed, 3 skipped
```

The three skipped tests require Fusion, so skipping them is normal at this stage.

# Part 2: Start and configure Autodesk Fusion

## 4. Open Fusion

1. Open the Windows Start menu.
2. Search for **Autodesk Fusion**.
3. Start Fusion and sign in if requested.
4. Wait until Fusion has loaded completely.

## 5. Install or link NEMOBridge

This is required the first time only.

1. In Fusion, open the **Utilities** tab.
2. Select **Scripts and Add-Ins**.
3. Open the **Add-Ins** tab.
4. Click the green **+** button or **Script or add-in from device**.
5. Browse to:

```text
C:\Users\muigu\Documents\Projects\NEMO\fusion_addin\NEMOBridge
```

6. Select the complete `NEMOBridge` folder.
7. Confirm the selection.
8. Select **NEMOBridge** from the add-in list.
9. Click **Run**.

Fusion should report that NEMOBridge is watching for requests.

## 6. Create the correct design type

1. In Fusion, select **File → New**.
2. Choose **Hybrid Design**.
3. Wait for the blank design to open.

Do not use a Part Design. NEMOBridge needs to create its own generated component.

Leave Fusion open.

# Part 3: Run one individual-part pipeline

## 7. Open Command Prompt in the NEMO folder

You do not need PowerShell.

1. Return to File Explorer.
2. Open the NEMO project folder.
3. Click the File Explorer address bar.
4. Type:

```text
cmd
```

5. Press Enter.

A Command Prompt will open directly in the NEMO folder.

You should see a prompt similar to:

```text
C:\Users\muigu\Documents\Projects\NEMO>
```

## 8. Start the complete bracket pipeline

Enter:

```bat
build.bat fusion bracket
```

For a different part, use:

```bat
build.bat fusion padeye
```

or:

```bat
build.bat fusion stabilizer
```

Do not use menu option 5 for the bracket because that menu option runs the padeye and stabilizer together. The explicit command above runs only the selected part.

## 9. What happens automatically

For the bracket, NEMO will:

1. Run the offline tests.
2. Evaluate the baseline bracket.
3. Generate 60 Latin-hypercube samples.
4. Run Nelder–Mead from the baseline.
5. Select two additional starting designs.
6. Run two more Nelder–Mead optimizations.
7. Combine the results.
8. Select the baseline plus five finalists.
9. Create a validation package.
10. Send each candidate to NEMOBridge.
11. Rebuild the bracket in Fusion.
12. Export STEP geometry.
13. Export boundary-face metadata.
14. Save each Fusion response.

Keep both Fusion and Command Prompt open. Do not submit another CAD request while this process is running.

# Part 4: Locate the validation package

After the pipeline finishes, open the `reports` folder in File Explorer.

Find the newest folder resembling:

```text
<timestamp>_bracket_validation
```

It contains:

```text
VALIDATION_CHECKLIST.md
validation_candidates.csv
validation_candidates.json
fusion_requests
fusion_responses
```

The `fusion_requests` folder should contain:

```text
baseline_request.json
candidate_01_request.json
candidate_02_request.json
candidate_03_request.json
candidate_04_request.json
candidate_05_request.json
```

# Part 5: Perform FEA for the baseline

The pipeline sends all candidates through Fusion, but only the final generated candidate will remain visible. Therefore, regenerate each candidate individually before its FEA study.

## 10. Generate the baseline again

In Command Prompt, enter the following as one line, replacing the folder name with your actual timestamped validation folder:

```bat
.venv\Scripts\nemo.exe cad --part bracket --params-json "reports\<timestamp>_bracket_validation\fusion_requests\baseline_request.json" --artifact step --artifact boundary_tags
```

Example:

```bat
.venv\Scripts\nemo.exe cad --part bracket --params-json "reports\20260728_210000_bracket_validation\fusion_requests\baseline_request.json" --artifact step --artifact boundary_tags
```

Wait until:

- Fusion finishes generating the bracket.
- The terminal prints a response.
- The response status is `partial`.
- A positive mass and volume are reported.

`partial` is correct because Fusion CAD completed, but FEA has not yet been performed.

# Part 6: Create the bracket Static Stress study

## 11. Inspect the CAD model

Before creating the study, check that the bracket has:

- One connected solid
- A baseplate
- Four mounting holes
- Two triangular ribs
- Rib-root fillets
- No failed timeline features

If the geometry looks incorrect, do not proceed to FEA.

## 12. Enter the Simulation workspace

1. In Fusion, change from **Design** to **Simulation**.
2. Select **New Study**.
3. Choose **Static Stress**.
4. Confirm the study.

Create a fresh study for each candidate where practical. Rebuilding the CAD may invalidate faces referenced by an earlier study.

## 13. Assign the bracket material

Assign **Aluminum 6061-T6**.

Confirm or create a material with:

| Property | Value |
|---|---:|
| Density | 2,700 kg/m³ |
| Yield strength | 276 MPa |
| Elastic modulus | 68.9 GPa |
| Poisson ratio | 0.33 |

Do not rely only on the material name. Check that the numerical properties match.

## 14. Apply the fixed support

Apply a fixed constraint to the cylindrical surfaces of all four mounting holes.

These faces correspond to:

```text
fixed_support
```

Confirm that all four hole surfaces are selected—not only one.

This represents the bracket being securely attached through its mounting bolts. It is still a simplified support assumption and should be documented.

## 15. Apply the equipment load

Apply a total downward force of:

```text
1,471.5 N
```

Apply it to the upper rib faces identified by:

```text
equipment_load
```

Important:

- The combined load across all selected faces must equal 1,471.5 N.
- Do not accidentally apply 1,471.5 N separately to every face.
- Confirm that the arrow points downward in the intended equipment-weight direction.

## 16. Check contacts

The bracket should normally be one joined solid, so separate contact definitions may not be required.

Verify that:

- Both ribs are joined to the baseplate.
- No component is disconnected.
- Fusion does not report unconstrained or freely moving bodies.

# Part 7: Mesh and solve

## 17. Generate the first mesh

1. Start with a medium global mesh.
2. Add local refinement around:

   - Mounting holes
   - Rib-to-baseplate junctions
   - Root fillets
   - Upper load faces

3. Generate the mesh.
4. Inspect it visually for excessively large or distorted elements.

## 18. Solve

Click **Solve** and use the available Fusion solver.

Wait for the study to complete. Do not accept a result containing rigid-body-motion, unconstrained-body, material, or contact errors.

## 19. Inspect the results

Record:

- Fusion mass
- Maximum von Mises stress
- Minimum factor of safety
- Maximum displacement
- Location of maximum stress
- Location of maximum displacement
- Mesh size
- Element count
- Applied load
- Total support reaction

Check that:

```text
Minimum FOS ≥ 2.5
Maximum displacement ≤ 0.5 mm
```

The support reaction should approximately balance the applied 1,471.5 N load.

# Part 8: Perform a mesh-convergence check

Do not rely on one mesh.

1. Record the first solution.
2. Refine the mesh around the high-stress regions.
3. Solve again.
4. Compare stress, factor of safety, and displacement.
5. Refine again if the meaningful results are still changing substantially.

Be cautious if the maximum stress occurs at:

- A perfectly fixed edge
- A sharp corner
- A point-like load
- A contact edge

Such a peak may be a numerical singularity. Examine nearby structural stress and how it changes under mesh refinement.

# Part 9: Repeat for each finalist

For `candidate_01`, return to the Design workspace and run:

```bat
.venv\Scripts\nemo.exe cad --part bracket --params-json "reports\<timestamp>_bracket_validation\fusion_requests\candidate_01_request.json" --artifact step --artifact boundary_tags
```

Then repeat:

1. Inspect the rebuilt geometry.
2. Create or update the Static Stress study.
3. Reassign or verify the material.
4. Reapply all four supports.
5. Reapply the total 1,471.5 N load.
6. Verify contacts.
7. Mesh.
8. Solve.
9. Perform refinement checks.
10. Record the results.

Repeat for at least:

```text
baseline
candidate_01
candidate_02
candidate_03
```

Validate additional candidates if the first three fail.

# Part 10: Record and compare the results

Open this file in Notepad or another editor:

```text
reports\<timestamp>_bracket_validation\VALIDATION_CHECKLIST.md
```

For every candidate, enter:

- Fusion mass
- Maximum stress
- Minimum FOS
- Maximum displacement
- Pass or fail
- Mesh information
- Notes about stress locations or modeling concerns

Then compare analytical and Fusion results.

The final selected bracket should:

- Pass FOS ≥ 2.5
- Pass displacement ≤ 0.5 mm
- Be lighter than the baseline
- Have a credible converged FEA result
- Have reaction forces consistent with the applied load

Select the lowest-mass candidate that passes all checks.

The correct conclusion is:

> “This is the best bracket design found within the parameterized search and validated under the documented Static Stress load case.”

It is not automatically certified for manufacture or service.