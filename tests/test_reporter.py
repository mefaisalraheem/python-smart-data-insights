from pathlib import Path

from smart_insights.analyzer import analyze
from smart_insights.detector import detect_anomalies, detect_quality_issues
from smart_insights.reporter import render_html


def test_render_html(sample_df, tmp_path):
    summary = analyze(sample_df)
    anomaly = detect_anomalies(sample_df)
    issues = detect_quality_issues(sample_df)

    out = render_html(
        dataset_name="sample.csv",
        summary=summary,
        anomaly=anomaly,
        issues=issues,
        charts={"missing": None, "correlation": None, "distributions": []},
        output_path=tmp_path / "report.html",
    )

    assert isinstance(out, Path)
    assert out.exists()
    html = out.read_text()
    assert "Smart Data Insights" in html
    assert "sample.csv" in html
    assert "Dataset overview" in html