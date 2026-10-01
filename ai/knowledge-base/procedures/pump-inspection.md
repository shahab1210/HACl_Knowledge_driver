# Centrifugal & Process Pump Inspection Procedure & Checklist

## Purpose
This document provides a structured, safety-first checklist and procedure for inspecting industrial process and centrifugal pumps displaying hydraulic, mechanical, or thermal telemetry anomalies (abnormal pressure, cavitation vibration, seal overheating, or motor overcurrent).

---

## Safety Requirements & Preparation
- **Mandatory LOTO (Electrical & Hydraulic):**
  - Electrically isolate and lock out the pump drive motor at the MCC before approaching rotating parts.
  - Hydraulically isolate the pump by closing and locking suction and discharge isolation valves.
  - Tag out all related utility lines (seal flush, cooling water, chemical injection).
- **Depressurization & Venting:**
  - Slowly open pump casing drain and vent valves to verify zero hydraulic pressure before loosening any bolts, fittings, or flange connections.
  - Collect drained process fluids in compliant chemical containment vessels.
- **Thermal & Chemical Hazard Precaution:**
  - Verify casing temperature has cooled to safe ambient handling limits (< 40 °C) before opening vents.
  - Wear chemical-resistant gloves, splash apron, face shield, and safety glasses when draining process lines.

---

## Pump Inspection Checklist

### 1. Operational & Hydraulic Check (Online / Pre-Shutdown)
- [ ] Record suction pressure, discharge pressure, and differential pressure across the pump.
- [ ] Compare measured differential head ($H = \frac{\Delta P}{\rho g}$) against the pump performance curve at current flow rate.
- [ ] Listen for characteristic cavitation acoustic noise ("pumping gravel/rocks") near suction flange and impeller eye.
- [ ] Inspect pump mechanical seal gland / stuffing box:
  - Check for liquid leakage drops per minute (standard mechanical seal should have zero visible drop leakage).
  - Measure seal gland surface temperature using an infrared pyrometer.
- [ ] Check seal flush / barrier fluid pressure, temperature, and circulating flow.
- [ ] Inspect suction and discharge piping for visible pipe vibration, water hammer shocks, or strained hangers.

### 2. Suction & Inlet Line Inspection (De-energized & Isolated)
- [ ] Check liquid supply source: verify actual vessel/tank liquid level via sight gauge vs. level transmitter.
- [ ] Inspect suction line strainer: remove basket, inspect for clogging, debris, rags, or scale; clean thoroughly.
- [ ] Verify that suction line isolation valve is 100% fully open and valve disc is not detached from stem.
- [ ] Inspect suction piping geometry: ensure suction pipe has at least 5 to 10 pipe diameters of straight run prior to the suction nozzle, with no high-point vapor traps.
- [ ] Check for air ingress points: inspect suction flange gaskets, valve packing, and instrumentation tappings for vacuum leaks.

### 3. Mechanical & Rotating Assembly Inspection (LOTO Applied)
- [ ] Rotate pump shaft manually by hand:
  - Shaft must turn freely and smoothly without tight spots, binding, or rubbing.
  - Ensure zero axial binding against volute cutwater or wear rings.
- [ ] Inspect bearing housing and lubrication:
  - Check constant-level oiler level and cleanliness; check for water emulsion or metal sediment.
  - Check bearing temperatures and inspect oil seals/isolators for oil leakage.
- [ ] Check shaft radial and axial runout using a dial indicator mounted on the pump casing.
- [ ] Inspect pump-to-motor coupling:
  - Check flexible element wear, bolt torques, and check coupling alignment (angular and offset).

### 4. Internal Casing & Impeller Inspection (Major Teardown / Maintenance)
- [ ] Inspect impeller vanes:
  - Check suction vane leading edges for classic cavitation pitting, honeycombing, or spongy metal loss.
  - Check for foreign object damage, bent vanes, or corrosion erosion.
- [ ] Measure wear ring clearances:
  - Measure diametrical clearance between impeller wear ring and casing wear ring using feeler gauges.
  - Replace wear rings if clearance exceeds 2x original manufacturer design specification.
- [ ] Inspect mechanical seal components:
  - Inspect seal faces (silicon carbide, tungsten carbide, carbon) for thermal cracking (heat checking), blistering, or deep scoring.
  - Inspect secondary elastomer O-rings for thermal hardening, embrittlement, or chemical swelling.
- [ ] Inspect casing volute and cutwater: check for abrasive erosion, cracks, or erosion groves.

---

## Action Matrix Based on Inspection Findings

| Observed Finding | Likely Root Cause | Immediate Corrective Action |
| :--- | :--- | :--- |
| Popping noise + erratic pressure + high vibration | Pump Cavitation (insufficient NPSHa) | Clean suction strainer, raise suction level, open throttled suction valves, lower fluid temp |
| Zero pressure + very low motor current | Pump Dry Running or lost prime | Immediately shut down pump, inspect supply reservoir, vent casing, and re-prime completely |
| High discharge pressure + motor straining | Downstream blockage or closed valve | Re-align discharge valve lineup, inspect downstream filters/strainers for clogs |
| Low discharge pressure + normal current | Excessive wear ring clearance or worn impeller | Measure wear ring clearance; replace worn rings and impeller as necessary |
| Seal gland overheating (> 80 °C) | Dry running seal or plugged flush line | Clean seal flush tubing and orifice; ensure adequate barrier fluid cooling |
| Heavy leakage from mechanical seal gland | Blistered, cracked, or worn seal faces | Replace mechanical seal cartridge; inspect shaft sleeve for fretting |
