# NEMO Engineering Assumptions

## Component

The case-study component is a marine equipment mounting bracket for a small auxiliary unit such as a pump. The geometry is intentionally simple enough to parametrize with six variables and validate with a first-order hand calculation.

NEMO now also includes a 500 kg-class gusseted lifting padeye and a fixed-envelope
small-craft stabilizer. Their dimensions, materials, loads, and constraints are
defined in the packaged part manifests. The stabilizer optimization changes
internal structure only; it does not claim hydrodynamic shape optimization.

## Material

- Material: Aluminum 6061-T6
- Density: 2700 kg/m^3
- Yield strength: 276 MPa
- Elastic modulus: 68.9 GPa

These values are representative project defaults. Before final submission, cite the source used for final material properties.

## Load Case

- Equipment mass: 50 kg
- Gravity: 9.81 m/s^2
- Dynamic amplification factor: 3
- Design load: 1471.5 N

The load is applied vertically at the equipment mounting point. The baseplate bolt-hole/base faces are treated as fixed in the Fusion FEA template.

## Constraints

- Minimum factor of safety: 2.5
- Maximum equipment-point deflection: 0.5 mm

## Analytical Fallback Model

The fallback model estimates:

- mass from baseplate, bolt-hole subtraction, two triangular ribs, and a small fillet-volume approximation,
- max stress from a cantilever bending moment and an effective section modulus,
- deflection from a cantilever beam approximation and an effective second moment of area.

This model is for optimizer guidance only. Final claims must be validated in Fusion FEA.

The padeye and stabilizer analytical models have the same screening role. They
are deliberately conservative first-order section models and are not substitutes
for the documented manual Fusion validation.

## Propeller Boundary

A propeller generator and optimizer remain future work. A defensible propeller
study must provide thrust, torque, efficiency, cavitation, centrifugal loading,
and hydrodynamic pressure through a blade-element or CFD model before varying
pitch, chord, skew, or rake.
