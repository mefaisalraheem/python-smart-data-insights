import pandas as pd
import pytest

from smart_insights.loader import DataLoadError, load_dataframe


def test_load_csv(tmp_path):
    p = tmp_path / "data.csv"
    pd.DataFrame({"a": [1, 2], "b": ["x", "y"]}).to_csv(p, index=False)
    df = load_dataframe(p)
    assert list(df.columns) == ["a", "b"]
    assert len(df) == 2


def test_load_excel(tmp_path):
    p = tmp_path / "data.xlsx"
    pd.DataFrame({"a": [1, 2]}).to_excel(p, index=False)
    df = load_dataframe(p)
    assert list(df.columns) == ["a"]


def test_missing_file(tmp_path):
    with pytest.raises(DataLoadError, match="File not found"):
        load_dataframe(tmp_path / "nope.csv")


def test_unsupported_extension(tmp_path):
    p = tmp_path / "data.txt"
    p.write_text("hello")
    with pytest.raises(DataLoadError, match="Unsupported extension"):
        load_dataframe(p)


def test_empty_csv(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text("a,b\n")
    with pytest.raises(DataLoadError):
        load_dataframe(p)