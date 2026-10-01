---
id: FAULT-006
title: Pump Cavitation
category: hydraulic
equipment: pump
severity: critical
sensors:
  - pressure
  - vibration
  - current
---

# Pump Cavitation

## Description
Pump cavitation occurs when the local static pressure inside a centrifugal or positive displacement pump drops below the vapor pressure of the pumped liquid, causing vapor bubbles (cavities) to form in the fluid stream. When these vapor bubbles travel into regions of higher pressure within the impeller vanes or volute casing, they violently implode. These implosions generate localized micro-jets with shock pressures exceeding thousands of atmospheres, eroding metal surfaces (pitting), causing severe structural vibration, reducing pump head and flow capacity, and ultimately destroying impellers, mechanical seals, and bearings.

## Typical Symptoms
- Characteristic loud rattling, popping, or crackling noise often described as "pumping gravel, marbles, or rocks."
- High-frequency, random, broad-band vibration concentrated in the pump casing and bearing housings.
- Severe fluctuations and degradation in pump discharge pressure and delivered flow rate.
- Premature failure of mechanical seals and rapid deterioration of pump shaft bearings.
- Severe pitting, sponginess, and metal erosion on impeller vane suction surfaces and shroud walls upon teardown.

## Possible Causes
- Inadequate Net Positive Suction Head Available (NPSHa is less than NPSHr required by pump manufacturer).
- Suction line restrictions: Clogged suction strainer, partially closed suction valve, or obstructed piping.
- Suction lift too high or liquid source level dropping below minimum submerged intake level.
- Elevated fluid temperature causing an increase in fluid vapor pressure without corresponding pressure elevation.
- Fluid velocity too high through undersized suction piping or sharp elbows placed immediately adjacent to the pump suction flange.
- Operating the pump too far out on the performance curve (excessive flow rate) or near shut-off head (internal recirculation cavitation).

## Sensor Indicators

| Sensor Parameter | Observed Pattern | Diagnostic Significance | Correlation with Other Readings |
| :--- | :--- | :--- | :--- |
| **Pressure** | Fluctuating, erratic, or depressed discharge pressure; abnormally low suction pressure | Direct hydraulic indicator of vapor pocket formation and loss of hydraulic coupling | Erratic pressure directly correlates with erratic vibration bursts |
| **Vibration** | Sharp elevation in high-frequency broadband vibration (often > 2 kHz to ultrasonic) | Caused by energy shockwaves from bubble implosions against casing walls | High vibration coincides with discharge pressure drops and instability |
| **Current** | Unstable, erratic, or depressed motor current fluctuations | Density fluctuations from liquid/vapor mix reduce and destabilize load on motor | Lower or swinging current distinguishes cavitation from mechanical binding |
| **Temperature** | Mild to moderate rise in pump casing and seal flush temperature | Secondary result of fluid recirculating or friction in poorly lubricated seals | Can rise if internal recirculation cavitation is occurring |
| **Humidity** | Ambient; may rise if mechanical seal leaks vaporized fluid into surroundings | Secondary environmental indicator | Vapor release from damaged seals increases localized relative humidity |

## Recommended Checks
1. Calculate and compare NPSHa against manufacturer NPSHr curve for the actual operating flow rate.
2. Inspect suction line: Check suction strainer for debris, ensure suction isolation valves are 100% fully open, and verify pipe run straightness.
3. Check fluid temperature at suction; verify if process liquid has experienced unexpected thermal rise altering its vapor point.
4. Review vibration spectral data: Look for characteristic broadband "cavitation floor" noise across high frequencies rather than clean discrete 1x/2x peaks.
5. Check pump discharge pressure and flow meter readings against the published head-capacity (H-Q) pump curve.
6. Inspect mechanical seal faces and gland flush lines for vapor locking, leakage, or dry running symptoms.

## Safety
- Hydraulic pressure surge hazard: Collapsing vapor pockets can induce violent pressure spikes and water hammer, threatening pipe integrity.
- Chemical/Fluid spray: Leaking mechanical seals or blown gaskets caused by cavitation vibration can spray hazardous or hot fluids.
- Isolation and depressurization: Verify zero mechanical, hydraulic, and electrical energy via LOTO before opening pump strainers, vents, or casing flanges.

## Related Faults
- [FAULT-007: Pump Dry Running](pump-dry-running.md)
- [FAULT-008: Low Pressure](low-pressure.md)
- [FAULT-005: Excessive Motor Vibration](motor-vibration.md)
