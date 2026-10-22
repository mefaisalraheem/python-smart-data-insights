"""Generate matplotlib charts embedded in the HTML report as base64 PNGs."""

from __future__ import annotations

import base64
import io
from typing import Optional

import matplotlib

matplotlib.use("Agg")  # headless backend

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


def _fig_to_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=90, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


def missing_values_chart(df: pd.DataFrame) -> Optional[str]:
    """Bar chart of missing-value % per column (returns None if no missing data)."""
    missing = df.isna().mean() * 100
    missing = missing[missing > 0].sort_values(ascending=False)
    if missing.empty:
        return None

    fig, ax = plt.subplots(figsize=(8, max(2.5, 0.35 * len(missing))))
    missing.plot(kind="barh", ax=ax, color="#e74c3c")
    ax.set_xlabel("% missing")
    ax.set_title("Missing Values by Column")
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.3)
    return _fig_to_b64(fig)


def numeric_distributions(df: pd.DataFrame, max_cols: int = 6) -> list[tuple[str, str]]:
    """Histograms for numeric columns. Returns list of (column_name, base64_png)."""
    numeric = df.select_dtypes(include="number").dropna(how="all", axis=1)
    charts: list[tuple[str, str]] = []
    for col in list(numeric.columns)[:max_cols]:
        series = numeric[col].dropna()
        if series.empty:
            continue
        fig, ax = plt.subplots(figsize=(6, 3.2))
        ax.hist(series, bins=30, color="#3498db", edgecolor="white")
        ax.set_title(f"Distribution: {col}")
        ax.set_ylabel("count")
        ax.grid(alpha=0.3)
        charts.append((str(col), _fig_to_b64(fig)))
    return charts


def correlation_heatmap(df: pd.DataFrame) -> Optional[str]:
    """Correlation heatmap for numeric columns (requires >=2 numeric cols)."""
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        return None

    corr = numeric.corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(max(4, corr.shape[1] * 0.9), max(3, corr.shape[1] * 0.8)))
    im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticklabels(corr.columns)
    for i in range(len(corr)):
        for j in range(len(corr)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8, color="black")
    ax.set_title("Correlation Matrix")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    return _fig_to_b64(fig)