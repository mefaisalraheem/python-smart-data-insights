"""Render an HTML report from analyzer/detector outputs."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, select_autoescape

from smart_insights import __version__
from smart_insights.analyzer import DatasetSummary
from smart_insights.detector import AnomalyReport, QualityIssue


_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Smart Data Insights — {{ dataset_name }}</title>
<style>
  :root { --fg:#1f2937; --muted:#6b7280; --bg:#f8fafc; --card:#fff; --border:#e5e7eb;
          --accent:#2563eb; --warn:#f59e0b; --crit:#dc2626; --ok:#16a34a; }
  * { box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
         margin: 0; background: var(--bg); color: var(--fg); line-height: 1.5; }
  header { background: linear-gradient(135deg,#2563eb,#7c3aed); color: white; padding: 2rem; }
  header h1 { margin: 0 0 .25rem; font-size: 1.75rem; }
  header p { margin: 0; opacity: .9; font-size: .9rem; }
  main { max-width: 1100px; margin: 0 auto; padding: 2rem 1rem 4rem; }
  section { background: var(--card); border: 1px solid var(--border); border-radius: 12px;
            padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; }
  section h2 { margin: 0 0 1rem; font-size: 1.15rem; }
  .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px,1fr)); gap: 1rem; }
  .kpi { background: var(--bg); border-radius: 8px; padding: .75rem 1rem; }
  .kpi .label { color: var(--muted); font-size: .8rem; text-transform: uppercase; letter-spacing: .03em; }
  .kpi .value { font-size: 1.6rem; font-weight: 600; margin-top: .25rem; }
  table { width: 100%; border-collapse: collapse; font-size: .88rem; }
  th, td { text-align: left; padding: .5rem .6rem; border-bottom: 1px solid var(--border); }
  th { color: var(--muted); font-weight: 500; font-size: .8rem; text-transform: uppercase; }
  tr:hover td { background: #f9fafb; }
  .badge { display: inline-block; padding: .1rem .5rem; border-radius: 999px; font-size: .75rem; font-weight: 600; }
  .badge.info { background: #e0f2fe; color: #0369a1; }
  .badge.warning { background: #fef3c7; color: #b45309; }
  .badge.critical { background: #fee2e2; color: #b91c1c; }
  .chart { margin: 1rem 0; text-align: center; }
  .chart img { max-width: 100%; border-radius: 8px; }
  .charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px,1fr)); gap: 1rem; }
  .empty { color: var(--muted); font-style: italic; }
</style>
</head>
<body>
<header>
  <h1>Smart Data Insights</h1>
  <p>{{ dataset_name }} &middot; generated {{ generated_at }} &middot; v{{ version }}</p>
</header>
<main>

<section>
  <h2>Dataset overview</h2>
  <div class="kpis">
    <div class="kpi"><div class="label">Rows</div><div class="value">{{ summary.rows }}</div></div>
    <div class="kpi"><div class="label">Columns</div><div class="value">{{ summary.columns }}</div></div>
    <div class="kpi"><div class="label">Missing</div><div class="value">{{ summary.missing_pct }}%</div></div>
    <div class="kpi"><div class="label">Duplicates</div><div class="value">{{ summary.duplicate_rows }}</div></div>
    <div class="kpi"><div class="label">Memory</div><div class="value">{{ summary.memory_kb }} KB</div></div>
  </div>
</section>

<section>
  <h2>Data quality issues ({{ issues|length }})</h2>
  {% if issues %}
    <table>
      <thead><tr><th>Severity</th><th>Column</th><th>Issue</th></tr></thead>
      <tbody>
      {% for issue in issues %}
        <tr><td><span class="badge {{ issue.severity }}">{{ issue.severity }}</span></td>
            <td>{{ issue.column }}</td><td>{{ issue.message }}</td></tr>
      {% endfor %}
      </tbody>
    </table>
  {% else %}
    <p class="empty">No quality issues detected. 🎉</p>
  {% endif %}
</section>

<section>
  <h2>Anomalies ({{ anomaly.method|upper }}, {{ anomaly.total_anomalies }} total)</h2>
  {% if anomaly.per_column %}
    <table>
      <thead><tr><th>Column</th><th>Count</th><th>%</th><th>Bounds</th><th>Extreme values</th></tr></thead>
      <tbody>
      {% for col, info in anomaly.per_column.items() %}
        <tr>
          <td>{{ col }}</td><td>{{ info.count }}</td><td>{{ info.pct }}%</td>
          <td>{{ info.bounds }}</td>
          <td>{{ info.extreme_values|join(", ") }}</td>
        </tr>
      {% endfor %}
      </tbody>
    </table>
  {% else %}
    <p class="empty">No anomalies detected.</p>
  {% endif %}
</section>

{% if charts.missing %}
<section>
  <h2>Missing values</h2>
  <div class="chart"><img src="data:image/png;base64,{{ charts.missing }}" alt="missing values"></div>
</section>
{% endif %}

{% if charts.correlation %}
<section>
  <h2>Correlation</h2>
  <div class="chart"><img src="data:image/png;base64,{{ charts.correlation }}" alt="correlation"></div>
</section>
{% endif %}

{% if charts.distributions %}
<section>
  <h2>Numeric distributions</h2>
  <div class="charts-grid">
  {% for name, img in charts.distributions %}
    <div class="chart"><img src="data:image/png;base64,{{ img }}" alt="{{ name }}"></div>
  {% endfor %}
  </div>
</section>
{% endif %}

<section>
  <h2>Column summaries</h2>
  <table>
    <thead>
      <tr><th>Column</th><th>Dtype</th><th>Non-null</th><th>Null %</th><th>Unique</th><th>Sample</th></tr>
    </thead>
    <tbody>
    {% for c in summary.column_summaries %}
      <tr>
        <td>{{ c.name }}</td><td>{{ c.dtype }}</td><td>{{ c.non_null }}</td>
        <td>{{ c.null_pct }}%</td><td>{{ c.unique }}</td>
        <td>{{ c.sample_values|join(", ") }}</td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
</section>

</main>
</body>
</html>
"""


def render_html(
    dataset_name: str,
    summary: DatasetSummary,
    anomaly: AnomalyReport,
    issues: list[QualityIssue],
    charts: dict,
    output_path: str | Path,
) -> Path:
    """Render and save the HTML report. Returns the output path."""
    env = Environment(autoescape=select_autoescape(["html"]))
    template = env.from_string(_TEMPLATE)

    html = template.render(
        dataset_name=dataset_name,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        version=__version__,
        summary=summary,
        anomaly=anomaly,
        issues=issues,
        charts=charts,
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out