# P22: Real Industrial Dataset Validation using MetroPT-3

This directory contains the reproducible offline industrial validation pipeline for **P_311 — Knowledge-Driven IoT Fault Diagnosis Assistant**, using the real-world **MetroPT-3** dataset from Metro do Porto urban rail trains.

---

## 1. Dataset Provenance & Literature Citations

- **Dataset Name:** MetroPT-3 (Air Production Unit / Screw Compressor)
- **Origin / Authors:** INESC TEC & Metro do Porto, Portugal (Mahdi Davari, Bruno Veloso, Rita Ribeiro, João Gama)
- **Scientific Citations:**
  - [1] M. Davari, B. Veloso, R. Ribeiro, J. Gama, *"A data-driven predictive maintenance framework for air production units in metro trains"*, IEEE International Conference on Data Science and Advanced Analytics (DSAA), 2021. DOI: [10.1109/DSAA53316.2021.9564181](https://doi.org/10.1109/DSAA53316.2021.9564181)
  - [2] B. Veloso, M. Davari, R. Ribeiro, J. Gama, *"MetroPT: A real-world dataset for predictive maintenance of railway components"*, Nature Scientific Data, 2022. DOI: [10.1038/s41597-022-01877-3](https://doi.org/10.1038/s41597-022-01877-3)
  - [3] UCI Machine Learning Repository: MetroPT Dataset. DOI: [10.24432/C5CH87](https://doi.org/10.24432/C5CH87)

---

## 2. Architecture & Strict Pipeline Isolation

The MetroPT-3 dataset is used strictly for **offline industrial benchmarking and physical validation**. It is completely isolated from the live operational IoT pipeline:

```text
┌────────────────────────────────────────────────────────┐
│               LIVE OPERATIONAL PIPELINE                │
│ (Real-time simulated telemetry, AI & dashboards)       │
│                                                        │
│  Python Sensor Simulator (ESP32 emulation)             │
│            ↓                                           │
│      MQTT Mosquitto (port 1883)                        │
│            ↓                                           │
│    Spring Boot Backend (port 8080)                     │
│            ↓                                           │
│   PostgreSQL (sensor_readings, diagnosis_records)      │
│            ↓                                           │
│   React Dashboard (5173) & Grafana (3000)              │
└────────────────────────────────────────────────────────┘

                           ≠ (COMPLETELY ISOLATED)

┌────────────────────────────────────────────────────────┐
│             OFFLINE P22 VALIDATION PIPELINE            │
│ (Reproducible industrial benchmark using MetroPT-3)   │
│                                                        │
│  MetroPT-3 CSV (208 MB, 1,516,948 rows)                │
│            ↓                                           │
│  MetroPTLoader (loader.py)                             │
│            ↓                                           │
│  MetroPTValidator (validator.py)                       │
│            ↓                                           │
│  MetroPTFeatureExtractor (features.py)                 │
│            ↓                                           │
│  MetroPTAnalyzer (analyzer.py)                         │
│            ↓                                           │
│  MetroPTReportGenerator (report.py)                    │
│            ↓                                           │
│  JSON Artifacts, Validation Report & 6 Plots           │
└────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Signal Distinction:**
> - MetroPT-3 contains real APU signals: **Oil Temperature**, **Motor Current**, and 5 pneumatic pressures (**TP2**, **TP3**, **H1**, **DV_pressure**, **Reservoirs**), plus 8 control signals.
> - MetroPT-3 contains **NO humidity** and **NO vibration** signals.
> - The validator explicitly rejects any mapping that attempts to treat MetroPT-3 as ESP32 telemetry, ensuring zero live pipeline pollution.

---

## 3. Directory Structure

```text
ai/dataset/metropt/
├── README.md               # This documentation
├── requirements.txt        # Python dependencies (pandas, numpy, matplotlib)
├── data/
│   └── metropt3.csv        # Symlink to raw CSV (metropt+3+dataset/MetroPT3(AirCompressor).csv)
├── src/
│   ├── __init__.py         # Package entry point
│   ├── loader.py           # Loads CSV, parses timestamps, audits quality
│   ├── validator.py        # Validates schema, boundaries, and isolation
│   ├── features.py         # Statistical summaries of continuous & state signals
│   ├── analyzer.py         # Operating states & ground truth failure evaluation
│   ├── report.py           # Markdown report, JSON artifacts & 6 plots
│   └── run_pipeline.py     # Main CLI orchestrator
├── output/
│   ├── dataset_summary.json
│   ├── feature_summary.json
│   ├── anomaly_summary.json
│   ├── validation_report.md
│   └── plots/
│       ├── oil_temperature_timeline.png
│       ├── motor_current_timeline.png
│       ├── pressure_signals_timeline.png
│       ├── current_vs_temperature.png
│       ├── operating_state_transitions.png
│       └── anomaly_detection_overlay.png
└── tests/
    ├── test_loader.py
    ├── test_validator.py
    ├── test_features.py
    ├── test_analyzer.py
    └── test_report.py
```

---

## 4. How to Run

### Install Dependencies
```bash
source ai/vector-db/.venv/bin/activate
pip install -r ai/dataset/metropt/requirements.txt
```

### Run Full Pipeline
```bash
./ai/vector-db/.venv/bin/python3 ai/dataset/metropt/src/run_pipeline.py
```

### Optional Arguments
- `--data-path <path>`: Custom path to the dataset CSV file.
- `--output-dir <path>`: Custom directory for output reports and plots.
- `--nrows <int>`: Fast run limiting the dataset to first N rows.
- `--skip-plots`: Run data validation and JSON reporting without generating plots.

### Run Unit Tests
```bash
./ai/vector-db/.venv/bin/pytest ai/dataset/metropt/tests -v
```
