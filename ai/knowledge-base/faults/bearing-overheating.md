---
id: FAULT-001
title: Bearing Overheating
category: mechanical
equipment: motor
severity: high
sensors:
  - temperature
  - vibration
  - current
---

# Bearing Overheating

## Description
Bearing overheating occurs when the operating temperature of a rolling element or sleeve bearing exceeds its designed thermal equilibrium, typically due to excessive friction, improper lubrication, mechanical overload, or misalignment. If left unaddressed, thermal degradation of bearing materials and lubricants leads to catastrophic bearing seizure, shaft damage, rotor-stator contact, and unplanned motor shutdown.

## Typical Symptoms
- Rapid or progressive rise in bearing housing or bearing cap temperature.
- Distinct metallic rubbing, whining, or squealing acoustic signatures near the bearing end bell.
- Discoloration, scorching, degradation, or liquefaction and leaking of bearing grease or oil.
- Increased rotational resistance and elevated localized heat dissipation.
- Secondary rise in motor drive-end or non-drive-end casing temperature.

## Possible Causes
- Inadequate lubrication (insufficient grease quantity, dried grease, or oil starvation).
- Over-greasing or over-lubrication causing excessive fluid friction and churning heat.
- Use of degraded, oxidized, contaminated, or incorrect lubricant viscosity grade.
- Excessive radial or axial mechanical preload from shaft misalignment or overtightened belts.
- Bearing internal clearance reduction due to thermal expansion or incorrect fit on shaft/housing.
- Contaminant ingress (dust, metal particulate, moisture) accelerating frictional heating.

## Sensor Indicators

| Sensor Parameter | Observed Pattern | Diagnostic Significance | Correlation with Other Readings |
| :--- | :--- | :--- | :--- |
| **Temperature** | Sustained high or steeply rising trend above baseline | Primary indicator of thermal stress and elevated friction at bearing point | Directly correlates with bearing housing localized thermal rise |
| **Vibration** | Elevated overall RMS vibration; emergence of high-frequency friction noise | Indicates mechanical friction, early raceway contact, or imbalance | Often accompanies temperature spikes when degradation is mechanical |
| **Current** | Moderate increase in motor current or baseline electrical load | Increased mechanical drag and friction torque reflected at motor shaft | Confirms mechanical resistance resisting rotor rotation |
| **Pressure** | Generally unaffected unless coupled pump experiences shaft binding | Secondary indicator in coupled machinery | Normal or fluctuating if hydraulic system is unloaded |
| **Humidity** | Ambient humidity unchanged; may promote corrosion if high | Environmental contributing factor | Sustained high humidity may indicate moisture wash-out of grease |

## Recommended Checks
1. Verify localized bearing housing temperature using a calibrated non-contact infrared pyrometer or contact probe against the sensor reading.
2. Inspect lubricant condition: check grease reservoir for discoloration, odor, carbonization, contamination, or hardened grease cake.
3. Check grease relief ports to ensure grease purge paths are open and the cavity is not over-pressurized.
4. Measure shaft radial and axial runout and inspect coupling alignment (angular and parallel) with dial indicators or laser alignment tools.
5. Review vibration spectrum for bearing characteristic fault frequencies (BPFO, BPFI, BSF, FTF) or high-frequency friction carpets.
6. Inspect seal integrity to ensure dust and water exclusions are functioning properly.

## Safety
- High surface temperature hazard: Exercise extreme caution near bearing housings and motor end bells; wear thermal-resistant PPE.
- Rotating machinery hazard: Do not touch shafts, couplings, or bearing caps while the machine is energized or rotating.
- De-energization: Strictly enforce Lockout/Tagout (LOTO) protocols on the motor electrical supply before opening bearing housings, cleaning grease fittings, or performing mechanical checks.

## Related Faults
- [FAULT-002: Bearing Wear](bearing-wear.md)
- [FAULT-003: Motor Overheating](motor-overheating.md)
- [FAULT-005: Excessive Motor Vibration](motor-vibration.md)
