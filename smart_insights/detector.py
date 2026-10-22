"""Detect anomalies and data quality issues."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd

AnomalyMethod = Literal["iqr", "zscore"]


@dataclass
class AnomalyReport:
    method: str
    per_column: dict[str, dict] = field(default_factory=dict)
    total_anomalies: int = 0


@dataclass
class QualityIssue:
    severity: Literal["info", "warning", "critical"]
    column: str
    message: str


def detect_anomalies(
    df: pd.DataFrame,
    method: AnomalyMethod = "iqr",
    z_threshold: float = 3.0,
    iqr_multiplier: float = 1.5,
) -> AnomalyReport:
    """Detect numeric outliers using IQR or Z-score."""
    numeric = df.select_dtypes(include="number")
    report = AnomalyReport(method=method)

    for col in numeric.columns:
        series = numeric[col].dropna()
        if series.empty:
            continue

        if method == "iqr":
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - iqr_multiplier * iqr, q3 + iqr_multiplier * iqr
            mask = (numeric[col] < lower) | (numeric[col] > upper)
            bounds = {"lower": float(lower), "upper": float(upper)}
        elif method == "zscore":
            mean, std = series.mean(), series.std(ddof=0)
            if std == 0 or np.isnan(std):
                continue
            z = (numeric[col] - mean) / std
            mask = z.abs() > z_threshold
            bounds = {"mean": float(mean), "std": float(std)}
        else:
            raise ValueError(f"Unknown method: {method}")

        count = int(mask.sum())
        if count:
            report.per_column[str(col)] = {
                "count": count,
                "pct": round(count / len(series) * 100, 2),
                "bounds": {k: round(v, 4) for k, v in bounds.items()},
                "extreme_values": sorted(
                    series[mask].tolist(), key=lambda v: abs(v), reverse=True
                )[:5],
            }
            report.total_anomalies += count

    return report


def detect_quality_issues(df: pd.DataFrame, high_cardinality_threshold: int = 50) -> list[QualityIssue]:
    """Flag common data quality problems."""
    issues: list[QualityIssue] = []
    n = len(df) or 1

    for col in df.columns:
        series = df[col]
        null_pct = series.isna().mean() * 100

        if null_pct >= 50:
            issues.append(QualityIssue("critical", str(col), f"{null_pct:.1f}% missing values"))
        elif null_pct >= 10:
            issues.append(QualityIssue("warning", str(col), f"{null_pct:.1f}% missing values"))

        if series.nunique(dropna=True) == 1 and series.notna().any():
            issues.append(QualityIssue("warning", str(col), "Column has a single constant value"))

        if series.dtype == object:
            stripped = series.dropna().astype(str).str.strip()
            if (stripped != series.dropna().astype(str)).any():
                issues.append(QualityIssue("info", str(col), "Leading/trailing whitespace detected"))
            if series.nunique(dropna=True) > high_cardinality_threshold and series.nunique() / n > 0.5:
                issues.append(
                    QualityIssue("info", str(col), "High-cardinality categorical column (likely ID)")
                )

        if pd.api.types.is_numeric_dtype(series) and series.notna().sum() > 0:
            if (series.dropna() < 0).all() and series.min() < 0:
                issues.append(QualityIssue("info", str(col), "All values negative"))

    if df.duplicated().any():
        dup = int(df.duplicated().sum())
        issues.append(QualityIssue("warning", "<rows>", f"{dup} duplicate rows found"))

    return issues