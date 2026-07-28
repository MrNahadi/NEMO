# Research Draft and Report Blueprint

## Working title

**Development and Evaluation of an Auditable, Resource-Conscious Parametric Optimization Workflow for Marine Structural Components**

## Purpose of this draft

This document is the research-stage source for the final LaTeX project report. It defines the central argument, research questions, literature synthesis, methodology, evidence boundaries, and report structure. The final report will expand this material into at least 55 pages of numbered chapters. This target provides a margin above the required 50 pages. Preliminary pages, references, and appendices do not count toward that target.

The report concerns the design and implementation of the Nelder-Mead Marine Optimizer (NEMO). NEMO supports three case-study parts:

1. an aluminum marine equipment bracket;
2. an S275 steel lifting padeye; and
3. an aluminum small-craft stabilizer fin.

The bracket is the completed proof-of-concept case. It shows the full intended sequence from a parameterized engineering definition to analytical optimization, native Fusion CAD, and a manually prepared Static Stress study. The padeye and stabilizer use the same software architecture. They have analytical screening models, native CAD generators, semantic boundary roles, CAD sweep evidence, and finalist validation packages. Their manual FEA campaigns remain future validation work.

## Central framing

NEMO is an auditable and resource-conscious engineering workflow. It uses inexpensive analytical calculations to explore many designs. It limits the more expensive CAD and FEA work to baselines and selected finalists. The workflow preserves the connection between each design, its inputs, its calculated outputs, its generated CAD, and its validation record.

This framing does not claim that NEMO invented structural optimization, Nelder-Mead search, Latin-hypercube sampling, CAD automation, or multi-fidelity analysis. Those methods have established literatures. Automated CAD-CAE optimization frameworks have also existed for many years. Park and Dang coupled commercial CAD and CAE software through programming interfaces and metamodels in 2010 ([Park and Dang, 2010](https://doi.org/10.1016/j.cad.2010.06.003)). More recent work has developed unified representations that maintain design and simulation intent inside closed optimization loops ([Li et al., 2023](https://doi.org/10.1016/j.cad.2023.103528)).

The contribution is instead an implementation-and-evaluation contribution. NEMO combines the following elements in one inspectable desktop workflow:

- unit-aware JSON definitions for several marine part types;
- first-order analytical models with stated assumptions;
- scaled and bounded design variables;
- seeded Latin-hypercube exploration;
- multi-start Nelder-Mead refinement;
- controlled penalties and failed-evaluation handling;
- versioned request and response records;
- atomic file exchange with Autodesk Fusion;
- native CAD generation;
- semantic names for load and support regions;
- generated validation packages;
- separate treatment of analytical, CAD, and FEA evidence; and
- a dashboard for reviewing recorded runs.

This combination is evaluated as a proof of concept. It is not a certified design process.

## Research gap

The reviewed literature contains mature work on derivative-free optimization, multi-fidelity modeling, automated CAD-CAE loops, offshore structural optimization, lifting-padeye assessment, and simulation verification. No individual NEMO method is new.

However, the reviewed sources do not directly address the practical implementation gap targeted by this project: a transparent, part-manifest-driven workflow that operates on an ordinary engineering workstation and connects low-cost screening, bounded multi-start search, native CAD generation, semantic boundary metadata, and human-reviewed FEA preparation across several marine component archetypes.

NEMO addresses this limited gap as a reference implementation. The project studies whether such a workflow can remain traceable, part-aware, and failure-contained while reducing the number of designs that require manual CAD and FEA attention.

This gap statement is intentionally narrower than a claim that NEMO is the first marine optimizer. Offshore and marine researchers already combine parametric models, FEA, surrogate models, and global optimization. For example, Gentils, Wang, and Kolios coupled parametric FEA with a genetic algorithm for an offshore wind support structure ([Gentils et al., 2017](https://doi.org/10.1016/j.apenergy.2017.05.009)). Zheng et al. used sensitivity analysis, surrogate models, and a genetic algorithm to reduce jacket-optimization cost ([Zheng et al., 2023](https://doi.org/10.1016/j.marstruc.2023.103372)). Wang et al. later reported a fast parametric FEA and genetic-algorithm tool for jacket structures ([Wang et al., 2024](https://doi.org/10.1016/j.marstruc.2024.103605)).

## Aim

The project aims to develop and evaluate an auditable, resource-conscious workflow for the parameterized mass optimization and validation preparation of marine structural components.

## Specific objectives

1. Define part parameters, units, bounds, materials, loads, constraints, fixed geometry, and semantic boundary roles in inspectable source files.
2. Develop first-order analytical models for mass, stress, yield-based factor of safety, and displacement.
3. explore each design space with seeded Latin-hypercube sampling.
4. Implement bounded, scaled, multi-start Nelder-Mead optimization.
5. Preserve failed evaluations without terminating a complete optimization campaign.
6. Implement a versioned file protocol between external Python and an Autodesk Fusion add-in.
7. Generate native Fusion geometry, STEP files, optional STL files, and semantic boundary metadata.
8. Test each generator over a baseline and 20 seeded design vectors.
9. Prepare baseline and finalist packages for manual Fusion Static Stress studies.
10. Demonstrate the complete method with the bracket proof of concept.
11. Show how the same method extends to a lifting padeye and stabilizer fin.
12. State the validation work required before any manufacturing or service decision.

## Research questions

1. Can one part-aware software architecture represent and process a bracket, padeye, and stabilizer without adding bracket-only assumptions to shared workflow code?
2. Can Latin-hypercube sampling and multi-start bounded Nelder-Mead search find lower-mass analytically feasible candidates for all three parts?
3. Can the Fusion bridge rebuild valid native CAD and identify every required semantic boundary role across bounded geometry changes?
4. How closely do analytical mass estimates agree with the Fusion CAD mass for the baseline and lightest selected finalist?
5. What evidence is still required before the analytical candidates can be treated as validated structural designs?
6. What lessons does the bracket proof of concept provide for future padeye and stabilizer FEA studies?

## Research perspectives and guiding questions

### Perspective 1: Structural mechanics and model fidelity

- Which physical quantities does each analytical model estimate?
- Which load paths and failure modes can the equations represent?
- Which local effects do the equations omit?
- When does a linear static model remain valid?
- What evidence is required to compare analytical and FEA results?

### Perspective 2: Optimization and design-space exploration

- Why is a derivative-free method appropriate for this implementation?
- What benefits does Latin-hypercube sampling provide before local search?
- How do scaling, clipping, penalties, and multiple starts affect the search?
- Does the minimum penalized objective always correspond to a feasible design?
- What can the project claim about optimality?

### Perspective 3: CAD-CAE integration and simulation intent

- How does the workflow move parameters from external Python into Fusion?
- How does it preserve load and support meaning after geometry changes?
- What happens when topology changes or a CAD operation fails?
- Which results can the public Fusion API return reliably?
- Why does the project separate CAD automation from manual FEA?

### Perspective 4: Marine application and engineering practice

- Why were a bracket, padeye, and stabilizer selected?
- How do the parts represent different marine structural load paths?
- Which marine rules or standards would govern later detailed design?
- Which effects of fatigue, corrosion, fabrication, and service loading remain outside the screening models?

### Perspective 5: Verification, validation, and traceability

- How does the project distinguish code verification, CAD verification, and structural validation?
- Can each reported result be traced to inputs, code, run records, and artifacts?
- How are solver input mistakes detected?
- What minimum FEA record is needed for credible comparison?
- What evidence is needed before physical testing?

### Perspective 6: Practical and educational value

- Can the workflow run with normal desktop tools and a small project team?
- Which tasks are automated, and which tasks require engineering judgment?
- Does the architecture make limitations visible to a student, supervisor, or reviewer?
- Can the bracket demonstration communicate the original project intent without overstating completion?

# Proposed report structure and page budget

The final LaTeX report will use the university title-page and preliminary-page format. The body will use the following minimum page budget:

| Chapter | Planned content | Target pages |
|---|---|---:|
| 1. Introduction | Background, problem, aim, objectives, questions, contribution, scope, limitations, report organization | 7-8 |
| 2. Literature Review | Structural optimization, sampling, Nelder-Mead, multi-fidelity methods, CAD-CAE integration, simulation intent, marine applications, FEA credibility, research gap | 15-17 |
| 3. Methodology and System Development | Research design, requirements, architecture, data contracts, all three analytical models, optimization, Fusion bridge, boundary metadata, bracket FEA procedure, extension method | 17-19 |
| 4. Results and Discussion | Tests, sampling, multi-start optimization, baseline and finalist comparisons, CAD sweeps, CAD mass comparison, bracket FEA quality-control finding, limitations | 13-15 |
| 5. Conclusions and Recommendations | Answers to research questions, contributions, limitations, immediate validation work, future development | 5-6 |
| **Planned numbered-chapter total** |  | **57-65** |

Appendices will hold the complete parameter tables, equations, command procedures, schema examples, validation checklist, selected run data, and code extracts. These pages will not be used to satisfy the 50-page body requirement.

# Draft report text

## 1. Introduction

### 1.1 Background

Marine vessels and offshore systems use many secondary structural components. Examples include equipment foundations, brackets, lifting points, appendage roots, and internal stiffeners. These parts may be small relative to the complete vessel, but they transfer concentrated loads into larger structures. Poor detailing can cause excessive deformation, local yielding, fatigue cracking, fastener failure, weld failure, or loss of attached equipment.

Mass also matters. Added structural mass increases material use and can affect vessel displacement, payload, fuel demand, installation effort, and center-of-gravity management. Removing material without a controlled analysis can reduce stiffness and strength. Marine component design is therefore a constrained problem. A designer seeks lower mass while maintaining defined limits for stress, factor of safety, displacement, fatigue resistance, buckling, fabrication, and service durability.

Traditional iteration often moves between calculations, CAD edits, and occasional FEA studies. This process can produce a suitable design, but it examines only a small portion of a multi-variable design space. It can also separate the evidence. Dimensions may exist in one document, loads in another, analysis results in screenshots, and CAD history in a proprietary file. This separation makes later checking and reproduction difficult.

Parametric modeling changes this process. A parameterized model represents a family of designs rather than one fixed design. An optimizer can then vary the dimensions, evaluate the response, and compare candidates. Park and Dang showed how programming interfaces can connect commercial CAD and CAE tools into automated structural optimization loops ([Park and Dang, 2010](https://doi.org/10.1016/j.cad.2010.06.003)). Such automation still faces a difficult problem. A change in geometry can change the faces, edges, and topology used by a mesh, load, or support. Nolan et al. described this wider problem as the preservation of simulation intent ([Nolan et al., 2015](https://doi.org/10.1016/j.cad.2014.08.030)).

NEMO was developed in response to these linked design and implementation problems. It combines a Python optimization application with an Autodesk Fusion add-in. The external application stores the engineering definitions, evaluates analytical screening models, explores design spaces, records runs, and selects candidates. The add-in rebuilds native CAD, calculates physical properties, exports neutral geometry, and describes the faces associated with engineering boundary roles.

The original concept aimed to solve Fusion FEA inside every optimization iteration. An API investigation found no reliable public Python interface or stable text command for starting Static Stress solves and extracting the required results. The project therefore adopted a resource-conscious sequence. Analytical models guide the search. Fusion generates CAD for selected candidates. An engineer then creates and checks the final Static Stress studies manually.

This change reduced automation but improved the credibility of the project boundary. The software does not invent unavailable FEA outputs. A CAD-only response contains mass, volume, and artifact paths, while stress, factor of safety, and displacement remain empty. A reserved open-source FEA mode also returns a controlled failure because its Gmsh and CalculiX implementation does not yet exist.

### 1.2 Problem statement

The project addresses two related problems.

The first problem is engineering efficiency. Manual iteration does not systematically explore the combined effects of plate dimensions, stiffener dimensions, fillet radii, lug geometry, spar positions, and reinforcement dimensions. High-fidelity FEA for every candidate would require more time and computing effort than the project can support.

The second problem is traceability. A useful workflow must preserve the connection between the engineering definition, candidate dimensions, calculated metrics, CAD geometry, load and support regions, and validation record. If geometry changes invalidate a boundary selection, the workflow must expose that condition instead of silently reporting success.

### 1.3 Research contribution

The project contribution has four parts.

First, NEMO defines each part through one unit-aware manifest. The manifest contains exact parameter names, units, bounds, baselines, material properties, loads, constraints, fixed geometry, and semantic boundary roles. The same definition informs evaluation, optimization, logging, validation packaging, and Fusion generation.

Second, NEMO provides a failure-contained optimization pipeline. It scales every design variable to the interval from zero to one, clips candidates at the bounds, applies explicit penalties, caches repeated evaluations, and records every unique evaluation. Invalid candidates and unavailable evaluators return a large controlled objective instead of stopping the search.

Third, NEMO provides a simple bridge between two Python environments. The external environment cannot directly import or control Fusion. The Fusion add-in cannot use the complete external dependency environment. The bridge exchanges versioned JSON files through a serialized channel and correlates each response by run identifier and iteration.

Fourth, NEMO records semantic boundary metadata. Each generated CAD model identifies regions such as `fixed_support`, `equipment_load`, `pin_bearing`, `pressure_band_1`, and `tip_monitor`. The metadata stores geometric selectors and face signatures. This approach does not guarantee permanent face identity, but it makes boundary intent explicit and checkable.

### 1.4 Scope

The completed scope includes:

- three registered part definitions;
- first-order linear-elastic screening models;
- continuous bounded variables;
- mass minimization with factor-of-safety and displacement penalties;
- random and Latin-hypercube sampling;
- bounded multi-start Nelder-Mead optimization;
- CSV and JSON run records;
- a Streamlit results dashboard;
- native Fusion generators for all three parts;
- STEP and STL export;
- semantic boundary metadata;
- baseline plus 20-vector CAD generator sweeps;
- baseline plus five-finalist validation packages; and
- a bracket Static Stress setup demonstration.

The completed scope does not include certified design, classification approval, automated Fusion FEA, open-source FEA, physical testing, uncertainty quantification, probabilistic reliability, fatigue, buckling, corrosion, weld-detail assessment, nonlinear pin contact, bolt preload, impact, vibration, or stabilizer CFD.

### 1.5 Safety and claim boundary

The analytical outputs are screening estimates. CAD mass is a geometry result, not an FEA result. A Fusion study is not credible only because it solved. Its material, load, support, contact, mesh, reactions, and result interpretation must also be correct.

The project can claim the “best design found within this parameterized search.” It cannot claim a global optimum. It also cannot claim that a selected design is safe for manufacture or service.

## 2. Literature review

### 2.1 Structural optimization as a constrained search

Structural optimization formalizes the selection of design variables to improve an objective while satisfying constraints. The objective may represent mass, cost, compliance, displacement, stress, fatigue damage, or several competing measures. The design variables may control geometry, material, topology, or manufacturing choices.

NEMO performs size and shape parameter optimization. It does not perform topology optimization. The number and general arrangement of major features remain fixed. The optimizer changes dimensions such as thickness, height, length, position, and radius inside declared bounds. This restriction keeps the generated parts recognizable and makes each candidate compatible with a predefined engineering interpretation.

The objective in NEMO is mass plus penalties. Let \(m(\mathbf{x})\) be the estimated mass for design vector \(\mathbf{x}\). Let \(F_{\min}\) be the minimum factor of safety and \(\delta_{\max}\) be the maximum displacement. The implemented objective is:

\[
J(\mathbf{x}) =
m(\mathbf{x}) +
w\left[
\left(
\frac{\max(0,F_{\min}-F(\mathbf{x}))}{F_{\min}}
\right)^2
+
\left(
\frac{\max(0,\delta(\mathbf{x})-\delta_{\max})}{\delta_{\max}}
\right)^2
\right],
\]

where \(w=100\) for the three current parts.

This objective makes feasible mass the objective value when both constraints pass. It gives an infeasible design a larger value based on the normalized constraint violations. The final selection must still filter explicitly for feasibility. The stabilizer results show why this step matters. The smallest penalized objective from each stabilizer optimization run belonged to a design with factor of safety below 2.5. The validation package therefore selected the lightest explicitly feasible rows instead.

### 2.2 Derivative-free optimization

Many engineering simulations behave as black-box functions from the optimizer’s viewpoint. The optimizer supplies dimensions and receives calculated outputs. It may not have exact derivatives. CAD regeneration, meshing changes, solver tolerances, and failed candidates can also make numerical gradients unreliable.

Direct-search methods use objective values without requiring analytical gradients. Kolda, Lewis, and Torczon reviewed the theoretical and practical development of direct-search methods and distinguished methods with stronger convergence properties from heuristic searches ([Kolda et al., 2003](https://doi.org/10.1137/S003614450242889)). Derivative-free methods remain useful when derivatives are unavailable or expensive, but the absence of gradients does not remove the need for careful scaling, constraints, termination rules, and multiple starts.

### 2.3 Nelder-Mead simplex search

Nelder and Mead introduced their simplex method in 1965 ([Nelder and Mead, 1965](https://doi.org/10.1093/comjnl/7.4.308)). In an \(n\)-dimensional space, the method maintains \(n+1\) vertices. It ranks the vertices by objective value and replaces poor vertices through reflection, expansion, contraction, or shrink operations.

NEMO uses the standard coefficients:

- reflection coefficient \(\alpha=1\);
- expansion coefficient \(\gamma=2\);
- contraction coefficient \(\rho=0.5\); and
- shrink coefficient \(\sigma=0.5\).

The implementation stops when it reaches the iteration limit or when the spread between simplex objective values is below the tolerance. The current full pipeline uses 80 iterations per start.

Nelder-Mead is attractive for this project because the three problems have six or nine continuous variables and inexpensive analytical evaluations. The method is also simple enough to implement without an external optimization library.

The method has important limits. Lagarias et al. proved limited convergence results in low dimensions and discussed counterexamples in which the method can approach a non-minimizer ([Lagarias et al., 1998](https://doi.org/10.1137/S1052623496303470)). Nelder-Mead is a local search, so the result depends on the initial simplex and the design landscape. NEMO therefore uses three starts: the configured baseline and two promising sampled candidates. It reports the best feasible design found rather than a global optimum.

### 2.4 Variable scaling and bounds

The physical variables have different magnitudes. A stabilizer spar position uses percent chord, while a reinforcement length uses millimeters. Directly optimizing these values would distort the initial simplex and step sizes.

NEMO maps each physical variable \(x_i\) into:

\[
z_i = \frac{x_i-l_i}{u_i-l_i},
\]

where \(l_i\) and \(u_i\) are the lower and upper bounds. The optimizer operates on \(z_i\in[0,1]\). The evaluator converts the scaled coordinates back to physical units. All trial coordinates are clipped at the scaled bounds.

This scaling gives each variable the same numerical range. It does not make the physics equally sensitive to each variable. Sensitivity still depends on the equations and geometry.

### 2.5 Latin-hypercube sampling

McKay, Beckman, and Conover introduced Latin-hypercube sampling as a stratified alternative to simple random sampling for computer experiments ([McKay et al., 1979](https://doi.org/10.1080/00401706.1979.10489755)). For each variable, an \(N\)-point Latin hypercube samples once from each of \(N\) equal-probability intervals. Independent permutations combine the one-dimensional samples into \(N\) multi-dimensional points.

NEMO uses 60 samples per part and seed 42. The seed makes the sampling campaign repeatable. The sampling phase has three purposes:

1. inspect the range of predicted responses;
2. locate feasible low-mass starting points; and
3. reduce reliance on one baseline-start local search.

The sample is not a statistical proof that the entire design space has been covered. Sixty points are sparse in a nine-dimensional space. The sample is a practical exploration stage.

### 2.6 Low-fidelity screening and high-fidelity validation

Engineering optimization often uses models with different costs and accuracies. Peherstorfer, Willcox, and Gunzburger reviewed multi-fidelity methods that combine inexpensive low-fidelity models with expensive high-fidelity models ([Peherstorfer et al., 2018](https://doi.org/10.1137/16M1082469)). A formal multi-fidelity optimizer keeps the high-fidelity model in the loop to improve accuracy or convergence.

NEMO does not yet implement formal multi-fidelity optimization. The current analytical model guides the search, while CAD and manual FEA follow as separate validation stages. The correct term is therefore a **tiered-fidelity workflow**, not a closed multi-fidelity optimizer.

The distinction matters. The analytical optimum is not corrected automatically by FEA. If FEA shows that the analytical model is optimistic, an engineer must revise assumptions, reject candidates, or recalibrate the model. Future work can close this loop by fitting correction models or by implementing the reserved open-source FEA evaluator.

### 2.7 CAD-CAE integration

Automated structural optimization requires dependable communication between geometry, analysis, and optimization. Park and Dang implemented an automated commercial CAD-CAE loop using scripting, programming interfaces, response surfaces, and radial-basis-function metamodels ([Park and Dang, 2010](https://doi.org/10.1016/j.cad.2010.06.003)). Their work confirms that integration can reduce repetitive work and computational cost. It also shows that metamodel error becomes an additional source of uncertainty.

Li et al. described a more recent parametric optimization method based on extended voxels. Their representation supports a closed loop among design, simulation, and optimization while carrying design and simulation meaning ([Li et al., 2023](https://doi.org/10.1016/j.cad.2023.103528)). These studies establish that automated CAD-CAE optimization is not itself the novel part of NEMO.

NEMO uses a more modest architecture. External Python handles optimization and evidence records. Fusion handles native CAD. The two environments exchange JSON files. This choice avoids undocumented process injection and third-party dependencies inside Fusion. It also creates artifacts that a reviewer can inspect.

### 2.8 Simulation intent and semantic boundary roles

Geometry changes can break an analysis even when the regenerated solid looks correct. A load attached to “Face 42” can move to the wrong location or disappear after a feature changes the boundary representation.

Nolan et al. defined simulation intent as the high-level modeling and idealization decisions needed for a fit-for-purpose analysis ([Nolan et al., 2015](https://doi.org/10.1016/j.cad.2014.08.030)). Their work attaches analysis meaning to regions and interfaces instead of relying only on unstable low-level topology.

NEMO applies the same general principle at a smaller scale. Each part definition declares semantic boundary roles:

- bracket: `fixed_support` and `equipment_load`;
- padeye: `fixed_support` and `pin_bearing`;
- stabilizer: `fixed_support`, four pressure bands, and `tip_monitor`.

The Fusion generator uses geometric rules to select matching faces. It records face area, centroid, normal, bounding box, and cylinder data where available. The later FEA procedure uses these roles to find and verify the intended regions.

This method improves traceability but does not eliminate all ambiguity. A human must still inspect the selected faces before a manual solve.

### 2.9 Marine structural optimization

Marine structural optimization must represent realistic loads, supports, and failure modes. Gentils et al. optimized an offshore wind support structure with parametric FEA and a genetic algorithm. Their constraints included stress, displacement, vibration, buckling, and fatigue ([Gentils et al., 2017](https://doi.org/10.1016/j.apenergy.2017.05.009)). Their study reported a 19.8 percent mass reduction for the complete support structure.

Zheng et al. later used sensitivity analysis and surrogate models for jacket structures. They included natural frequency, displacement, stress, buckling, and later fatigue checks ([Zheng et al., 2023](https://doi.org/10.1016/j.marstruc.2023.103372)). Wang et al. used realistic loading and boundary assumptions in a fast parametric FEA tool and compared parametric and genetic-algorithm optimization strategies ([Wang et al., 2024](https://doi.org/10.1016/j.marstruc.2024.103605)).

These studies provide two lessons for NEMO. First, mass reduction must remain subject to several engineering constraints. Second, simple fixed supports and prescribed loads can change the selected design if they do not represent the real system. NEMO therefore treats its three load cases as project envelopes, not complete marine design cases.

### 2.10 Brackets

The bracket is a common static-stress example because it has a clear load path and several geometric stress raisers. Autodesk lists mounting brackets among suitable applications when the assumptions of linear static analysis hold ([Autodesk, Static Stress Study](https://help.autodesk.com/cloudhelp/ENU/Fusion-Simulate/files/SIM-STATIC-STRESS-ANALYSIS.htm)).

The NEMO bracket represents a small equipment foundation. The model includes a baseplate, four mounting holes, two ribs, and rib-root fillets. The analytical model treats the load path as an equivalent cantilever. This approximation captures broad bending trends but omits bolt bearing, fastener preload, weld details, local plate bending, and three-dimensional load sharing.

### 2.11 Padeyes and pinned connections

Padeyes transfer lifting forces through a pin hole into a lug, welds, gussets, and supporting structure. Local contact, net-section tension, bearing, shear-out, bending, and weld stresses can govern.

Soh and Soh compared simplified two-dimensional padeye models with a three-dimensional finite-element solution. Their work showed that conservative manual formulas can produce overdesigned padeyes and that model selection affects practical results ([Soh and Soh, 1989](https://doi.org/10.1016/0143-974X(89)90071-0)). Liu, Zhou, and Tan used FEA to study padeye stress and deformation and then formulated an optimization problem to reduce steel use ([Liu et al., 2013](https://doi.org/10.4028/www.scientific.net/AMR.658.399)).

Pinned connections are sensitive to clearance and three-dimensional contact. Pedersen showed that contact modeling and geometric refinement can reduce the stress concentration around a pin-loaded hole ([Pedersen, 2019](https://doi.org/10.1177/0309324719842766)). NEMO’s padeye analytical model does not include explicit pin contact. The future Fusion study must therefore use an appropriate bearing load or contact representation and inspect the hole, lug root, gussets, and weld interfaces.

Marine lifting design also requires a governing rule set. DNV-ST-N001 addresses marine operations, load cases, and structural strength for offshore movements and lifting operations ([DNV, 2023](https://www.dnv.com/energy/standards-guidelines/dnv-st-n001-marine-operations-and-marine-warranty/)). Lloyd’s Register publishes a Code for Lifting Appliances in a Marine Environment that also covers materials, fabrication, testing, marking, surveys, and documentation ([Lloyd’s Register, 2026](https://www.lr.org/en/knowledge/lloyds-register-rules/code-for-lifting-appliances-in-a-marine-environment/)). NEMO does not claim compliance with either document.

### 2.12 Stabilizer fins

The stabilizer case differs from the bracket and padeye. It has a fixed hydrodynamic envelope and a parameterized internal structure. The outer profile is NACA 0015. Abbott, von Doenhoff, and Stivers documented the NACA four-digit family and its aerodynamic data in NACA Report 824 ([Abbott et al., 1945](https://ntrs.nasa.gov/citations/19930090976)).

The NEMO model retains an 800 mm span, 500 mm root chord, 250 mm tip chord, 12-degree sweep, and three fixed rib stations. It changes skin thickness, two spar positions, two spar thicknesses, rib thickness, root insert dimensions, and root fillet radius.

The prescribed resultant load comes from:

\[
F_d =
\frac{1}{2}\rho V^2 S C_L \gamma_d,
\]

with seawater density \(1025\,\mathrm{kg/m^3}\), velocity \(8\,\mathrm{m/s}\), lift coefficient 0.8, planform area \(0.3\,\mathrm{m^2}\), and dynamic factor 1.5. This gives \(11\,808\,\mathrm{N}\).

The load is divided into four pressure bands with relative weights 1.00, 0.93, 0.75, and 0.40. These weights are engineering assumptions. They are not CFD results. The optimization therefore sizes an internal structure under a prescribed load. It does not optimize hydrodynamic performance.

### 2.13 Linear static FEA

Autodesk states that a Fusion Static Stress study assumes small deformation, unchanged load direction, constant material properties, and linear elastic material response ([Autodesk, Static Stress Study](https://help.autodesk.com/cloudhelp/ENU/Fusion-Simulate/files/SIM-STATIC-STRESS-ANALYSIS.htm)). These assumptions match the intended screening comparison, provided the candidates remain elastic and the supports and loads represent the physical case.

A complete study requires geometry, material, constraints, loads, contact behavior, a mesh, a solution, and result review ([Autodesk, Static Stress Setup](https://help.autodesk.com/view/fusion360/ENU/?guid=SIM-SSA)). Reaction forces provide an important equilibrium check. Autodesk states that the support reactions should oppose the total applied load ([Autodesk, Reaction Results](https://help.autodesk.com/cloudhelp/ENU/Fusion-Simulate/files/SIM-REACTION-FORCE-VIEW-CONCEPT.htm)).

Mesh convergence is also necessary. Autodesk notes that coarse meshes commonly underpredict stress and that stress is more mesh-sensitive than displacement ([Autodesk, Mesh Convergence](https://help.autodesk.com/cloudhelp/ENU/Fusion-Simulate/files/SIM-MESH-CONVERGENCE.htm)). It recommends comparing the same geometric location across refinements rather than comparing unrelated maximum-stress nodes.

### 2.14 Verification, validation, and model credibility

Verification asks whether the equations and software were solved or implemented correctly. Validation asks whether the model represents the real system well enough for its intended use. ASME V&V 10 provides a framework and common language for verification, validation, and uncertainty quantification in computational solid mechanics ([ASME, 2019](https://www.asme.org/codes-standards/find-codes-standards/standard-for-verification-and-validation-in-computational-solid-mechanics)).

NASA-STD-7009B emphasizes intended use, acceptance criteria, input pedigree, result uncertainty, sensitivity, validation, verification, and communicated credibility ([NASA, 2024](https://standards.nasa.gov/standard/nasa/nasa-std-7009)). These principles are relevant even though NEMO is not a NASA system. A model can be acceptable for screening and unacceptable for manufacture. Credibility depends on the decision the model supports.

NEMO therefore separates four evidence levels:

1. **Software verification:** automated tests check calculations, schemas, bounds, logs, and failure handling.
2. **CAD verification:** Fusion sweeps check that bounded inputs create one valid solid with positive volume and required boundary roles.
3. **FEA verification:** manual checks must confirm the study input, equilibrium, mesh convergence, and result extraction.
4. **Physical validation:** later tests must compare predicted and measured response.

### 2.15 Literature synthesis

The literature establishes the methods that NEMO uses. Nelder-Mead supplies a compact derivative-free local search. Latin-hypercube sampling spreads starting evidence across bounded variables. Tiered-fidelity practice justifies using inexpensive models before expensive validation. CAD-CAE research identifies geometry and boundary transfer as central automation problems. Marine optimization studies show that mass is only one of many design criteria. V&V standards require a clear intended use and evidence chain.

The project contribution is the way these established methods are combined, constrained, and exposed in an inspectable student-scale implementation.

## 3. Methodology and system development

### 3.1 Research design

The project uses a design-and-evaluate methodology. It creates a working engineering software artifact, tests its components, applies it to three cases, and evaluates the outputs against declared requirements.

The study has four phases:

1. define engineering inputs and screening models;
2. explore and optimize the design spaces;
3. generate and verify CAD artifacts; and
4. prepare and inspect structural validation evidence.

### 3.2 System architecture

The external Python package contains the part registry, analytical models, samplers, optimizer, evaluator, logger, validation-package generator, command-line interface, and dashboard reader.

The Fusion add-in runs inside Fusion’s embedded Python environment. Autodesk documents Python scripts and add-ins with `run` and `stop` entry points and a JSON manifest ([Autodesk, Scripts and Add-Ins](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-9701BBA7-EC0E-4016-A9C8-964AA4838954)). NEMOBridge watches a request file, activates or creates a Fusion design, validates the payload, rebuilds the selected part, calculates physical properties, exports artifacts, and writes a response.

The bridge uses one shared channel at `data/runs/active`. The external side acquires an inter-process lock before writing a request. It writes JSON to a temporary file and replaces the target atomically. The response must match both the requested run identifier and iteration. The bridge retries atomic replacement to tolerate short Windows file locks.

This architecture favors simplicity and traceability. It does not support concurrent CAD requests.

### 3.3 Versioned data contract

Schema version 2 requests contain:

- `schema_version`;
- `part_id`;
- `run_id`;
- `iteration`;
- `mode`;
- `parameters`; and
- `artifact_formats`.

Schema version 1 is retained for the original bracket demonstration. It used `parameters_mm` and implied the bracket part.

A response contains status, metrics, artifact paths, and any error. A Fusion CAD response has `partial` status because CAD can provide volume and mass without structural metrics. An invalid request returns `failed` status and objective \(10^9\).

### 3.4 Bracket engineering definition

The bracket carries a 50 kg equipment mass with dynamic factor 3:

\[
F_d = 50(9.81)(3) = 1471.5\,\mathrm{N}.
\]

Fusion does not accept the decimal force value in the current user workflow. The manual Fusion study must therefore use the conservative integer value of 1472 N. This rounding changes the load by approximately 0.034 percent.

The material is project-defined Aluminum 6061-T6:

- density: \(2700\,\mathrm{kg/m^3}\);
- yield strength: \(276\,\mathrm{MPa}\);
- elastic modulus: \(68.9\,\mathrm{GPa}\); and
- Poisson ratio: 0.33.

The six variables and bounds are:

| Variable | Unit | Lower | Baseline | Upper |
|---|---:|---:|---:|---:|
| Baseplate length | mm | 100 | 150 | 200 |
| Baseplate width | mm | 80 | 100 | 150 |
| Baseplate thickness | mm | 4 | 8 | 15 |
| Rib height | mm | 20 | 40 | 60 |
| Rib thickness | mm | 3 | 6 | 10 |
| Fillet radius | mm | 2 | 5 | 10 |

The fixed geometry includes four 10 mm mounting holes and two ribs. Acceptance requires factor of safety at least 2.5 and displacement no more than 0.5 mm.

### 3.5 Bracket analytical model

The bracket volume includes the baseplate, hole subtraction, two triangular ribs, and an approximate fillet contribution:

\[
V =
L W t_b
- n_h\pi\left(\frac{d_h}{2}\right)^2t_b
+ n_r\frac{Lh_rt_r}{2}
+n_r\frac{\pi r_f^2}{4}\max(0.35W,t_r).
\]

The load moment is:

\[
M=F_d e,\qquad
e=\max(0.03,0.35L+0.02).
\]

The effective section modulus is:

\[
Z_{\mathrm{eff}} =
\frac{Wt_b^2}{6}
+0.65n_r\frac{t_rh_r^2}{6}.
\]

The stress estimate is:

\[
\sigma =
\frac{M}{Z_{\mathrm{eff}}}K_t,
\qquad
K_t=\max\left(1.08,1.35-\frac{r_f[\mathrm{mm}]}{40}\right).
\]

The displacement model uses:

\[
I_{\mathrm{eff}} =
\frac{Wt_b^3}{12}
+0.45n_r\frac{t_rh_r^3}{36},
\]

\[
\delta = \frac{F_de^3}{3EI_{\mathrm{eff}}}.
\]

The model preserves the expected broad trends. Increased plate or rib thickness raises mass and stiffness. Increased rib height raises bending stiffness strongly. Increased fillet radius lowers the assumed stress concentration. The model does not resolve bolt, weld, contact, or local shell behavior.

### 3.6 Padeye engineering definition and model

The padeye carries a 500 kg working load with dynamic factor 3:

\[
F_d=500(9.81)(3)=14\,715\,\mathrm{N}.
\]

The project material is S275 structural steel with density \(7850\,\mathrm{kg/m^3}\), yield strength \(275\,\mathrm{MPa}\), elastic modulus \(210\,\mathrm{GPa}\), and Poisson ratio 0.30.

Nine variables control doubler-plate dimensions, lug dimensions, neck width, gusset dimensions, and fillet radius. The fixed pin-hole diameter is 50 mm and the model has two gussets.

The volume model combines the doubler plate, tapered lug and crown, hole subtraction, two triangular gussets, and a fillet approximation.

The model calculates four stress candidates:

1. net-section tension with a fillet-dependent concentration factor;
2. pin-bearing stress;
3. equivalent shear-out stress; and
4. lateral bending stress from an assumed 25 percent side-load component.

The reported stress is the maximum of these four estimates. The displacement combines axial and lateral components. This is useful for screening but does not replace a pin-contact and weld assessment.

### 3.7 Stabilizer engineering definition and model

The stabilizer uses the fixed external geometry and load described in Section 2.12. Nine variables control skin, spar, rib, insert, and fillet geometry.

The volume model combines:

- two-sided skin area;
- front and rear spar webs;
- three internal ribs;
- a root insert;
- a fixed root flange; and
- a root-fillet approximation.

The NACA thickness equation estimates spar heights at the two chord positions. The root section model combines skin, spar, and insert contributions to the second moment of area.

The root moment uses a load centroid at 40 percent span:

\[
M_r = 0.40F_d b.
\]

The stress combines bending and shear:

\[
\sigma_{\mathrm{eq}} =
\sqrt{(K_t\sigma_b)^2+3\tau^2}.
\]

The displacement estimate is:

\[
\delta =
\frac{F_db^3}{8EI_{\mathrm{eff}}}.
\]

The model does not calculate pressure from vessel motion, angle of attack, free-surface effects, ventilation, cavitation, or actuator dynamics.

### 3.8 Sampling and optimization procedure

For each part, the full pipeline:

1. evaluates the configured baseline;
2. generates 60 Latin-hypercube samples with seed 42;
3. evaluates every sample analytically;
4. selects promising feasible sampled designs;
5. starts Nelder-Mead from the baseline;
6. starts Nelder-Mead from two selected sampled designs;
7. permits at most 80 iterations per start;
8. combines all run records;
9. filters explicitly for feasibility;
10. selects the baseline and five light finalists; and
11. creates Fusion requests and a validation checklist.

Each result row stores the schema, part, run, iteration, mode, status, parameters, volume, mass, stress, factor of safety, displacement, objective, error, and timestamp.

### 3.9 Fusion geometry generation

The bracket generator creates one baseplate, cuts four holes, adds two triangular ribs, joins the bodies, and applies four long rib-root fillets.

The padeye generator creates a doubler plate, tapered lug and crown, pin bore, two root fillets, and overlapping gussets. It requires one connected solid.

The stabilizer generator creates a root flange, lofted NACA outer envelope, root fillet, hollow interior, two spars, three ribs, a root insert, and pressure-band splits. It also requires one connected solid.

The generator reads the same part-definition JSON files as the external Python package. This avoids maintaining separate values for bounds, materials, and fixed geometry.

Autodesk provides public API methods for physical properties and neutral-file export. The physical-properties API supports mass and volume extraction ([Autodesk, Physical Properties](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Component_getPhysicalProperties.htm)). The export manager supports STEP and STL workflows ([Autodesk, Export Manager](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExportManager_execute.htm)).

### 3.10 CAD generator verification

Each part generator was tested with its baseline and 20 seeded Latin-hypercube vectors. Acceptance required:

- one connected solid;
- positive volume;
- successful STEP export;
- successful boundary metadata export; and
- at least one matched face for every required semantic role.

The final recorded sweeps used generator version 2.4.

### 3.11 Bracket proof-of-concept workflow

The bracket preserves the original project demonstration. The live flow is:

1. start Fusion;
2. start NEMOBridge;
3. start the external bracket pipeline;
4. evaluate and optimize the analytical model;
5. package the baseline and finalists;
6. regenerate a requested bracket in Fusion;
7. inspect the native solid;
8. create a Static Stress study;
9. assign the project material;
10. fix the four mounting-hole cylindrical faces;
11. apply a total downward 1472 N load to the four upper sloping rib faces;
12. disable “force per entity” so that 1472 N is the combined load;
13. generate and inspect the mesh;
14. solve;
15. inspect stress, factor of safety, displacement, and reactions;
16. refine the mesh; and
17. record the results in the validation checklist.

The four upper sloping rib faces represent the equipment-load interface. They are the inclined top surfaces of both ribs, with two selectable faces on each rib.

### 3.12 FEA evidence rule

The available `Study Final.html` report records a load magnitude of 1.472 N. The intended integer load is 1472 N. The report therefore contains a factor-of-1000 input error.

The report can support these statements:

- the bracket geometry entered the Simulation workspace;
- the material, support, load, and mesh interfaces were exercised;
- the load was placed on the intended upper rib faces;
- the supports were placed at the four mounting holes; and
- Fusion produced a result report.

It cannot support the intended structural acceptance case. Its reported stress, displacement, and factor of safety must not appear as validated 1472 N results. Images from this report may be used only as setup and quality-control evidence. Each caption must state that the numerical result is invalid for the intended design load.

The corrected study must use 1472 N and record a support reaction close to 1472 N. It must also report the material properties, mesh settings, node and element count, stress, factor of safety, displacement, result locations, and convergence behavior.

### 3.13 Extension to padeye and stabilizer FEA

The padeye will use the same sequence with part-specific changes. The fixed support is the underside of the doubler plate. The 14,715 N load acts through the pin-bearing region. The model must inspect the hole, crown, net section, lug root, gusset roots, and welded interface. A later study should replace a simple bearing load with a pin and nonlinear contact when the required fidelity justifies it.

The stabilizer will fix the root flange. It will distribute the 11,808 N resultant over four pressure bands according to their normalized weights and actual areas. It will monitor the tip and inspect the root fillet, spars, skin-spar intersections, rib junctions, insert termination, and trailing edge. A later hydrodynamic study must replace the prescribed pressure pattern.

## 4. Results and discussion

### 4.1 Software verification results

The recorded offline test campaign passed 27 tests. Three Fusion-only tests were skipped during the offline run. The tests cover analytical behavior, multi-part definitions, optimizer behavior, handshakes, validation packages, dashboard reading, and Fusion generator contracts.

The Fusion sweep is a separate integration test because it requires an open desktop Fusion session and changes the shared request directory. It is not an ordinary offline unit test.

### 4.2 Baseline analytical results

| Part | Baseline mass (kg) | Stress (MPa) | Factor of safety | Displacement (mm) |
|---|---:|---:|---:|---:|
| Bracket | 0.418125 | 41.5321 | 6.6455 | 0.195642 |
| Padeye | 8.847625 | 46.1070 | 5.9644 | 0.013429 |
| Stabilizer | 19.655593 | 86.9853 | 3.1730 | 3.336750 |

All three baselines pass their analytical factor-of-safety and displacement constraints. The baseline margins also leave room for mass reduction.

### 4.3 Latin-hypercube results

Each part used 60 seeded samples.

| Part | Feasible samples | Lightest feasible sample mass (kg) | Sample FOS | Sample displacement (mm) |
|---|---:|---:|---:|---:|
| Bracket | 55/60 | 0.245687 | 10.4945 | 0.073331 |
| Padeye | 60/60 | 5.923561 | 4.9324 | 0.010449 |
| Stabilizer | 47/60 | 16.482802 | 2.7674 | 4.107578 |

The sample phase found lower-mass feasible designs for all parts. It did not approach the final mass achieved by local refinement. It still improved the multi-start strategy by providing starts away from the configured baselines.

### 4.4 Multi-start optimization

The bracket searches required 132, 126, and 129 recorded evaluations. The lightest feasible results were 0.126545 kg, 0.116928 kg, and 0.113396 kg.

The padeye searches required 108, 116, and 109 evaluations. The lightest feasible results were 3.837083 kg, 3.609310 kg, and 3.547772 kg.

The stabilizer searches required 110, 116, and 111 evaluations. Their lightest feasible results were 14.414066 kg, 14.315361 kg, and 14.391670 kg.

The different results confirm that starting points matter. The best result did not come from the baseline start for any part.

### 4.5 Selected analytical finalists

| Part | Baseline mass (kg) | Lightest selected mass (kg) | Analytical reduction | FOS | Displacement (mm) |
|---|---:|---:|---:|---:|---:|
| Bracket | 0.418125 | 0.113396 | 72.88% | 2.5386 | 0.369832 |
| Padeye | 8.847625 | 3.547772 | 59.90% | 2.6224 | 0.027933 |
| Stabilizer | 19.655593 | 14.315361 | 27.17% | 2.5149 | 3.822300 |

These reductions apply only to the analytical screening models and declared bounds. They are not validated service mass reductions.

### 4.6 Bound activity and engineering interpretation

The bracket finalist has baseplate length, baseplate width, baseplate thickness, and rib thickness near their lower bounds. Its rib height remains above the lower bound. This pattern reflects the model’s bending equations. Section depth preserves stiffness more efficiently than uniform plate mass.

The padeye finalist has several variables close to their lower bounds. Its fillet radius reaches the upper bound. The analytical concentration factor rewards a large fillet while the thin plates reduce mass. A detailed design must check whether the large fillet, minimum gauges, weld access, and gusset geometry are manufacturable.

The stabilizer finalist uses nearly minimum skin thickness, front spar at its forward bound, and rear spar at its aft bound. A wider spar separation increases the effective structural depth. The finalist retains added web, rib, insert, and fillet material because the factor-of-safety constraint is active.

When many variables meet a bound, the bounds are part of the result. The optimizer has not proved that the physical optimum lies there. It has shown that the screening model prefers values at the current admissible limits.

### 4.7 Penalized objective and feasibility

The stabilizer provides an important software and methodological result. Its smallest penalized objectives corresponded to factors of safety from 2.382 to 2.416, below the required 2.5. The 100-point penalty did not always make a slightly infeasible low-mass design worse than every feasible design.

The validation selector prevented this issue from reaching the finalist package because it filters for feasibility before ranking mass. The result shows that the objective penalty and the acceptance test serve different purposes. Future work can use stronger adaptive penalties or a constrained optimizer, but explicit feasibility filtering must remain.

### 4.8 CAD sweep results

The bracket and padeye Fusion tests each completed 21 of 21 vectors through the automated integration test. The stabilizer generated all 21 requested artifact sets, but the outer test process reached its 30-minute limit while reading the last response. A direct audit confirmed the completed artifacts.

Every recorded vector had:

- positive CAD volume;
- a STEP artifact;
- a boundary metadata artifact; and
- at least one face for every required semantic boundary role.

The padeye had one fixed-support face throughout the sweep. The stabilizer had one fixed-support face and one tip-monitor face. Its four pressure bands each contained external positive-side skin faces.

This evidence supports generator reliability over the tested vectors. It does not prove reliability over every possible point in a continuous design space.

### 4.9 Finalist CAD results

All 18 baseline and finalist requests completed with generator version 2.4. Each returned `partial` status, positive CAD mass, positive CAD volume, STEP geometry, and non-empty required boundary roles.

| Part | Analytical baseline (kg) | CAD baseline (kg) | Baseline difference | Analytical finalist (kg) | CAD finalist (kg) | Finalist difference |
|---|---:|---:|---:|---:|---:|---:|
| Bracket | 0.418125 | 0.422813 | +1.12% | 0.113396 | 0.114705 | +1.15% |
| Padeye | 8.847625 | 8.897280 | +0.56% | 3.547772 | 3.682600 | +3.80% |
| Stabilizer | 19.655593 | 19.297300 | -1.82% | 14.315361 | 14.400300 | +0.59% |

The analytical and CAD masses agree within approximately four percent for these six comparisons. This agreement verifies the broad volume approximations. It does not validate stress or displacement.

The padeye finalist has the largest mass difference. Its analytical model approximates tapered, crowned, gusseted, and filleted volumes. The native CAD generator resolves these shapes more exactly. The difference is therefore plausible and should be treated as model-form discrepancy.

### 4.10 Bracket FEA pilot and quality-control finding

The bracket Static Stress pilot confirms that the project reached the intended manual Simulation stage. The available report shows the bracket, mounting-hole supports, upper-rib load faces, material interface, mesh, and result interface.

The same report also exposes a critical input error. It records a 1.472 N force instead of 1472 N. The displayed structural outputs are therefore invalid for the intended case.

This finding is not only a missing result. It demonstrates why the workflow requires explicit validation records. A solver can complete successfully while answering the wrong engineering question. The magnitude, direction, “force per entity” option, and reaction balance must be checked before interpreting contours.

The final report may include the Fusion images as evidence of the procedure and error-detection process. It must not label the reported stress, factor of safety, or displacement as validated design results.

### 4.11 Research-question answers

**RQ1:** The shared architecture processes all three parts through one registry, evaluator, logger, optimizer, schema, validation generator, and bridge. Part-specific logic remains in manifests and model or CAD dispatch functions.

**RQ2:** The sampling and multi-start search found lower-mass analytically feasible candidates for all parts. The reported reductions range from 27.17 to 72.88 percent.

**RQ3:** The Fusion bridge generated the tested native solids and non-empty semantic boundary roles. Sixty-three sweep vectors and 18 validation-package requests completed at the artifact level, with the stated stabilizer test-harness timeout caveat.

**RQ4:** Analytical and Fusion CAD masses differed by less than four percent in the baseline and lightest-finalist comparisons. This supports broad volume consistency only.

**RQ5:** The project still needs corrected loads, reaction balance, mesh-converged FEA, analytical-to-FEA comparison, relevant code checks, and physical tests.

**RQ6:** The bracket proves the workflow and exposes the principal manual-control risks. The padeye and stabilizer must repeat the procedure with part-specific boundary conditions and higher-fidelity physics.

### 4.12 Limitations

The analytical models have deterministic project inputs. They do not propagate uncertainty in loads, yield strength, modulus, density, manufacturing tolerances, or model coefficients.

The dynamic factors are static multipliers. They are not results from vibration, impact, roll-motion, or transient analyses.

The fixed supports can be too stiff. Real bolts, welds, supporting plates, pins, bearings, and actuator structures have compliance.

The yield-based factor of safety does not cover fatigue, fracture, buckling, wear, corrosion, or weld quality.

The optimizer handles continuous variables. It does not select stock gauges, rib counts, materials, fastener sizes, or manufacturing methods.

The current penalty can rank a slightly infeasible design ahead of feasible designs. Explicit finalist filtering corrects package selection but does not change the optimizer’s search pressure.

The Fusion channel is single-user and serial. It does not support parallel requests.

The public Fusion workflow does not automate Static Stress solving or result extraction.

The available bracket FEA report uses the wrong load magnitude.

## 5. Conclusions and recommendations

### 5.1 Conclusions

The project developed a working, part-aware optimization and CAD-generation workflow for three marine structural components. The software stores engineering inputs in unit-aware manifests, evaluates first-order models, explores bounded design spaces, performs multi-start direct search, records results, selects feasible finalists, and generates native Fusion artifacts.

The bracket proof of concept shows the complete intended path from engineering definition to a manual Static Stress study. The padeye and stabilizer show that the architecture can support different variables, materials, loads, geometric generators, and boundary roles.

The analytical campaigns found substantial mass reductions within the chosen bounds. These reductions are screening outcomes. The optimizer often moved variables to their bounds and factors of safety close to the acceptance limit. This behavior increases the need for detailed validation.

The CAD campaigns provide stronger evidence than the original report draft contained. All tested parts generated positive-volume geometry and semantic boundary metadata. Analytical and CAD masses showed close broad agreement for the compared baselines and finalists.

The FEA evidence remains incomplete. The available bracket report used a force of 1.472 N instead of 1472 N. It can document the procedure but cannot validate the intended structural case.

The project’s defensible contribution is an auditable and resource-conscious workflow. It is not a new optimization algorithm, a fully closed multi-fidelity system, or a certified design method.

### 5.2 Immediate work before submission

1. Rerun the bracket baseline Static Stress study with a total force of 1472 N.
2. Make sure “force per entity” is disabled.
3. Record the total reaction and confirm equilibrium.
4. Perform at least two mesh refinements.
5. Record stress and displacement at consistent geometric regions.
6. Export the corrected Fusion HTML report.
7. Repeat the study for at least three bracket finalists.
8. Enter the results in the bracket validation checklist.
9. Replace all report placeholders for project code and supervisor.
10. Obtain supervisor approval for the selected marine rules and material-property sources.

### 5.3 Padeye validation

The padeye campaign should validate the baseline and at least three finalists. It should examine pin bearing, net-section stress, shear-out, lug-root stress, gusset stress, weld transfer, and support-plate deformation. A later nonlinear model should include pin contact and realistic support compliance.

### 5.4 Stabilizer validation

The stabilizer campaign should validate the root, spars, ribs, skin, insert, and tip displacement. The pressure bands must sum to 11,808 N. A later hydrodynamic analysis should calculate the pressure distribution for defined vessel speed, motion, angle, and sea condition.

### 5.5 Software development

Future work should:

- add adaptive or constraint-dominating penalties;
- add sensitivity and uncertainty analysis;
- compare Nelder-Mead with another bounded derivative-free method;
- add discrete manufacturing variables;
- record software version and commit identifier in every run;
- implement the documented Gmsh and CalculiX contract;
- calibrate analytical models against FEA;
- preserve boundary roles through a solver-independent representation; and
- add physical test records to the validation packages.

# References

1. I. H. Abbott, A. E. von Doenhoff, and L. S. Stivers, Jr., “Summary of Airfoil Data,” NACA Report 824, National Advisory Committee for Aeronautics, 1945. Available: https://ntrs.nasa.gov/citations/19930090976

2. American Bureau of Shipping, *Guidance Notes on Fracture Analysis for Marine and Offshore Structures*, 2022. Available: https://ww2.eagle.org/content/dam/eagle/rules-and-guides/current/design_and_analysis/329_fracture_analysis_2022/fracture-analysis-gn-feb22.pdf

3. American Bureau of Shipping, *Guidance Notes on Nonlinear Finite Element Analysis of Marine and Offshore Structures*, 2021. Available: https://ww2.eagle.org/content/dam/eagle/rules-and-guides/current/design_and_analysis/316_gnnlfea_2021/nlfea-gn-jan21.pdf

4. ASME, *V&V 10-2019 (R2025): Standard for Verification and Validation in Computational Solid Mechanics*, American Society of Mechanical Engineers, 2019, reaffirmed 2025. Available: https://www.asme.org/codes-standards/find-codes-standards/standard-for-verification-and-validation-in-computational-solid-mechanics

5. Autodesk, “Component.getPhysicalProperties Method,” *Fusion API Reference*. Available: https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Component_getPhysicalProperties.htm

6. Autodesk, “Creating a Script or Add-In,” *Fusion API User’s Manual*. Available: https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-9701BBA7-EC0E-4016-A9C8-964AA4838954

7. Autodesk, “ExportManager.execute Method,” *Fusion API Reference*. Available: https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExportManager_execute.htm

8. Autodesk, “Mesh Convergence,” *Fusion Simulation Help*. Available: https://help.autodesk.com/cloudhelp/ENU/Fusion-Simulate/files/SIM-MESH-CONVERGENCE.htm

9. Autodesk, “Reaction Results,” *Fusion Simulation Help*. Available: https://help.autodesk.com/cloudhelp/ENU/Fusion-Simulate/files/SIM-REACTION-FORCE-VIEW-CONCEPT.htm

10. Autodesk, “Set Up a Static Stress Analysis,” *Fusion Simulation Help*. Available: https://help.autodesk.com/view/fusion360/ENU/?guid=SIM-SSA

11. Autodesk, “Static Stress Study,” *Fusion Simulation Help*. Available: https://help.autodesk.com/cloudhelp/ENU/Fusion-Simulate/files/SIM-STATIC-STRESS-ANALYSIS.htm

12. DNV, *DNV-ST-N001: Marine Operations and Marine Warranty*, edition 2023-12, 2023. Available: https://www.dnv.com/energy/standards-guidelines/dnv-st-n001-marine-operations-and-marine-warranty/

13. T. Gentils, L. Wang, and A. Kolios, “Integrated Structural Optimisation of Offshore Wind Turbine Support Structures Based on Finite Element Analysis and Genetic Algorithm,” *Applied Energy*, vol. 199, pp. 187–204, 2017. doi: 10.1016/j.apenergy.2017.05.009.

14. T. G. Kolda, R. M. Lewis, and V. Torczon, “Optimization by Direct Search: New Perspectives on Some Classical and Modern Methods,” *SIAM Review*, vol. 45, no. 3, pp. 385–482, 2003. doi: 10.1137/S003614450242889.

15. J. C. Lagarias, J. A. Reeds, M. H. Wright, and P. E. Wright, “Convergence Properties of the Nelder-Mead Simplex Method in Low Dimensions,” *SIAM Journal on Optimization*, vol. 9, no. 1, pp. 112–147, 1998. doi: 10.1137/S1052623496303470.

16. M. Li, C. Lin, W. Chen, Y. Liu, S. Gao, and Q. Zou, “XVoxel-Based Parametric Design Optimization of Feature Models,” *Computer-Aided Design*, vol. 160, art. 103528, 2023. doi: 10.1016/j.cad.2023.103528.

17. Lloyd’s Register, *LR-CO-001 Code for Lifting Appliances in a Marine Environment*, July 2026. Available: https://www.lr.org/en/knowledge/lloyds-register-rules/code-for-lifting-appliances-in-a-marine-environment/

18. Z. C. Liu, B. Zhou, and S. K. Tan, “Finite Element Analysis and Structure Optimum Design of Lifting Padeye,” *Advanced Materials Research*, vol. 658, pp. 399–403, 2013. doi: 10.4028/www.scientific.net/AMR.658.399.

19. M. D. McKay, R. J. Beckman, and W. J. Conover, “A Comparison of Three Methods for Selecting Values of Input Variables in the Analysis of Output from a Computer Code,” *Technometrics*, vol. 21, no. 2, pp. 239–245, 1979. doi: 10.1080/00401706.1979.10489755.

20. J. A. Nelder and R. Mead, “A Simplex Method for Function Minimization,” *The Computer Journal*, vol. 7, no. 4, pp. 308–313, 1965. doi: 10.1093/comjnl/7.4.308.

21. D. C. Nolan, C. M. Tierney, C. G. Armstrong, and T. T. Robinson, “Defining Simulation Intent,” *Computer-Aided Design*, vol. 59, pp. 50–63, 2015. doi: 10.1016/j.cad.2014.08.030.

22. NASA, *NASA-STD-7009B: Standard for Models and Simulations*, National Aeronautics and Space Administration, 2024. Available: https://standards.nasa.gov/standard/nasa/nasa-std-7009

23. H.-S. Park and X.-P. Dang, “Structural Optimization Based on CAD-CAE Integration and Metamodeling Techniques,” *Computer-Aided Design*, vol. 42, no. 10, pp. 889–902, 2010. doi: 10.1016/j.cad.2010.06.003.

24. B. Peherstorfer, K. Willcox, and M. Gunzburger, “Survey of Multifidelity Methods in Uncertainty Propagation, Inference, and Optimization,” *SIAM Review*, vol. 60, no. 3, pp. 550–591, 2018. doi: 10.1137/16M1082469.

25. N. L. Pedersen, “Stress Concentration and Optimal Design of Pinned Connections,” *The Journal of Strain Analysis for Engineering Design*, vol. 54, no. 2, pp. 95–104, 2019. doi: 10.1177/0309324719842766.

26. A.-K. Soh and C.-K. Soh, “Design and Analysis of Offshore Lifting Padeyes,” *Journal of Constructional Steel Research*, vol. 14, no. 3, pp. 167–180, 1989. doi: 10.1016/0143-974X(89)90071-0.

27. Z. Wang, S. K. Mantey, and X. Zhang, “A Numerical Tool for Efficient Analysis and Optimization of Offshore Wind Turbine Jacket Substructure Considering Realistic Boundary and Loading Conditions,” *Marine Structures*, vol. 95, art. 103605, 2024. doi: 10.1016/j.marstruc.2024.103605.

28. S. Zheng, C. Li, and Y. Xiao, “Efficient Optimization Design Method of Jacket Structures for Offshore Wind Turbines,” *Marine Structures*, vol. 89, art. 103372, 2023. doi: 10.1016/j.marstruc.2023.103372.
