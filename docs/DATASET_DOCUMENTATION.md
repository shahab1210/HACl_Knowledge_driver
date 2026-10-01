# P_311 — MetroPT-3 Real Industrial Dataset Documentation

This document specifies the provenance, schema, statistical properties, failure event benchmarks, and architectural isolation of the **MetroPT-3** dataset used in Phase 22.

---

## 1. Dataset Provenance & Attribution

- **Dataset Identifier:** MetroPT-3 (Air Production Unit / Railway Compressor)
- **Originating Organization:** Metro do Porto (urban rail operator in Porto, Portugal) & INESC TEC (Institute for Systems and Computer Engineering, Technology and Science)
- **Authors:** Mahdi Davari, Bruno Veloso, Rita Ribeiro, and João Gama (University of Porto)
- **Scientific Citations:**
  - [1] M. Davari, B. Veloso, R. Ribeiro, J. Gama, *"A data-driven predictive maintenance framework for air production units in metro trains"*, IEEE International Conference on Data Science and Advanced Analytics (DSAA), 2021. DOI: [10.1109/DSAA53316.2021.9564181](https://doi.org/10.1109/DSAA53316.2021.9564181)
  - [2] B. Veloso, M. Davari, R. Ribeiro, J. Gama, *"MetroPT: A real-world dataset for predictive maintenance of railway components"*, Nature Scientific Data, 2022. DOI: [10.1038/s41597-022-01877-3](https://doi.org/10.1038/s41597-022-01877-3)
  - [3] UCI Machine Learning Repository: MetroPT Dataset. DOI: [10.24432/C5CH87](https://doi.org/10.24432/C5CH87)

---

## 2. Physical Machinery Context

The dataset records telemetry from an operational **Air Production Unit (APU)** installed on an active passenger rail train. The APU is a critical subsystem responsible for supplying compressed air to:
- Primary train friction and electro-pneumatic braking systems.
- Air suspension levelling bellows.
- Pneumatic passenger door actuators.
- Pantograph pneumatic lifting mechanisms.

The primary mechanical driver is a heavy-duty rotary screw air compressor driven by an electric 3-phase induction motor with desiccant air drying towers.

---

## 3. Dataset Characteristics & Audit Metrics

| Metric | Measured Value | Quality Audit Result |
| :--- | :--- | :---: |
| **Total Observations** | `1,516,948` rows | Verified |
| **Total Signal Channels** | `16` features + 1 timestamp | Verified |
| **Time Span** | `2020-02-01 00:00:00` to `2020-09-01 03:59:50` | 213.17 days (7 full months) |
| **Nominal Sampling Interval** | `10.0` seconds | Verified |
| **Observed Median Interval** | `10.0` seconds (Mean: 12.14s) | Verified |
| **Missing Values (Nulls)** | **`0`** across all columns (0.00%) | **100% Complete** |
| **Duplicate Timestamps** | **`0`** | **100% Unique** |
| **File Storage Footprint** | 208 MB raw CSV (`metropt3.csv`) | In-memory load: 185 MB |

---

## 4. Signal Catalog & Units

### 4.1 Continuous Physical Signals

| Signal Name | Physical Description | Unit | Min | Mean | Median | Max |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `Oil_temperature` | Compressor lubricating oil temperature | °C | 15.40 | 62.64 | 62.70 | 89.05 |
| `Motor_current` | Single-phase compressor motor operating current | A | 0.02 | 2.05 | 0.05 | 9.30 |
| `TP2` | Compressor discharge outlet pressure | bar | -0.03 | 1.37 | -0.01 | 10.68 |
| `TP3` | Pneumatic control panel internal pressure | bar | 0.73 | 8.99 | 8.96 | 10.30 |
| `H1` | Discharge pressure after cyclonic separator filter | bar | -0.04 | 7.57 | 8.78 | 10.29 |
| `DV_pressure` | Drying tower purge/discharge pressure | bar | -0.03 | 0.06 | -0.02 | 9.84 |
| `Reservoirs` | Main compressed air reservoir storage pressure | bar | 0.71 | 8.99 | 8.96 | 10.30 |

### 4.2 Digital Control & Machine State Signals

| Signal Name | Operational Meaning | Value Meaning | Active % |
| :--- | :--- | :--- | :---: |
| `COMP` | Air intake valve electrical control | 1.0 = valve closed (offloaded); 0.0 = valve open (compressing) | 83.70% (closed) |
| `DV_eletric` | Compressor discharge valve electrical signal | 1.0 = discharge valve open (under load); 0.0 = closed | 16.06% (open) |
| `Towers` | Active desiccant drying tower selector | 0.0 = Tower 1 active; 1.0 = Tower 2 active | 91.98% (Tower 2) |
| `MPG` | Main Pressure Governor pressure switch | 1.0 = pressure < 8.2 bar (cut-in request) | 83.27% |
| `LPS` | Low Pressure Safety switch | 1.0 = critical low pressure (< 7.0 bar warning) | 0.34% (5,188 rows) |
| `Pressure_switch`| Drying tower regeneration pressure sensor | 1.0 = pressure detected | 99.14% |
| `Oil_level` | Compressor oil reservoir level switch | 1.0 = low oil level warning | 90.42% |
| `Caudal_impulses`| Volumetric airflow pulse counter | Integer impulse count to reservoirs | Flow accumulation |

> [!IMPORTANT]
> **Strict Domain Boundary:**
> - MetroPT-3 contains **NO humidity** and **NO vibration** signals.
> - The dataset validator explicitly rejects any mapping that attempts to treat MetroPT-3 as live ESP32 simulator telemetry.

---

## 5. Machine Operating-State Classification

Based on motor electrical loading and valve states, APU operation is partitioned into three operational regimes:

1. **Standby / Off (`Motor_current < 1.0 A`):** Motor is de-energized or idle (~0.04 A). Comprises **54.65%** of observations (2,302.8 hours, mean oil temp 59.3°C).
2. **Offloaded / Idling (`1.0 A <= Motor_current < 5.5 A`):** Motor spins with intake valve closed (`COMP == 1.0`) preventing compression (~3.88 A). Comprises **32.06%** of observations (1,350.9 hours, mean oil temp 66.9°C).
3. **Under Load / Compressing (`Motor_current >= 5.5 A`):** Motor actively compresses air with intake open (`COMP == 0.0`) and discharge open (`DV_eletric == 1.0`) (~5.89 A). Comprises **13.29%** of observations (560.1 hours, mean oil temp 66.2°C).

---

## 6. Ground Truth Failure Event Cross-Validation

The published literature records four major real-world pneumatic air leak events that caused severe compressor degradation:

| Event ID | Period | Failure Description | Readings | UnderLoad Duty Cycle | Ratio vs Baseline | Mean Temp | Max Temp | LPS Trips (<7 bar) | Detection Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **EV-01** | `2020-04-18` | Air Leak / High Stress | 8,663 | **83.60%** | **6.29x** | 74.13°C | 78.17°C | 0 | **DETECTED** |
| **EV-02** | `2020-05-29` to `05-30` | Air Leak / Compressor Stress | 2,360 | **79.75%** | **6.00x** | 75.87°C | 76.65°C | 0 | **DETECTED** |
| **EV-03** | `2020-06-05` to `06-07` | Severe Air Leak / Cutoff | 17,315 | **62.11%** | **4.67x** | 75.52°C | 78.03°C | 198 | **DETECTED** |
| **EV-04** | `2020-07-15` | Air Leak / Thermal Overheat | 1,622 | **52.53%** | **3.95x** | 83.91°C | 89.05°C | 530 | **DETECTED** |

### Key Physical Failure Insights:
1. **Duty Cycle Elongation:** In normal operation, the compressor operates under load only **13.29%** of the time. When pneumatic leaks occur, continuous air loss forces the compressor into **62%–84% continuous load** (up to a **6.3x** increase).
2. **Thermal Stress:** Prolonged compression drives lubricating oil temperatures from ~60°C up to **74–84°C** (peaking at **89.05°C** during EV-04).
3. **Pneumatic Depletion:** Severe air leaks eventually exceed compressor recovery capacity, causing storage pressure to fall below 7.0 bar and triggering **198** and **530** Low Pressure Safety (`LPS`) trips.

---

## 7. Strict Architectural Isolation

The MetroPT-3 dataset is processed solely via `ai/dataset/metropt/src/run_pipeline.py`.
- **Zero Live Contamination:** MetroPT-3 rows are **never** inserted into the live `sensor_readings` table.
- **Isolated Artifacts:** All analytical outputs are saved locally to `ai/dataset/metropt/output/` without affecting Mosquitto, Spring Boot, or the live React dashboard.
