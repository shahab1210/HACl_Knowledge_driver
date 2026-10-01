"""
MetroPT-3 Validation Pipeline Orchestrator.
Executes data loading, validation, feature extraction, anomaly analysis,
and report/plot generation in a single reproducible command.
"""

import argparse
import sys
import time
from pathlib import Path

# Add src directory to path if running directly
sys.path.insert(0, str(Path(__file__).resolve().parent))

from loader import MetroPTLoader
from validator import MetroPTValidator
from features import MetroPTFeatureExtractor
from analyzer import MetroPTAnalyzer
from report import MetroPTReportGenerator


def run_pipeline(
    data_path: str = None,
    output_dir: str = None,
    nrows: int = None,
    sample_fraction: float = None,
    skip_plots: bool = False
):
    print("=" * 70)
    print("P_311 — Phase 22: MetroPT-3 Industrial Dataset Validation Pipeline")
    print("=" * 70)
    t0 = time.time()

    # 1. Loading
    print("\n[1/5] Loading and Auditing MetroPT-3 Dataset...")
    loader = MetroPTLoader(data_path=data_path)
    df, audit_summary = loader.load_data(nrows=nrows, sample_fraction=sample_fraction)
    print(f"      Loaded {audit_summary['total_rows']:,} rows across {audit_summary['total_columns']} columns.")
    print(f"      Time span: {audit_summary['start_time']} to {audit_summary['end_time']} ({audit_summary['duration_days']} days)")
    print(f"      Sampling interval median: {audit_summary['observed_median_interval_sec']}s (nominal 10.0s)")
    print(f"      Data quality: {audit_summary['total_nulls']} nulls, {audit_summary['duplicate_timestamps']} duplicate timestamps.")

    # 2. Validation
    print("\n[2/5] Validating Schema, Physical Bounds, and Dataset Isolation...")
    validator = MetroPTValidator()
    val_results = validator.validate(df)
    if not val_results["is_valid"]:
        print(f"      [ERROR] Validation failed: {val_results['errors']}")
        sys.exit(1)
    print("      [PASS] Schema integrity confirmed.")
    print(f"      [PASS] Dataset isolation confirmed (Prohibited signals check: {val_results['forbidden_signals_found']}).")
    print(f"      Physical boundary warnings: {val_results['warnings_count']}")

    # 3. Feature Extraction
    print("\n[3/5] Extracting Continuous & Machine State Features...")
    extractor = MetroPTFeatureExtractor()
    feature_summary = extractor.extract_summary(df)
    cont_signals = list(feature_summary["continuous_signals"].keys())
    state_signals = list(feature_summary["machine_state_signals"].keys())
    print(f"      Continuous signals summarized ({len(cont_signals)}): {cont_signals}")
    print(f"      Machine state signals summarized ({len(state_signals)}): {state_signals}")

    # 4. Anomaly & Operational State Analysis
    print("\n[4/5] Analyzing Operating States, Anomaly Detection & Ground Truth Failures...")
    analyzer = MetroPTAnalyzer()
    analysis_results = analyzer.run_full_analysis(df)
    op_states = analysis_results["operating_states"]
    for state, details in op_states.items():
        print(f"      State '{state}': {details['percentage']}% ({details['duration_hours']} hrs, Mean Current: {details['mean_motor_current_a']}A, Mean Temp: {details['mean_oil_temp_c']}°C)")

    gt_evals = analysis_results["ground_truth_evaluations"]
    print(f"      Ground truth failure events evaluated ({len(gt_evals)}):")
    for ev in gt_evals:
        status = "DETECTED" if ev["anomaly_detected"] else "MISSED"
        print(f"        - {ev['event_id']} ({ev['name']}): {ev['reading_count']:,} readings | UnderLoad Duty: {ev['underload_percentage']}% ({ev['duty_cycle_ratio_vs_baseline']}x normal) | Status: {status}")

    # 5. Reporting and Visualizations
    print("\n[5/5] Generating Artifacts, Plots, and Markdown Validation Report...")
    reporter = MetroPTReportGenerator(output_dir=output_dir)
    reporter.save_json_artifacts(audit_summary, val_results, feature_summary, analysis_results)
    print(f"      Saved JSON artifacts to: {reporter.output_dir}")

    plot_paths = {}
    if not skip_plots:
        print("      Generating 6 analytical figures...")
        plot_paths = reporter.generate_plots(df, analysis_results)
        for name, path in plot_paths.items():
            print(f"        - {name}: {path}")
    else:
        print("      Skipping plots as requested.")

    report_path = reporter.generate_markdown_report(
        audit_summary, val_results, feature_summary, analysis_results, plot_paths
    )
    print(f"      Generated Markdown report at: {report_path}")

    elapsed = time.time() - t0
    print("\n" + "=" * 70)
    print(f"P22 Pipeline completed successfully in {elapsed:.2f} seconds.")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run P22 MetroPT-3 Industrial Dataset Validation Pipeline")
    parser.add_argument("--data-path", type=str, default=None, help="Path to MetroPT3 CSV file")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory for reports and plots")
    parser.add_argument("--nrows", type=int, default=None, help="Row limit for testing")
    parser.add_argument("--sample-fraction", type=float, default=None, help="Fraction to sample")
    parser.add_argument("--skip-plots", action="store_true", help="Skip plot generation")
    args = parser.parse_args()

    run_pipeline(
        data_path=args.data_path,
        output_dir=args.output_dir,
        nrows=args.nrows,
        sample_fraction=args.sample_fraction,
        skip_plots=args.skip_plots,
    )
