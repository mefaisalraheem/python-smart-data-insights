"""Compute descriptive statistics and data quality metrics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class ColumnSummary:
    name: str
    dtype: str
    non_null: int
    null_count: int
    null_pct: float
    unique: int
    sample_values: list[Any] = field(default_factory=list)
    numeric_stats: dict[str, float] = field(default_factory=dict)


@dataclass
class DatasetSummary:
    rows: int
    columns: int
    memory_kb: float
    duplicate_rows: int
    total_missing: int
    missing_pct: float
    column_summaries: list[ColumnSummary]
    numeric_summary: pd.DataFrame
    categorical_summary: pd.DataFrame
    correlation: pd.DataFrame


def _safe_scalar(x: Any) -> Any:
    try:
        if pd.isna(x):
            return None
    except (TypeError, ValueError):
        return x
    if hasattr(x, "item"):
        return x.item()
    return x


def analyze(df: pd.DataFrame, sample_size: int = 3) -> DatasetSummary:
    """Return a full summary of the dataset."""
    rows, cols = df.shape
    total_missing = int(df.isna().sum().sum())
    cells = rows * cols
    missing_pct = (total_missing / cells * 100.0) if cells else 0.0

    column_summaries: list[ColumnSummary] = []
    for name in df.columns:
        series = df[name]
        non_null = int(series.notna().sum())
        null_count = int(series.isna().sum())
        null_pct = (null_count / rows * 100.0) if rows else 0.0
        uniques = int(series.nunique(dropna=True))

        samples = [(_safe_scalar(v)) for v in series.dropna().head(sample_size)]

        numeric_stats: dict[str, float] = {}
        if pd.api.types.is_numeric_dtype(series) and non_null > 0:
            desc = series.describe()
            numeric_stats = {
                k: float(desc[k]) for k in ("mean", "std", "min", "25%", "50%", "75%", "max") if k in desc
            }

        column_summaries.append(
            ColumnSummary(
                name=str(name),
                dtype=str(series.dtype),
                non_null=non_null,
                null_count=null_count,
                null_pct=round(null_pct, 2),
                unique=uniques,
                sample_values=samples,
                numeric_stats={k: round(v, 4) for k, v in numeric_stats.items()},
            )
        )

    numeric_cols = df.select_dtypes(include="number")
    if not numeric_cols.empty:
        numeric_summary = numeric_cols.describe().transpose().round(4)
    else:
        numeric_summary = pd.DataFrame()

    cat_cols = df.select_dtypes(include=["object", "category", "bool"])
    if not cat_cols.empty:
        cat_data = {
            "unique": cat_cols.nunique(),
            "top": cat_cols.apply(lambda s: s.mode().iloc[0] if not s.mode().empty else None),
            "freq": cat_cols.apply(lambda s: int(s.value_counts().iloc[0]) if not s.value_counts().empty else 0),
        }
        categorical_summary = pd.DataFrame(cat_data)
    else:
        categorical_summary = pd.DataFrame()

    correlation = (
        numeric_cols.corr(numeric_only=True).round(3)
        if numeric_cols.shape[1] > 1
        else pd.DataFrame()
    )

    return DatasetSummary(
        rows=rows,
        columns=cols,
        memory_kb=round(df.memory_usage(deep=True).sum() / 1024.0, 2),
        duplicate_rows=int(df.duplicated().sum()),
        total_missing=total_missing,
        missing_pct=round(missing_pct, 2),
        column_summaries=column_summaries,
        numeric_summary=numeric_summary,
        categorical_summary=categorical_summary,
        correlation=correlation,
    )