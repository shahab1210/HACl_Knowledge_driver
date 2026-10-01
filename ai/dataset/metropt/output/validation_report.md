# P22: Real Industrial Dataset Validation Report (MetroPT-3)

**Project:** P_311 — Knowledge-Driven IoT Fault Diagnosis Assistant  
**Dataset:** MetroPT-3 (Air Production Unit / Compressor Telemetry)  
**Authors / Origin:** Metro do Porto & INESC TEC (Davari, Veloso, Ribeiro, Gama)  
**Literature Citations:**
- [1] Davari et al., *"A data-driven predictive maintenance framework for air production units in metro trains"*, IEEE DSAA 2021 (DOI: 10.1109/DSAA53316.2021.9564181)
- [2] Veloso et al., *"MetroPT: A real-world dataset for predictive maintenance of railway components"*, Scientific Data 2022 (DOI: 10.1038/s41597-022-01877-3)
- [3] UCI Machine Learning Repository: MetroPT Dataset (DOI: 10.24432/C5CH87)

---

## 1. Executive Summary & Purpose

The purpose of Phase 22 (P22) is to conduct a **rigorous, reproducible offline validation study** using the real-world industrial **MetroPT-3** dataset to validate:
1. Industrial physical signal behaviors: **Oil Temperature**, **Motor Current**, and **Pneumatic Pressures** (TP2, TP3, Reservoirs, DV_pressure).
2. Machine operating-state transitions and duty cycle dynamics under normal vs failure conditions.
3. Anomaly detection efficacy against verified, real-world maintenance failure events (air leaks).

> [!IMPORTANT]
> **Strict Scope & Dataset Isolation Notice:**
> - MetroPT-3 is processed via a dedicated **offline validation pipeline**.
> - The live operational pipeline (`Python Sensor Simulator → MQTT → Spring Boot → PostgreSQL → React / Grafana`) remains **100% UNCHANGED**.
> - MetroPT-3 data is **NOT** inserted into the live `sensor_readings` PostgreSQL table.
> - MetroPT-3 contains **NO humidity** and **NO vibration** signals; this validator explicitly prevents conflating MetroPT-3 with the ESP32 simulator schema.

---

## 2. Dataset Metadata & Quality Audit

The dataset consists of high-frequency downsampled telemetry from an operational Metro do Porto urban rail train's Air Production Unit (APU) screw compressor:

| Property | Value |
| :--- | :--- |
| **Total Observations** | `1,516,948` rows |
| **Total Features** | `16` columns |
| **Start Timestamp** | `2020-02-01 00:00:00` |
| **End Timestamp** | `2020-09-01 03:59:50` |
| **Observation Span** | `213.17` days (Feb 2020 – Sep 2020, 7 full months) |
| **Nominal Sampling Interval** | `10.0` seconds |
| **Observed Median Interval** | `10.0` seconds |
| **Observed Mean Interval** | `12.14` seconds |
| **Null Values Count** | **`0`** (0.00% missing values across all columns) |
| **Duplicate Timestamps** | **`0`** |
| **Memory Footprint** | `185.17` MB |
| **Data Cleanliness Audit** | **`PASSED (Zero nulls, zero duplicates)`** |

### Schema & Dataset Isolation Validation
- **Schema Integrity:** **`PASSED`**
- **Dataset Isolation Check:** **`CONFIRMED`** (Zero humidity or vibration signals present).
- **Physical Boundary Verification:** All continuous signals (`Oil_temperature`, `Motor_current`, `TP2`, `TP3`, `H1`, `DV_pressure`, `Reservoirs`) operate strictly within physical thermodynamic limits.

---

## 3. Signal Analysis & Statistical Distributions

### 3.1 Continuous Physical Signals

The table below presents the empirical statistical distribution across the full 1.51M observations:

| Signal | Mean | Std | Min | Median (p50) | p75 (Q3) | p95 | Max | IQR | Unit |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Oil_temperature** | `62.644` | `6.516` | `15.4` | `62.7` | `67.25` | `73.525` | `89.05` | `9.475` | °C |
| **Motor_current** | `2.05` | `2.302` | `0.02` | `0.045` | `3.808` | `5.987` | `9.295` | `3.768` | A |
| **TP2 (Compressor Outlet)** | `1.368` | `3.251` | `-0.032` | `-0.012` | `-0.01` | `9.59` | `10.676` | `0.004` | bar |
| **TP3 (Pneumatic Panel)** | `8.985` | `0.639` | `0.73` | `8.96` | `9.492` | `9.98` | `10.302` | `1.0` | bar |
| **H1 (Separator Drop)** | `7.568` | `3.333` | `-0.036` | `8.784` | `9.374` | `9.916` | `10.288` | `1.12` | bar |
| **DV_pressure (Drying Towers)**| `0.056` | `0.382` | `-0.032` | `-0.02` | `-0.018` | `-0.008` | `9.844` | `0.004` | bar |
| **Reservoirs** | `8.985` | `0.638` | `0.712` | `8.96` | `9.492` | `9.978` | `10.3` | `0.998` | bar |

### 3.2 Machine State & Digital Control Signals

| Signal | Description | Type | Duty Cycle / Active % |
| :--- | :--- | :---: | :---: |
| **COMP** | Air intake valve (1.0 = intake closed / offloaded; 0.0 = open / compressing) | Binary | `83.7%` active (closed) |
| **DV_eletric** | Outlet valve electrical control (1.0 = open under load; 0.0 = closed) | Binary | `16.06%` active (open) |
| **Towers** | Desiccant drying tower selection (0 = Tower 1, 1 = Tower 2) | Binary | `91.98%` Tower 2 |
| **MPG** | Pressure governor switch (triggers when APU pressure < 8.2 bar) | Binary | `83.27%` active |
| **LPS** | Low Pressure Safety switch (critical warning: pressure < 7.0 bar) | Binary | `0.34%` active (`5,188` events) |
| **Pressure_switch**| Tower discharge detection switch | Binary | `99.14%` active |
| **Oil_level** | Low oil level indicator (1.0 = low oil level) | Binary | `90.42%` active |
| **Caudal_impulses**| Flow meter pulse counter (APU to reservoirs) | Pulse | Integer counter |

---

## 4. Operating-State Analysis

Based on the physical compressor operation documented in railway engineering literature, observations are classified into three operational regimes:

1. **Standby / Off** (`Motor_current < 1.0 A`): APU motor is de-energized or idle (~0.04 A).
2. **Offloaded / Idling** (`1.0 A <= Motor_current < 5.5 A`): Motor spins with intake valve closed (`COMP == 1.0`), preventing air compression (~3.8 A).
3. **Under Load / Compressing** (`Motor_current >= 5.5 A`): Motor is actively driving the screw compressor with intake open (`COMP == 0.0`), discharging pressurized air to reservoir (~6.8 A).

| Operating State | Total Observations | Time Distribution (%) | Cumulative Duration | Mean Oil Temp (°C) | Mean Current (A) | Mean Reservoir Press (bar) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Standby** | `829,000` | `54.65%` | `2302.8` hrs | `59.3°C` | `0.04 A` | `8.69 bar` |
| **Offloaded** | `486,325` | `32.06%` | `1350.9` hrs | `66.88°C` | `3.88 A` | `9.48 bar` |
| **Under Load**| `201,623` | `13.29%` | `560.1` hrs | `66.19°C` | `5.89 A` | `9.03 bar` |

---

## 5. Anomaly Detection & Ground Truth Failure Cross-Validation

### 5.1 Ground Truth Air Leak Failure Events Validation

The published literature records four major real-world pneumatic air leak events that caused intense compressor degradation. The table below demonstrates how our analytical metrics perform during those exact failure intervals versus the baseline:

| Event ID | Period | Failure Description | Observations | UnderLoad Duty Cycle | Baseline Ratio | Mean Temp | Max Temp | LPS Trips (<7 bar) | Anomaly Detected? |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **EV-01** | 2020-04-18 to 2020-04-18 | Air Leak / Excessive Workload | 8,663 | **83.6%** | **6.29x** | 74.13°C | 78.17°C | 0 | **YES (DETECTED)** |
| **EV-02** | 2020-05-29 to 2020-05-30 | Air Leak / Compressor Stress | 2,360 | **79.75%** | **6.0x** | 75.87°C | 76.65°C | 0 | **YES (DETECTED)** |
| **EV-03** | 2020-06-05 to 2020-06-07 | Severe Air Leak / Low Pressure Shutdown | 17,315 | **62.11%** | **4.67x** | 75.52°C | 78.03°C | 198 | **YES (DETECTED)** |
| **EV-04** | 2020-07-15 to 2020-07-15 | Air Leak / Thermal Overheating | 1,622 | **52.53%** | **3.95x** | 83.91°C | 89.05°C | 530 | **YES (DETECTED)** |

### Key Physical Failure Insights:
1. **Severe Duty Cycle Elongation:** Under normal train operations, the APU compressor is under load only **13.29%** of the time. During the EV-01 and EV-02 air leak events, the duty cycle skyrocketed to **83.6%** and **79.7%** (a **6.3x** increase), because continuous pneumatic leakage prevented the reservoir from maintaining pressure.
2. **Thermal Stress & Overheating:** The sustained compression forced oil temperatures from the normal 58–63°C range up to **74–84°C** (peaking at 89.05°C during EV-04).
3. **Safety Switch Tripping (LPS):** In severe stages (EV-03, EV-04), the compressor could no longer maintain the minimum safe pneumatic threshold of 7.0 bar, resulting in **198** and **530** Low Pressure Safety trips.

### 5.2 Statistical Anomaly Summary (IQR & Z-Score)

| Signal | IQR Lower Bound | IQR Upper Bound | IQR Outliers Count (%) | Z-Score (>3σ) Count (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Oil_temperature** | `43.562°C` | `81.463°C` | `5,194 (0.342%)` | `4,084 (0.269%)` |
| **Motor_current** | `-5.611 A` | `9.459 A` | `0 (0.0%)` | `7 (0.0%)` |
| **Reservoirs** | `6.997 bar` | `10.989 bar` | `4,526 (0.298%)` | `4,657 (0.307%)` |

---

## 6. Generated Visualizations

The following 6 high-resolution analytical figures have been generated in `output/plots/`:

1. **`plots/oil_temperature_timeline.png`**: Seven-month timeline of compressor oil temperature, annotating warning thresholds (80°C) and shading ground truth failure events.
2. **`plots/motor_current_timeline.png`**: Longitudinal motor current profile with an expanded zoom-in view of the EV-01 air leak failure window.
3. **`plots/pressure_signals_timeline.png`**: Comparative multi-trace pneumatic pressure curves (`TP2`, `TP3`, `Reservoirs`, `DV_pressure`) with governor cut-in (8.2 bar) and safety cutoff (7.0 bar).
4. **`plots/current_vs_temperature.png`**: Bivariate hexbin density of Motor Current versus Oil Temperature, revealing the three distinct operational regimes.
5. **`plots/operating_state_transitions.png`**: Overall operational regime distribution pie chart accompanied by a 24-hour step-function timeline showing typical duty cycle transitions.
6. **`plots/anomaly_detection_overlay.png`**: Daily UnderLoad duty cycle trend with overlay of published ground truth air leak failure events.

---

## 7. Direct Relevance to P_311 Fault Diagnosis Assistant

The empirical findings from MetroPT-3 provide real-world industrial validation for the diagnostic models and alert rules implemented in P_311:

1. **Temperature Dynamics:** Industrial compressors exhibit thermal lag; continuous electrical loading directly drives progressive oil temperature rise. The 80°C threshold implemented in P20 Alerts is firmly grounded in real compressor behavior (where normal is ~60°C and severe air leaks reach 75–85°C).
2. **Current Signatures:** Motor current cleanly delineates machine health and operating states (~0A Standby, ~4A Idling, ~7A Under Load, ~9A Startup). Current alone is insufficient to diagnose an air leak; current combined with prolonged duty cycle confirms pneumatic failure.
3. **Pneumatic Pressures:** When an air leak develops, pressure drop across the reservoir forces the pressure governor (`MPG`) to repeatedly command compressor operation, preventing the compressor from entering idle or standby.
4. **Knowledge-Driven Diagnosis Connection:** In P12 / P14 AI diagnosis, when high temperature and prolonged duty cycle are observed, RAG retrieval matches compressor mechanical leakage and thermal degradation fault modes.

---

## 8. Architectural Boundaries & System Isolation

```text
┌────────────────────────────────────────────────────────┐
│               LIVE OPERATIONAL PIPELINE                │
│ (Unchanged, real-time ESP32 simulation & diagnosis)    │
│                                                        │
│  Python Sensor Simulator                               │
│            ↓                                           │
│      MQTT Mosquitto (1883)                             │
│            ↓                                           │
│    Spring Boot Backend (8080)                          │
│            ↓                                           │
│   PostgreSQL sensor_readings & diagnosis_records       │
│            ↓                                           │
│   React Dashboard (5173) & Grafana (3000)              │
└────────────────────────────────────────────────────────┘

                           ≠ (COMPLETELY ISOLATED)

┌────────────────────────────────────────────────────────┐
│             OFFLINE P22 VALIDATION PIPELINE            │
│ (Reproducible industrial benchmark using MetroPT-3)   │
│                                                        │
│  MetroPT-3 CSV (208 MB, 1.51M rows)                    │
│            ↓                                           │
│  MetroPTLoader (Cleanliness audit: 0 nulls, 0 dups)    │
│            ↓                                           │
│  MetroPTValidator (No humidity, no vibration check)    │
│            ↓                                           │
│  MetroPTFeatureExtractor (Continuous & State stats)    │
│            ↓                                           │
│  MetroPTAnalyzer (Operating states & Ground Truth)     │
│            ↓                                           │
│  MetroPTReportGenerator (MD report, JSON, 6 plots)     │
└────────────────────────────────────────────────────────┘
```

---

## 9. Conclusion

Phase 22 successfully completes the offline industrial validation of P_311 using real MetroPT-3 APU compressor data:
- **1,516,948 real observations** audited and validated without data loss.
- **100% detection of ground truth failure events** achieved through explainable duty cycle and thermodynamic stress metrics.
- **Strict architectural isolation preserved**: live MQTT, PostgreSQL, Spring Boot, React, Grafana, and AI/RAG pipelines remain completely untouched and fully functional.
