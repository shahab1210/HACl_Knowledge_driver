---
id: FAULT-008
title: Low Pressure
category: hydraulic
equipment: pump
severity: medium
sensors:
  - pressure
  - current
  - vibration
---

# Low Pressure

## Description
A low-pressure condition in an industrial pumping system occurs when the static or dynamic fluid discharge pressure falls below the acceptable operating design envelope. In continuous-process networks, insufficient pressure disrupts downstream delivery, starves cooling jackets or lubrication circuits, causes improper atomization or mixing in chemical reactors, and indicates hydraulic inefficiencies, line leakage, or mechanical deterioration of the pump impeller and casing wear rings.

## Typical Symptoms
- Manometer, gauge, or inline pressure transmitter readings consistently below normal process setpoint.
- Insufficient flow rate or delivery failure at downstream discharge terminals.
- Fluctuating or lagging response to downstream process demand increases.
- Potential high-speed rotation or cavitation in centrifugal stages if operating excessively far right on the pump head curve.
- Accumulation of liquid or visible leakage along pipeline joints, flanges, or valve packings.

## Possible Causes
- Downstream piping breach, rupture, open drain valve, or major flange gasket leak.
- Severely worn impeller vanes, eroded volute cutwater, or excessive clearance between impeller and wear rings.
- Internal fluid recirculation or bypass valve stuck open.
- Inadequate pump operational speed (VFD underspeed, belt slip, or low supply frequency).
- Upstream supply restriction or partially clogged suction strainer limiting available fluid mass flow.
- Entrained air, gas bubbles, or partial loss of prime causing loss of effective hydraulic density.

## Sensor Indicators

| Sensor Parameter | Observed Pattern | Diagnostic Significance | Correlation with Other Readings |
| :--- | :--- | :--- | :--- |
| **Pressure** | Steadily depressed or sudden sharp drop below operating limits | Primary direct indicator of hydraulic pressure deficiency | Central indicator defining the fault condition |
| **Current** | Decreased or higher depending on pump curve (often higher if high flow runaway; lower if starved) | Corroborating indicator distinguishing pipeline break (high flow) from suction starvation | Low pressure + high current indicates downstream pipe rupture or open valve |
| **Vibration** | Normal, or elevated if low pressure induces internal flow recirculation / cavitation | Secondary indicator for hydraulic turbulence or mechanical defect | Low pressure + high vibration indicates cavitation or internal recirculation |
| **Temperature** | Generally normal; elevated if internal liquid recirculation churns trapped fluid | Secondary thermal indicator | Can rise if pump is bypassing fluid continuously in a short loop |
| **Humidity** | Localized increase if fluid leakage or spray is escaping into ambient air | Environmental leak detection signal | High humidity in pipe trench or skid suggests active pipe rupture or leak |

## Recommended Checks
1. Inspect entire pipeline route for external leaks, blown gaskets, burst hoses, or inadvertently opened bypass/drain valves.
2. Verify suction line pressure, fluid reservoir level, and suction strainer differential pressure.
3. Compare discharge pressure and motor speed against the pump manufacturer head-capacity (H-Q) curve.
4. Check internal wear clearances: measure gap between impeller shroud and casing wear ring (replace if clearance exceeds manufacturer tolerance).
5. Inspect non-return (check) valves to ensure they are not stuck partially open or allowing reverse flow.
6. Verify calibration of inline pressure transmitters and verify impulse line tubing for clogs or air bubbles.

## Safety
- High-velocity fluid spray hazard: Pinhole leaks in pressurized lines can cause dangerous fluid injection injuries; never inspect lines with bare hands.
- Slip and environmental hazard: Leaking industrial fluids, lubricants, or chemicals create slip hazards and environmental contamination.
- Lockout/Tagout (LOTO): De-energize drive motor and isolate and tag hydraulic line valves before opening strainers or uncoupling piping.

## Related Faults
- [FAULT-006: Pump Cavitation](pump-cavitation.md)
- [FAULT-007: Pump Dry Running](pump-dry-running.md)
- [FAULT-010: Sensor Anomaly](sensor-anomaly.md)
