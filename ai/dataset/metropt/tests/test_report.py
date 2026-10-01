import json
import sys
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from loader import MetroPTLoader
from validator import MetroPTValidator
from features import MetroPTFeatureExtractor
from analyzer import MetroPTAnalyzer
from report import MetroPTReportGenerator


def test_report_generator_artifacts_and_plots(tmp_path):
    loader = MetroPTLoader()
    df, audit = loader.load_data(nrows=200)

    validator = MetroPTValidator()
    val_res = validator.validate(df)

    extractor = MetroPTFeatureExtractor()
    feat_res = extractor.extract_summary(df)

    analyzer = MetroPTAnalyzer()
    ana_res = analyzer.run_full_analysis(df)

    reporter = MetroPTReportGenerator(output_dir=str(tmp_path / "output"))
    reporter.save_json_artifacts(audit, val_res, feat_res, ana_res)

    # Check that JSON files were created and are valid
    dataset_json = tmp_path / "output" / "dataset_summary.json"
    feature_json = tmp_path / "output" / "feature_summary.json"
    anomaly_json = tmp_path / "output" / "anomaly_summary.json"

    assert dataset_json.exists()
    assert feature_json.exists()
    assert anomaly_json.exists()

    with open(dataset_json, "r") as f:
        data = json.load(f)
        assert data["dataset_name"] == "MetroPT-3 (Air Production Unit / Compressor)"
        assert data["audit"]["total_rows"] == 200

    # Test plot generation
    plots = reporter.generate_plots(df, ana_res)
    assert len(plots) == 6
    for name, path_str in plots.items():
        p = Path(path_str)
        assert p.exists()
        assert p.stat().st_size > 0

    # Test markdown report generation
    md_path_str = reporter.generate_markdown_report(audit, val_res, feat_res, ana_res, plots)
    md_path = Path(md_path_str)
    assert md_path.exists()
    content = md_path.read_text(encoding="utf-8")
    assert "P22: Real Industrial Dataset Validation Report" in content
    assert "MetroPT-3" in content
    assert "Operating-State Analysis" in content
    assert "plots/oil_temperature_timeline.png" in content
