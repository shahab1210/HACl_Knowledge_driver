---
id: FAULT-005
title: Excessive Motor Vibration
category: mechanical
equipment: motor
severity: high
sensors:
  - vibration
  - temperature
  - current
---

# Excessive Motor Vibration

## Description
Excessive motor vibration refers to oscillatory motion or kinetic shocks within the motor frame and rotating assembly that exceed acceptable ISO 10816 / ISO 20816 vibration severity standards. Unchecked vibration induces cyclic mechanical fatigue in motor components, accelerates bearing deterioration, loosens foundation mounting bolts, degrades mechanical couplings, and can cause catastrophic rotor-to-stator air-gap rubbing.

## Typical Symptoms
- Palpable shaking, trembling, or rocking motion of the motor frame, baseplate, or coupled piping.
- Pronounced acoustic humming, buzzing, rattling, or beat frequencies that pulse with rotational frequency.
- Loose, backed-out, or fractured hold-down bolts, foundation grouting cracks, or distorted shim packs.
- Rapidly accelerating wear patterns on flexible coupling inserts, belts, or drive pulleys.
- Premature failure of rolling element bearings at intervals far below expected L10 design life.

## Possible Causes
- Rotor unbalance caused by uneven material deposition, loss of balance weights, or asymmetric rotor casting.
- Shaft angular or parallel misalignment between motor and driven machinery.
- Soft foot condition (uneven foot contact with baseplate creating frame distortion).
- Mechanical looseness (loose foundation bolts, cracked baseframe, or worn bearing housing fits).
- Bent or eccentric motor shaft resulting from handling damage or thermal bow.
- Electrical unbalance: Stator eccentricity, broken rotor bars, or asymmetric air gaps generating 2x line frequency magnetic forces.
- Structural resonance: Operating speed coinciding with a natural resonant frequency of the motor support structure.

## Sensor Indicators

| Sensor Parameter | Observed Pattern | Diagnostic Significance | Correlation with Other Readings |
| :--- | :--- | :--- | :--- |
| **Vibration** | Overall RMS velocity and peak acceleration consistently above operational thresholds | Primary and direct indicator of dynamic mechanical and structural instability | Dominant diagnostic variable across multiple axes |
| **Temperature** | Elevated bearing housing and frame temperatures; progressive rise | Result of secondary friction and cyclic energy dissipation in bearings and joints | Follows vibration rise when misalignment or bearing friction is involved |
| **Current** | Periodic amplitude modulation or sidebands around supply line frequency | Electrical or dynamic eccentricity reflects cyclic air-gap modulation into stator current | Current spectral sidebands confirm rotor bar or air-gap defects |
| **Pressure** | Oscillations or pressure pulsations in fluid systems coupled to vibrating motor | Hydraulic transmission of rotational shaking | Correlates with fluid line pulsation or impeller blade-pass frequencies |
| **Humidity** | Neutral; does not directly cause vibration | Environmental baseline parameter | High moisture combined with vibration accelerates structural corrosion |

## Recommended Checks
1. Perform tri-axial vibration spectrum analysis (horizontal, vertical, axial):
   - Dominant 1x RPM suggests unbalance or bent shaft.
   - Dominant 2x RPM with high axial component indicates angular or offset misalignment.
   - Harmonics (3x, 4x, 5x RPM) with directional spikes indicate mechanical looseness.
   - 2x electrical line frequency spikes (100 Hz or 120 Hz) indicate dynamic/static air-gap eccentricity.
2. Check for soft foot: Loosen one hold-down bolt at a time while monitoring deflection with a dial indicator; max allowable lift is typically < 0.05 mm.
3. Check shaft alignment using a precision dual-laser alignment system across cold and thermal-growth conditions.
4. Inspect foundation integrity, structural welds, grouting, and torque on all base bolts.
5. Inspect flexible coupling element for degradation, backlash, or elastomeric shearing.

## Safety
- Mechanical projectile hazard: Structural components, balance weights, or sheared coupling bolts can detach at high operational speeds.
- Hand entrapment: Never apply hand contact or hand-held measurement devices to unguarded rotating shafts or pulleys.
- Lockout/Tagout (LOTO): Machine must be de-energized, verified zero-energy, and locked out before performing bolt torque checks, alignment corrections, or coupling inspections.

## Related Faults
- [FAULT-002: Bearing Wear](bearing-wear.md)
- [FAULT-001: Bearing Overheating](bearing-overheating.md)
- [FAULT-004: Motor Overcurrent](motor-overcurrent.md)
