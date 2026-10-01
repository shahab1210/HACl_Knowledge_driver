# Electric Motor Inspection Procedure & Checklist

## Purpose
This document provides a structured, safety-first checklist and procedure for inspecting industrial electric induction motors exhibiting telemetry anomalies (high temperature, elevated vibration, overcurrent, or acoustic distress).

---

## Safety Requirements & Preparation
- **Mandatory LOTO:** Always isolate main power feed at the Motor Control Center (MCC), install personal safety padlock, and apply Lockout/Tagout (LOTO) tags before removing junction covers, touching shafts, or opening fan shrouds.
- **Zero Energy Verification:** Verify absence of electrical voltage using a calibrated multimeter / voltage proximity detector at all incoming terminals (L1, L2, L3) phase-to-phase and phase-to-ground.
- **PPE Requirements:** NFPA 70E compliant arc-rated face shield and clothing (when testing electrical enclosures), safety glasses, cut-resistant gloves, steel-toed boots, and thermal gloves.
- **Stored Energy Dissipation:** Wait for rotating parts to stop completely and ensure power factor correction capacitors or VFD DC buses are completely discharged.

---

## Motor Inspection Checklist

### 1. Operational & Environmental Overview (Online / Pre-Shutdown)
- [ ] Record ambient temperature and relative humidity around motor location.
- [ ] Measure operating surface temperatures using an infrared thermal imager:
  - Stator core / frame center.
  - Drive-End (DE) bearing housing.
  - Non-Drive-End (NDE) bearing housing.
  - Conduit box and cable entries.
- [ ] Measure operating three-phase current (RMS) on L1, L2, L3 using a calibrated true-RMS clamp meter. Calculate phase current unbalance percentage:
  $$\text{Unbalance (\%)} = \frac{\text{Max Deviation from Average}}{\text{Average Current}} \times 100$$
- [ ] Check for unusual acoustic patterns (humming, grinding, clicking, or cyclical beating).
- [ ] Inspect motor cooling airflow: confirm air intake grill at fan shroud is unobstructed and discharge airflow is strong.

### 2. External Physical & Mechanical Inspection (De-energized & LOTO Applied)
- [ ] Inspect foundation and baseplate: check for cracks, structural corrosion, or loose hold-down bolts.
- [ ] Perform "Soft Foot" check: loosen hold-down bolts one by one with a dial indicator positioned at each foot; verify deflection is within tolerance (< 0.05 mm / 0.002 in).
- [ ] Inspect coupling and alignment:
  - Check flexible coupling element/spider for cracks, rubber dusting, or backlash.
  - Measure angular and radial shaft misalignment using dial indicators or laser alignment tool.
- [ ] Manually turn the motor shaft by hand (uncoupled if possible):
  - Verify smooth rotation with no binding, catching, or axial/radial play.
  - Listen for internal rubbing or bearing crunching.
- [ ] Inspect cooling fan: check fan shroud for debris, ensure cooling fan blades are intact, clean, and firmly secured to the shaft.
- [ ] Inspect cooling fins: clean accumulated grease, oil, and dust layers that restrict convective heat transfer.

### 3. Lubrication & Bearing System Check
- [ ] Inspect bearing seals (DE and NDE) for grease leakage or contamination ingress.
- [ ] Check grease relief ports: ensure purge plugs are free and hardened grease cakes are removed.
- [ ] Verify grease replenishment history: check grease type compatibility, date of last relubrication, and quantity added.
- [ ] For oil-lubricated bearings: check oil level sight glass, oil clarity, and inspect for water contamination (milky emulsion) or metal flakes.

### 4. Electrical & Terminal Junction Box Inspection
- [ ] Inspect terminal box interior for moisture, dust, carbon tracking, or signs of flashover.
- [ ] Inspect cable terminations: verify lugs are tight, no discoloration or heat scorch marks on insulation.
- [ ] Perform insulation resistance test (Megger) at 500 V / 1000 V DC:
  - Phase-to-Ground: Minimum acceptable resistance is typically $\ge 5 \text{ M}\Omega$ (clean, dry winding benchmark $> 100 \text{ M}\Omega$).
  - Phase-to-Phase (if individual phase leads are accessible).
- [ ] Measure winding resistance balance across all three phases with a micro-ohmmeter; ensure winding resistance is balanced within 1-2%.
- [ ] Check grounding conductor and ground bond resistance between motor frame and plant ground grid.

---

## Action Matrix Based on Inspection Findings

| Observed Finding | Likely Root Cause | Immediate Corrective Action |
| :--- | :--- | :--- |
| Hot bearing housing (> 85 °C) + high vibration | Lubrication breakdown, bearing wear | Purge old grease, check alignment; replace bearing if wear frequencies persist |
| Stator casing overheating + high balanced current | Mechanical overload or clogged cooling fins | Clean cooling fins and fan shroud; inspect driven pump for blockage or binding |
| Overcurrent with > 5% current unbalance | Supply voltage unbalance or winding turn fault | Measure incoming supply line voltages; test winding resistance and phase balance |
| High 1x RPM vibration on motor frame | Rotor unbalance | Clean rotor/fan; balance rotating assembly dynamically in-place |
| High axial vibration + 2x RPM peak | Shaft misalignment | Re-align motor and driven machine using precision laser alignment kit |
| Low insulation resistance (< 5 MΩ) | Moisture or chemical ingress into windings | Dry out windings using controlled heating; bake and revarnish if needed |
