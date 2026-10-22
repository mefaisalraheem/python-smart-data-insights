from smart_insights.detector import detect_anomalies, detect_quality_issues


def test_iqr_detects_outlier(sample_df):
    r = detect_anomalies(sample_df, method="iqr")
    assert "value" in r.per_column
    assert r.per_column["value"]["count"] >= 1
    assert 1000.0 in r.per_column["value"]["extreme_values"]


def test_zscore_method(sample_df):
    r = detect_anomalies(sample_df, method="zscore", z_threshold=1.5)
    assert r.method == "zscore"
    assert r.total_anomalies >= 1


def test_invalid_method(sample_df):
    import pytest
    with pytest.raises(ValueError):
        detect_anomalies(sample_df, method="bogus")


def test_quality_missing(sample_df):
    issues = detect_quality_issues(sample_df)
    cols = {i.column for i in issues}
    assert "name" in cols


def test_constant_column():
    import pandas as pd
    df = pd.DataFrame({"a": [1, 1, 1], "b": [1, 2, 3]})
    issues = detect_quality_issues(df)
    assert any(i.column == "a" and "constant" in i.message for i in issues)


def test_duplicate_rows_issue():
    import pandas as pd
    df = pd.DataFrame({"a": [1, 1], "b": [2, 2]})
    issues = detect_quality_issues(df)
    assert any(i.column == "<rows>" for i in issues)