# **Nelder-Mead  Marine Optimizer (NEMO)**

## **Automated, FEA-Driven Design Optimization Pipeline for a Marine Structural Component**

*Project Brief, PRD & 13-Week Project Plan*

## **1\. Project Brief**

### **1.1 Summary**

This project builds a software pipeline that couples Autodesk Fusion 360 (parametric CAD \+ FEA) with an external Python optimization routine, to automatically search for a minimum-mass design of a marine structural component that still satisfies a structural safety requirement. Instead of an engineer manually trying a handful of hand-picked design variants, the pipeline evaluates dozens to hundreds of variants automatically - changing geometry, re-running FEA, and reading back results - converging on a design a manual process would be very unlikely to find in the same amount of time.

### **1.2 Problem Being Solved**

Manual, trial-and-error design iteration in marine structural engineering is slow, and the resulting designs are typically "good enough" rather than optimal. The usual workflow - sketch a design, run FEA, check if it passes, manually guess a better set of dimensions, re-run FEA, repeat - is done by hand a handful of times before time runs out, leaving real, quantifiable performance (mass, material cost, and for moving parts, efficiency) on the table. This matters in marine engineering specifically because unnecessary mass in brackets, fittings, and structural components costs more to build, adds to vessel weight, and in service-critical applications can affect performance and fuel consumption over a vessel's lifetime.

### **1.3 Proposed Solution**

A Python script proposes a set of geometric parameter values; a Fusion 360 Add-in receives them, regenerates the parametric CAD model, automatically re-solves a pre-validated FEA study, and reports back the resulting mass, stress, factor of safety, and deflection; the Python script logs the result and proposes the next set of values using a gradient-free optimization algorithm (Nelder-Mead), repeating until the design converges on minimum mass subject to the safety constraint.

### **1.4 Case-Study Component**

The pipeline is demonstrated on a marine equipment mounting bracket - e.g. a bracket securing a small pump or auxiliary unit to a ship's structure. This component is chosen deliberately over a more complex shape (such as a hydrofoil) because its geometry parametrizes cleanly into a small number of independent variables, its load case is simple and well-defined (static equipment weight plus a dynamic/vibration amplification factor), and it is a genuinely common, real marine engineering component - every vessel has dozens of these brackets, so mass savings here have real-world relevance.

## **2\. Product Requirements Document (PRD)**

### **2.1 Purpose**

This PRD defines exactly what the optimization pipeline must do, who it is for, and how success will be judged, so that every week of the project plan in Section 6 is traceable to a specific requirement and scope decisions are made deliberately.

### **2.2 Problem Statement**

See Section 1.2. In PRD form: manual design iteration limits the number of design variants an engineer can realistically evaluate, preventing convergence on a genuinely optimal (minimum-mass, constraint-satisfying) structural design within a normal project timeline.

### **2.3 Target Audience / Stakeholders**

* Primary: project supervisor and examination panel, who need to see both genuine engineering rigor (a validated FEA workflow) and a genuinely novel artifact (a working automation/optimization tool, not just a single optimized part).  
* Secondary: the student (you), who needs a project with a clear, defensible novelty claim and a realistic chance of full completion in 3 months.  
* Tertiary: future students, who could reuse this pipeline architecture on a different component entirely (the bracket is a case study, not the limit of the tool).

### **2.4 Scope**

In scope: a parametric bracket model and validated FEA study in Fusion 360; a Fusion Add-in exposing programmatic control of geometry regeneration and FEA solving; an external Python optimization routine (Nelder-Mead, with a stretch comparison against a genetic algorithm); a results dashboard; a quantified baseline-vs-optimized comparison.

Out of scope (explicitly deferred to "Future Work"): use of Autodesk's paid, cloud-based Design Automation API; optimizing more than one component type in the same project; physical fabrication of any design; full CFD-based load derivation (the load case uses a standard static-plus-dynamic-factor approximation); multi-objective optimization beyond mass-vs-safety (e.g. explicitly trading off manufacturing cost).

### **2.5 Functional Requirements**

| ID | Requirement | Notes |
| :---- | :---- | :---- |
| FR1 | The system shall parametrically define a marine equipment mounting bracket in Fusion 360 using named User Parameters covering at minimum 6 independent geometric variables. | See Section 4.2 for the full parameter list. |
| FR2 | The system shall include a pre-validated FEA study template (constraints, load case, mesh settings) that can be re-solved automatically against any geometry generated from FR1. | Built and hand-validated once in Week 2; never redefined per-iteration. |
| FR3 | An external Python optimizer shall be able to request a new set of parameter values, trigger Fusion to regenerate the geometry and re-solve the FEA study, and receive back mass, max stress, factor of safety, and max deflection for that design. | This request/response loop is the core technical deliverable - see Section 3\. |
| FR4 | The system shall log every evaluated design (parameters \+ results) to a persistent file (CSV/JSON), regardless of whether the run completes or is interrupted. | Protects against lost work if Fusion or the script crashes mid-run. |
| FR5 | The optimizer shall search for a minimum-mass design that satisfies a minimum factor-of-safety constraint and a maximum-deflection constraint. | Constraint handling via penalty function - see Section 5.2. |
| FR6 | The system shall implement at least one gradient-free optimization algorithm (Nelder-Mead) as the primary search strategy. | Chosen for sample-efficiency given expensive (slow) FEA evaluations. |
| FR7 | The system shall produce a results dashboard/plot showing mass convergence over iterations and a stress-vs-mass trade-off view across all evaluated designs. | Primary demo artifact - see Section 8\. |
| FR8 | The system shall report a quantified comparison between a manually-designed baseline bracket and the optimizer's final design (mass reduction at equal or better factor of safety). | This single number is the project's key results headline. |

### **2.6 Non-Functional Requirements**

| ID | Requirement | Notes |
| :---- | :---- | :---- |
| NFR1 | Each full design evaluation (geometry update \+ FEA solve \+ result extraction) shall complete in under \~2 minutes on a typical student laptop. | Keeps a full optimization run (50-150 iterations) achievable within a single working session. |
| NFR2 | The pipeline shall be resilient to a single failed iteration (e.g. a non-converging mesh or an invalid geometry) without halting the entire optimization run. | Wrap each FEA evaluation in error handling; log failures and continue. |
| NFR3 | All communication between the external Python optimizer and the Fusion Add-in shall use a documented, inspectable file format (JSON), not an opaque or undocumented protocol. | Supports debugging and is itself good evidence of sound systems-engineering practice for the report. |
| NFR4 | The project shall require no paid software, cloud services, or Autodesk Platform Services (APS) account - only the free in-app Fusion Scripts & Add-Ins API. | See prior discussion: avoids the paid Design Automation API entirely. |
| NFR5 | Every simplifying assumption (load case, dynamic amplification factor, constraint thresholds) shall be explicitly stated and justified in the final report. | Protects academic credibility of the results. |

### **2.7 Success Metrics / Acceptance Criteria**

* The pipeline completes at least one full automated optimization run (50+ iterations) without manual intervention, OR, if full automation proves infeasible (see Section 7), completes an equivalent run in semi-automated mode with the optimization logic itself fully automated.  
* The optimizer's final design achieves a quantified mass reduction versus a manually-designed baseline bracket, at an equal or higher factor of safety (target: >= 15% mass reduction, stated as a goal not a guarantee).  
* The optimizer's final design is independently cross-checked by manually rebuilding and re-solving it in Fusion, confirming the pipeline's reported results within a small tolerance.  
* Every iteration evaluated during the project is logged and traceable, supporting full reproducibility of the reported results.

### **2.8 Assumptions & Constraints**

* Only the free, in-app Fusion 360 Scripts & Add-Ins API is used; no Autodesk Platform Services account or paid cloud automation is required.  
* The equipment load (mass and dynamic amplification factor) is a stated engineering assumption, not data from a specific named vessel.  
* Total project duration is fixed at approximately 13 weeks (3 months), as laid out in Section 6\.  
* If the Week 4 proof-of-concept shows that triggering/reading FEA results programmatically is not reliably possible, the project shifts to the semi-automated fallback described in Section 7 without changing its core novelty claim (the optimization methodology, not full automation, is the contribution).

## **3\. System Architecture**

The central technical challenge is that Fusion 360's free Scripts & Add-Ins API runs inside Fusion's own embedded Python interpreter, which does not have access to external libraries like SciPy that the optimization algorithm needs. The architecture below solves this with a simple, robust file-based handshake between two separate Python processes, rather than attempting to run the optimizer inside Fusion itself.

### **3.1 Components**

* External Python process (your normal Python installation, with NumPy/SciPy/Pandas): runs the optimization algorithm, decides the next parameter values to try, and reads/writes the handshake files.  
* Fusion 360 Add-in (running inside Fusion, using its embedded Python): watches for new requests, updates the CAD model's User Parameters, regenerates geometry, triggers the FEA study solve, and writes the results back out.  
* Handshake files (request.json / response.json): a simple, human-readable JSON contract between the two processes, written to a shared local folder both processes can access.

### **3.2 Request/Response Cycle**

1. External Python decides the next parameter values to test and writes them to request.json (e.g. { "iteration": 14, "baseplate\_length": 162.3, "rib\_height": 38.1, ... }).  
2. The Fusion Add-in (running a polling loop, e.g. checking every 1-2 seconds) detects the new request, reads the parameter values, and updates the corresponding Fusion User Parameters.  
3. The Add-in regenerates the model, runs the pre-validated FEA study (FR2), and extracts mass, max stress, factor of safety, and max deflection from the results.  
4. The Add-in writes these results to response.json, tagged with the same iteration number for traceability.  
5. External Python polls for response.json, reads the results, appends them to the persistent log (FR4), and - if running automatically - computes the next parameter values via the optimizer (Section 5\) and repeats from step 1\.

### **3.3 Why a File-Based Handshake (Not Sockets)**

A direct network/socket connection between the two processes is possible but adds real-time threading complexity inside Fusion's add-in event loop, which is a common source of instability for less experienced developers. A file-based handshake is slightly slower (polling introduces a small delay per iteration) but is far more robust, easier to debug (you can literally open the JSON files and read them), and easier to explain and defend in a viva - a deliberate, justified engineering trade-off worth stating explicitly in your report.

## **4\. Case-Study Component & Parametrization**

### **4.1 Load Case**

The bracket is assumed to support a small marine auxiliary unit (e.g. a pump) of approximately 50 kg. Shipboard equipment is commonly designed against a dynamic amplification factor to account for vibration and sea-induced motion rather than static weight alone; this project assumes a factor of 3 as a stated, referenced engineering assumption (NFR5), giving a design load of approximately 50 kg x 9.81 m/s^2 x 3 approx. 1.47 kN, applied vertically at the equipment mounting boss, with the baseplate's bolt-hole faces fixed (representing a rigid deck bolt-down).

### **4.2 Parametric Design Variables**

Six geometric parameters are varied by the optimizer; bolt hole diameter is held fixed since it is normally dictated by a standard bolt size rather than a free design choice:

| Parameter | Description | Baseline Value | Search Range |
| :---- | :---- | :---- | :---- |
| baseplate\_length | Length of the bracket's mounting baseplate | 150 mm | 100 \- 200 mm |
| baseplate\_width | Width of the mounting baseplate | 100 mm | 80 \- 150 mm |
| baseplate\_thickness | Thickness of the baseplate | 8 mm | 4 \- 15 mm |
| rib\_height | Height of the reinforcing rib/gusset | 40 mm | 20 \- 60 mm |
| rib\_thickness | Thickness of the reinforcing rib | 6 mm | 3 \- 10 mm |
| fillet\_radius | Fillet radius at the rib-to-baseplate junction | 5 mm | 2 \- 10 mm |
| bolt\_hole\_diameter | Diameter of the 4 mounting bolt holes | 10 mm | Fixed (standard bolt size, not optimized) |

### **4.3 Constraints**

* Minimum factor of safety: 2.5 (a reasonable structural margin for a marine fitting at this project's scope).  
* Maximum deflection at the equipment mounting point: 0.5 mm (a stated assumption representing equipment alignment tolerance).

## **5\. Optimization Methodology**

### **5.1 Objective**

Minimize total bracket mass, subject to the factor-of-safety and deflection constraints in Section 4.3. This is a classic constrained design-optimization problem, applied here to a structural marine component.

### **5.2 Constraint Handling**

Nelder-Mead (the chosen primary algorithm) does not natively support constraints, so constraints are incorporated using a penalty function: the value the optimizer actually minimizes is bracket mass plus a heavily-weighted penalty term that grows whenever factor of safety falls below the 2.5 target or deflection exceeds 0.5 mm. This pushes the optimizer away from infeasible designs without needing a more complex constrained-optimization algorithm - an accepted, well-documented simplification.

### **5.3 Primary Algorithm: Nelder-Mead**

Nelder-Mead (scipy.optimize.minimize, method='Nelder-Mead') is chosen as the primary optimizer because it is gradient-free (no derivative of the FEA "black box" is needed or available), well documented, simple to implement and explain in a viva, and - critically - relatively sample-efficient, which matters because each function evaluation here is an expensive Fusion+FEA solve, not a cheap calculation.

### **5.4 Baseline Search (Week 6\)**

Before optimizing, a coarse random/Latin-hypercube sample (\~20-30 designs) across the full parameter ranges is run to sanity-check that the pipeline behaves sensibly (heavier designs generally show higher factor of safety, etc.) and to give the final report a clear "before optimization" picture of the design space.

### **5.5 Stretch Comparison: Genetic Algorithm (Week 9\)**

If time and pipeline reliability allow, a simple genetic algorithm (e.g. via the DEAP library) is implemented as a second optimizer, allowing a direct comparison against Nelder-Mead on sample-efficiency (designs evaluated to reach a comparable result) and final converged mass. This upgrades the project from "I optimized a bracket" to "I compared optimization strategies for this class of problem," which is a stronger, more defensible novelty claim - but it is explicitly a stretch goal, not a committed deliverable, given the Week 4 technical risk.

## **6\. Detailed 13-Week Timeline**

Week 4 is the single most important checkpoint in this plan: it proves (or disproves) that Fusion's free API can trigger and read back FEA results programmatically. Everything from Week 5 onward depends on that result, which is why it is scheduled early, with Week 5 immediately available as recovery time.

| Week | Fusion 360 / CAD-FEA Track | Python / Pipeline-Optimization Track | Deliverable / Milestone |
| :---- | :---- | :---- | :---- |
| **1** | Select the case-study component (marine equipment mounting bracket). Sketch initial baseline geometry by hand to understand the design space before parametrizing. | Research the Fusion 360 Scripts & Add-Ins Python API (in-app, free tier). Work through 2-3 official sample scripts to confirm geometry can be read/modified via script on your machine. | **Component chosen and justified. API environment confirmed working with a trivial test script.** |
| **2** | Build the full parametric CAD model using User Parameters (Section 4.2). Set up the FEA study template once: material, load case (equipment weight x dynamic amplification factor), fixed constraints at bolt holes, mesh settings. Validate manually against a hand (beam-bending) calculation. | Draft the JSON request/response schema that will pass parameter values and results between Python and Fusion (e.g. request.json with parameter values; response.json with mass, stress, FOS, deflection). | **Parametric model \+ validated FEA template complete. Communication schema documented.** |
| **3** | Write a Fusion Add-in script that: (a) watches for a new request.json file, (b) updates the User Parameters accordingly, (c) regenerates the model. Test by manually editing request.json and confirming geometry updates. | Write a minimal external Python script that writes a single request.json file with new parameter values. | **Geometry can be changed from outside Fusion via a file, without opening the parameter dialog manually.** |
| **4** | CRITICAL PROOF-OF-CONCEPT (go/no-go week): extend the Add-in to programmatically trigger the FEA study solve and extract mass, max stress, FOS, and max deflection, writing them to response.json. | Write the external Python polling loop: wait for response.json, read it, print the results. Run several manual end-to-end test cycles. | **Full single-iteration loop proven: Python requests a design \-\> Fusion builds and solves it \-\> Python receives real results. If this fails, fall back to the semi-automated mode described in Section 7\.** |
| **5** | No new CAD work - used to harden the Add-in script (error handling for failed solves, invalid geometry, mesh failures) discovered during Week 4 testing. | Build the iteration logger: every request/response pair is appended to a persistent results.csv, regardless of success or failure, so no run data is ever lost. | **Pipeline survives at least 10 consecutive automated iterations without manual intervention.** |
| **6** | No new CAD work. | Implement a baseline random/Latin-hypercube search: generate \~20-30 random parameter sets within the ranges in Section 4.2, run them all through the pipeline, and plot the resulting mass-vs-stress spread. | **First real dataset of design evaluations. Confirms the design space behaves sensibly (heavier designs generally stronger, etc.) before optimization begins.** |
| **7** | No new CAD work. | Implement the primary optimizer: scipy.optimize.minimize with method='Nelder-Mead', using the penalty-function objective from Section 5.2. Run to convergence from at least 2 different starting points. | **First converged optimization run with a clear minimum-mass, constraint-satisfying result.** |
| **8** | Mid-project checkpoint: manually rebuild and re-solve the optimizer's final design in Fusion to independently confirm the automated result (cross-check against the pipeline's own report). | Write up interim methodology and results. Investigate any discrepancy between the manual cross-check and pipeline output. | **Mid-project report draft. Optimizer result independently verified.** |
| **9** | No new CAD work (stretch week). | STRETCH GOAL: implement a second optimizer (simple genetic algorithm, e.g. via the DEAP library) for comparison against Nelder-Mead on sample-efficiency and final mass. If the pipeline needs more reliability work instead, use this week as buffer. | **Either: a second optimizer comparison dataset, OR a more robust, battle-tested pipeline - both are acceptable depending on how Weeks 4-8 went.** |
| **10** | Export final CAD render, exploded view, and engineering drawing of both the baseline and optimized bracket designs for the report/slides. | Build the results dashboard (Streamlit recommended): convergence plot (mass vs iteration), stress-vs-mass scatter of all evaluated designs, and a baseline-vs-optimized comparison panel. | **Interactive results dashboard complete.** |
| **11** | No new CAD work - buffer for drawing clean-up or supervisor feedback. | Stress-test the full pipeline end-to-end at least 3 more times for the recorded demo; clean and comment the codebase. | **Codebase finalized. Demo run(s) recorded as a fallback in case live execution is unreliable on defense day.** |
| **12** | Compile all Fusion 360 deliverables (CAD files, FEA reports, drawings) into the final submission package. | Finalize dashboard polish; rehearse the live (or recorded-fallback) demo end-to-end at least twice. | **Final report written. Slide deck ready. Demo rehearsed.** |
| **13 (buffer)** | Contingency - absorb slippage from the Week 4 proof-of-concept or any later FEA rework. | Contingency - absorb slippage in optimizer tuning, dashboard bugs, or demo reliability. | **Project submission-ready with margin before the deadline.** |

## **7\. Fallback Plan: Semi-Automated Mode**

If Week 4 shows that programmatically triggering and reading an FEA solve is not reliably possible within the free in-app API, the project does not need to be abandoned or fundamentally redesigned - it shifts to a semi-automated mode that preserves the entire novelty claim:

* The Python optimizer still runs the full Nelder-Mead (or random-search) logic and still decides every parameter value to test - this is the actual intellectual contribution and is unaffected.  
* Instead of the Add-in updating Fusion automatically, the script prints the next parameter values for you to manually enter into Fusion's parameter dialog and click Solve.  
* You then manually type the 3-4 result numbers (mass, stress, FOS, deflection) back into the script, which logs them and computes the next iteration.

This is slower (you are the bottleneck instead of the computer), so the total number of iterations you can realistically run drops - plan for 15-25 manual iterations rather than 80-150 automated ones - but the methodology, the optimizer, the results dashboard, and the baseline-vs-optimized comparison all remain fully intact and defensible. State this fallback explicitly and proactively in your report if you end up using it; framed correctly ("automated where the API allowed, human-in-the-loop where it didn't, with the optimization logic identical either way") it reads as good engineering judgement, not as a shortfall.

## **8\. Demo Plan**

### **8.1 Layer 1 (Guaranteed): Results Replay**

Regardless of how Weeks 4-9 go, you will have a complete log of every evaluated design. Animate this as a live-feeling plot during your defense: mass on the y-axis, iteration number on the x-axis, with a horizontal line at the factor-of-safety constraint, ending on the clearly marked optimum. This is achievable no matter which path the project takes.

### **8.2 Layer 2 (If Pipeline Is Reliable): Live or Near-Live Run**

If the Week 4 proof-of-concept succeeds and the pipeline is stable, run a short live optimization (10-20 iterations is enough for a demo, even if your full report uses a longer logged run) with Fusion visibly regenerating geometry on one screen and your Python dashboard updating in real time on the other.

### **8.3 Layer 3 (Always Include): Before/After Comparison**

Close the demo by placing your manually-designed baseline bracket next to the optimizer's final result, both meeting the same factor-of-safety requirement, and state the quantified mass reduction (e.g. "the optimizer found a design 19% lighter than my hand-designed baseline, at the same factor of safety"). This single number is the strongest, most concrete claim you can make in the room, and should anchor both your report abstract and your closing demo statement.

## **9\. Final Deliverables Checklist**

* Fusion 360 parametric bracket model (baseline \+ final optimized geometry), with all User Parameters documented.  
* Validated FEA study template, including the hand-calculation cross-check (Section 1 of the earlier Fusion workflow notes applies directly here).  
* Fusion Add-in source code (or documented semi-automated procedure, if the fallback in Section 7 was used).  
* External Python codebase: optimizer, logging, results dashboard.  
* Full iteration log (CSV/JSON) of every design evaluated during the project.  
* Results dashboard showing convergence and the baseline-vs-optimized comparison.  
* Final written report (including all stated assumptions per NFR5) and defense slide deck.  
* Recorded video of at least one full successful optimization run, as a live-demo fallback.

## **10\. Suggested Tools & Resources**

* CAD/FEA/Automation: Autodesk Fusion 360 (Design \+ Simulation workspace \+ Scripts & Add-Ins API, free tier).  
* External optimization: Python 3, SciPy (optimize.minimize), NumPy, Pandas.  
* Stretch comparison algorithm: DEAP (genetic algorithm library) - optional, Week 9 only.  
* Dashboard: Streamlit (fastest to build) or Plotly Dash.  
* Data interchange: JSON for the request/response handshake (Section 3).  
* Reference material: Autodesk's official Fusion 360 API sample repositories (accessible via Help -> Learning and Documentation inside Fusion) for Scripts & Add-Ins examples.  
* Documentation/version control: Git repository recommended for all code; keep a dated log of every Week 4 proof-of-concept attempt regardless of outcome, since this is valuable evidence for the report either way.
