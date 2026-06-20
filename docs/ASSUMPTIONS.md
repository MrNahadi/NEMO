# NEMO Engineering Assumptions

## Component

The case-study component is a marine equipment mounting bracket for a small auxiliary unit such as a pump. The geometry is intentionally simple enough to parametrize with six variables and validate with a first-order hand calculation.

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
