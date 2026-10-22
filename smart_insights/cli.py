"""Command-line interface."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from smart_insights import __version__
from smart_insights.analyzer import analyze
from smart_insights.detector import detect_anomalies, detect_quality_issues
from smart_insights.loader import DataLoadError, load_dataframe
from smart_insights.reporter import render_html
from smart_insights.visualizer import (
    correlation_heatmap,
    missing_values_chart,
    numeric_distributions,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="smart-insights",
        description="Analyze CSV/Excel files: missing values, anomalies, stats, HTML report.",
    )
    parser.add_argument("input", type=Path, help="Path to CSV or Excel file")
    parser.add_argument("-o", "--output", type=Path, default=Path("report.html"),
                        help="Output HTML report path (default: report.html)")
    parser.add_argument("--sheet", default=None,
                        help="Excel sheet name or index (ignored for CSV)")
    parser.add_argument("--method", choices=["iqr", "zscore"], default="iqr",
                        help="Anomaly detection method (default: iqr)")
    parser.add_argument("--z", type=float, default=3.0,
                        help="Z-score threshold when --method=zscore (default: 3.0)")
    parser.add_argument("--no-charts", action="store_true", help="Skip chart generation")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        sheet = None
        if args.sheet is not None:
            sheet = int(args.sheet) if args.sheet.isdigit() else args.sheet
        df = load_dataframe(args.input, sheet_name=sheet)
    except DataLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    summary = analyze(df)
    issues = detect_quality_issues(df)
    anomalies = detect_anomalies(df, method=args.method, z_threshold=args.z)

    charts: dict = {"missing": None, "correlation": None, "distributions": []}
    if not args.no_charts:
        charts["missing"] = missing_values_chart(df)
        charts["correlation"] = correlation_heatmap(df)
        charts["distributions"] = numeric_distributions(df)

    out = render_html(
        dataset_name=args.input.name,
        summary=summary,
        anomaly=anomalies,
        issues=issues,
        charts=charts,
        output_path=args.output,
    )

    if not args.quiet:
        print(f"\n✓ Report written to {out}")
        print(f"  Rows: {summary.rows:,}   Columns: {summary.columns}")
        print(f"  Missing: {summary.missing_pct}%   Duplicates: {summary.duplicate_rows}")
        print(f"  Issues: {len(issues)}   Anomalies: {anomalies.total_anomalies}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())