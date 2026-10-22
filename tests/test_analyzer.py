from smart_insights.analyzer import analyze


def test_summary_shape(sample_df):
    s = analyze(sample_df)
    assert s.rows == 5
    assert s.columns == 4
    assert s.total_missing == 1
    assert s.missing_pct == 5.0
    assert len(s.column_summaries) == 4


def test_null_pct_per_column(sample_df):
    s = analyze(sample_df)
    by_name = {c.name: c for c in s.column_summaries}
    assert by_name["name"].null_count == 1
    assert by_name["name"].null_pct == 20.0
    assert by_name["id"].null_count == 0


def test_numeric_summary(sample_df):
    s = analyze(sample_df)
    assert "value" in s.numeric_summary.index
    assert "mean" in s.numeric_summary.columns


def test_correlation_present(sample_df):
    s = analyze(sample_df)
    # Only id and value are numeric -> 2x2 correlation
    assert s.correlation.shape == (2, 2)


def test_duplicate_detection():
    import pandas as pd
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    s = analyze(df)
    assert s.duplicate_rows == 1