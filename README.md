# Smart Data Insights Engine

Automated insights from CSV / Excel files: **missing value detection**, **anomaly detection**, **descriptive statistics**, and **self-contained HTML reports** — with a clean CLI and full test suite.

## Features

- 📥 **Load** CSV, `.xlsx`, `.xls` (with sheet selection)
- 📊 **Analyze** — dtypes, null rates, unique counts, descriptive stats, correlations
- 🚨 **Detect anomalies** using **IQR** or **Z-score** methods
- ⚠️ **Flag quality issues** — high missingness, constant columns, duplicates, whitespace, high-cardinality IDs
- 📈 **Visualize** — missing-value bars, histograms, correlation heatmap (embedded as base64 PNG)
- 📝 **Report** — single-file HTML with KPIs, issue tables, and charts
- ✅ **Tested** with pytest + coverage

## Install

```bash
git clone https://github.com/mefaisalraheem/python-smart-data-insights
cd python-smart-data-insights
pip install -e ".[dev]"
```

## Usage

```bash
# Basic
smart-insights examples/sample.csv -o report.html

# Excel sheet + z-score anomalies
smart-insights data.xlsx --sheet Sheet1 --method zscore --z 2.5 -o out.html

# Skip charts (faster for huge files)
smart-insights big.csv --no-charts
```

Output:

```
✓ Report written to report.html
  Rows: 15   Columns: 6
  Missing: 7.78%   Duplicates: 0
  Issues: 3   Anomalies: 2
```

### As a library

```python
from smart_insights.loader import load_dataframe
from smart_insights.analyzer import analyze
from smart_insights.detector import detect_anomalies, detect_quality_issues
from smart_insights.reporter import render_html

df = load_dataframe("data.csv")
summary = analyze(df)
anomalies = detect_anomalies(df, method="iqr")
issues = detect_quality_issues(df)

render_html("data.csv", summary, anomalies, issues, charts, "report.html")
```

## Tests

```bash
pytest
```

## Architecture

| Module | Responsibility |
|---|---|
| `loader.py` | Validate + parse CSV/Excel |
| `analyzer.py` | Descriptive statistics |
| `detector.py` | Anomaly + quality detection |
| `visualizer.py` | Matplotlib charts → base64 |
| `reporter.py` | Jinja2 HTML rendering |
| `cli.py` | Argument parsing, orchestration |

## License

MIT