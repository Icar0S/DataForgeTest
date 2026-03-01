from __future__ import annotations

import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass
class StageSummary:
    """Aggregate information extracted from a single test phase."""

    name: str
    artifact: Path
    tests: int = 0
    failures: int = 0
    errors: int = 0
    skipped: int = 0
    time_seconds: float | None = None
    status: str = "MISSING"
    details: list[str] = field(default_factory=list)

    @property
    def total_failed(self) -> int:
        return self.failures + self.errors


def format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "N/A"
    if seconds < 60:
        return f"{seconds:.2f}s"
    minutes, rem = divmod(seconds, 60)
    return f"{int(minutes)}m {rem:.1f}s"


def parse_junit_stage(name: str, path: Path) -> StageSummary:
    summary = StageSummary(name=name, artifact=path)
    if not path.exists():
        return summary

    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        summary.status = "ERROR"
        summary.details.append(f"Falha ao parsear XML: {exc}")
        return summary

    root = tree.getroot()
    suites: Iterable[ET.Element]
    if root.tag == "testsuites":
        suites = root.findall("testsuite")
    elif root.tag == "testsuite":
        suites = [root]
    else:
        suites = root.findall(".//testsuite")

    total_time = 0.0
    for suite in suites:
        summary.tests += int(suite.get("tests", "0"))
        summary.failures += int(suite.get("failures", "0"))
        summary.errors += int(suite.get("errors", "0"))
        summary.skipped += int(suite.get("skipped", "0"))
        total_time += float(suite.get("time", "0") or 0)

    # Capture individual failing testcases for quick reference
    for testcase in root.findall(".//testcase"):
        classname = testcase.get("classname", "")
        testname = testcase.get("name", "")
        test_label = f"{classname}.{testname}".strip(".")
        for child in testcase:
            if child.tag in {"failure", "error"}:
                message = child.get("message") or (child.text or "").strip()
                if message:
                    entry = f"{test_label}: {message}"
                else:
                    entry = test_label
                summary.details.append(entry[:500])

    summary.time_seconds = total_time if total_time > 0 else None
    summary.status = "PASS" if summary.total_failed == 0 else "FAIL"
    return summary


def parse_benchmarks(path: Path) -> list[dict[str, str | float | None]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError as exc:
        return [{"name": "Falha ao parsear benchmark.json", "mean": str(exc)}]

    entries: list[dict[str, str | float | None]] = []
    benchmarks = payload.get("benchmarks") if isinstance(payload, dict) else payload
    if not isinstance(benchmarks, list):
        return entries

    for bench in benchmarks:
        name = bench.get("name", "benchmark")
        stats = bench.get("stats", {}) if isinstance(bench, dict) else {}
        mean = stats.get("mean")
        rounds = bench.get("rounds") or stats.get("rounds")
        entries.append(
            {
                "name": name,
                "mean": mean,
                "rounds": rounds,
                "iterations": bench.get("iterations"),
            }
        )
    return entries


def parse_coverage_index(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="ignore")
    metrics = {}
    patterns = {
        "Statements": r"Statements[^0-9%]*?(\d+(?:\.\d+)?)%",
        "Branches": r"Branches[^0-9%]*?(\d+(?:\.\d+)?)%",
        "Functions": r"Functions[^0-9%]*?(\d+(?:\.\d+)?)%",
        "Lines": r"Lines[^0-9%]*?(\d+(?:\.\d+)?)%",
    }
    for label, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metrics[label] = float(match.group(1))
    return metrics


def collect_artifacts(
    results_dir: Path, timestamp: str, report_path: Path
) -> list[tuple[str, float]]:
    candidates = [
        results_dir / "backend" / "unit-results.xml",
        results_dir / "backend" / "api-results.xml",
        results_dir / "backend" / "security-results.xml",
        results_dir / "backend" / "integration-results.xml",
        results_dir / "backend" / "e2e-results.xml",
        results_dir / "backend" / "unit-report.html",
        results_dir / "performance" / "benchmark.json",
        results_dir / "frontend" / "coverage" / "coverage-summary.json",
        results_dir / "frontend" / "coverage" / "index.html",
        results_dir / "frontend" / "coverage" / "lcov-report" / "index.html",
        results_dir / f"pipeline_{timestamp}.log",
        report_path,
    ]
    artifacts: list[tuple[str, float]] = []
    base = results_dir.parent
    for candidate in candidates:
        if candidate.exists():
            rel = candidate.relative_to(base)
            artifacts.append((rel.as_posix(), candidate.stat().st_size / 1024.0))
    return artifacts


def build_stage_table(stage_results: list[StageSummary]) -> str:
    rows = []
    for stage in stage_results:
        rows.append(
            """
      <tr>
        <td>{name}</td>
        <td>{status}</td>
        <td>{tests}</td>
        <td>{fail}</td>
        <td>{skipped}</td>
        <td>{duration}</td>
      </tr>
      """.format(
                name=html.escape(stage.name),
                status=stage.status,
                tests=stage.tests if stage.tests else "-",
                fail=stage.total_failed if stage.tests else "-",
                skipped=stage.skipped if stage.skipped else "-",
                duration=format_duration(stage.time_seconds),
            )
        )
    return "".join(rows)


def build_failure_section(stage_results: list[StageSummary]) -> str:
    blocks = []
    for stage in stage_results:
        if not stage.details:
            continue
        items = "".join(f"<li>{html.escape(item)}</li>" for item in stage.details)
        blocks.append(
            f"<div class='card'><h3>{html.escape(stage.name)}</h3><ul>{items}</ul></div>"
        )
    return "".join(blocks) or "<p>Nenhuma falha registrada.</p>"


def build_performance_table(entries: list[dict[str, str | float]]) -> str:
    if not entries:
        return "<p>Nenhum benchmark encontrado.</p>"
    rows = []
    for entry in entries:
        mean = entry.get("mean")
        if isinstance(mean, (int, float)):
            mean_str = f"{mean*1000:.3f} ms" if mean < 1 else f"{mean:.4f} s"
        else:
            mean_str = str(mean) if mean is not None else "-"
        rows.append(
            """
      <tr>
        <td>{name}</td>
        <td>{mean}</td>
        <td>{rounds}</td>
        <td>{iters}</td>
      </tr>
      """.format(
                name=html.escape(str(entry.get("name", "benchmark"))),
                mean=mean_str,
                rounds=entry.get("rounds", "-"),
                iters=entry.get("iterations", "-"),
            )
        )
    header = "<tr><th>Benchmark</th><th>Tempo Medio</th><th>Rodadas</th><th>Iteracoes</th></tr>"
    return f"<table>{header}{''.join(rows)}</table>"


def build_coverage_list(metrics: dict[str, float]) -> str:
    if not metrics:
        return "<p>Relatorio de cobertura nao encontrado.</p>"
    items = "".join(
        f"<li>{html.escape(label)}: {value:.2f}%</li>"
        for label, value in metrics.items()
    )
    return f"<ul>{items}</ul>"


def build_html(
    *,
    timestamp: str,
    generated_at: str,
    stage_results: list[StageSummary],
    coverage_metrics: dict[str, float],
    benchmark_entries: list[dict[str, str | float]],
    log_text: str,
    artifacts: list[tuple[str, float]],
    backend_pass_count: int,
    backend_fail_count: int,
    frontend_pass_count: int,
    frontend_fail_count: int,
) -> str:
    total_time = sum(
        stage.time_seconds or 0 for stage in stage_results if stage.time_seconds
    )
    stage_table = build_stage_table(stage_results)
    failure_section = build_failure_section(stage_results)
    performance_table = build_performance_table(benchmark_entries)
    coverage_list = build_coverage_list(coverage_metrics)
    escaped_log = html.escape(log_text)

    if artifacts:
        artifact_rows = "".join(
            f"<tr><td><a href='{html.escape(path)}'>{html.escape(path)}</a></td><td>{size:.1f} KB</td></tr>"
            for path, size in artifacts
        )
    else:
        artifact_rows = "<tr><td colspan='2'>Nenhum artefato encontrado.</td></tr>"

    total_time_str = format_duration(total_time) if total_time else "N/A"

    return f"""
<!DOCTYPE html>
<html lang='pt-BR'>
<head>
  <meta charset='utf-8'>
  <title>DataForgeTest - Relatorio Consolidado {html.escape(timestamp)}</title>
  <style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 2rem; background: #f5f5f5; color: #1f1f1f; }}
  h1 {{ margin-bottom: 0.25rem; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; background: #fff; }}
  th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
  th {{ background: #f0f0f0; }}
  pre {{ background: #111; color: #0f0; padding: 1rem; overflow-x: auto; max-height: 500px; }}
  .card {{ background: #fff; padding: 1rem 1.5rem; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); margin-bottom: 1.5rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; }}
  .metric-card {{ background: #fff; padding: 1rem; border-radius: 8px; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.08); }}
  .metric-card h3 {{ margin: 0; font-size: 0.95rem; color: #555; }}
  .metric-card p {{ margin: 0.5rem 0 0; font-size: 1.3rem; font-weight: bold; }}
  </style>
</head>
<body>
  <div class='card'>
  <h1>DataForgeTest - Relatorio Consolidado</h1>
  <p>Timestamp: {html.escape(timestamp)} | Gerado em: {generated_at}</p>
  <div class='grid'>
    <div class='metric-card'>
    <h3>Backend PASS</h3>
        <p>{backend_pass_count}</p>
    </div>
    <div class='metric-card'>
    <h3>Backend FAIL</h3>
        <p>{backend_fail_count}</p>
    </div>
    <div class='metric-card'>
    <h3>Frontend PASS</h3>
        <p>{frontend_pass_count}</p>
    </div>
    <div class='metric-card'>
    <h3>Frontend FAIL</h3>
        <p>{frontend_fail_count}</p>
    </div>
    <div class='metric-card'>
    <h3>Tempo Total</h3>
    <p>{total_time_str}</p>
    </div>
  </div>
  </div>

  <div class='card'>
  <h2>Tempos por Fase</h2>
  <table>
    <tr><th>Fase</th><th>Status</th><th>Testes</th><th>Falhas</th><th>Skips</th><th>Duração</th></tr>
    {stage_table}
  </table>
  </div>

  <div class='card'>
  <h2>Resumo de Falhas</h2>
  {failure_section}
  </div>

  <div class='card'>
  <h2>Benchmarks de Performance</h2>
  {performance_table}
  </div>

  <div class='card'>
  <h2>Cobertura Frontend</h2>
  {coverage_list}
  </div>

  <div class='card'>
  <h2>Artefatos</h2>
  <table>
    <tr><th>Arquivo</th><th>Tamanho</th></tr>
    {artifact_rows}
  </table>
  </div>

  <div class='card'>
  <h2>Log Completo</h2>
  <pre>{escaped_log}</pre>
  </div>
</body>
</html>
"""


def main() -> int:
    if len(sys.argv) < 9:
        print("[ERROR] Missing arguments for pipeline report generation.")
        return 1

    log_path = Path(sys.argv[1])
    results_dir = Path(sys.argv[2])
    html_path = Path(sys.argv[3])
    backend_pass = int(sys.argv[4])
    backend_fail = int(sys.argv[5])
    frontend_pass = int(sys.argv[6])
    frontend_fail = int(sys.argv[7])
    timestamp = sys.argv[8]

    log_text = (
        "Arquivo de log nao encontrado."
        if not log_path.exists()
        else log_path.read_text(encoding="utf-8", errors="ignore")
    )

    stage_descriptors = [
        ("Backend - Unit", results_dir / "backend" / "unit-results.xml"),
        ("Backend - API", results_dir / "backend" / "api-results.xml"),
        ("Backend - Security", results_dir / "backend" / "security-results.xml"),
        ("Backend - Integration", results_dir / "backend" / "integration-results.xml"),
        ("Backend - E2E", results_dir / "backend" / "e2e-results.xml"),
    ]
    stage_results = [parse_junit_stage(name, path) for name, path in stage_descriptors]

    benchmark_path = results_dir / "performance" / "benchmark.json"
    benchmark_entries_raw = parse_benchmarks(benchmark_path)
    benchmark_entries = [
        {k: v for k, v in entry.items() if v is not None}
        for entry in benchmark_entries_raw
    ]
    performance_stage = StageSummary(
        name="Backend - Performance",
        artifact=benchmark_path,
        tests=len(benchmark_entries),
        status="PASS" if benchmark_entries else "MISSING",
        details=[],
    )
    stage_results.append(performance_stage)

    coverage_path = results_dir / "frontend" / "coverage" / "index.html"
    coverage_metrics = parse_coverage_index(coverage_path)
    coverage_stage = StageSummary(
        name="Frontend - Coverage",
        artifact=coverage_path,
        tests=0,
        status="PASS" if coverage_metrics else "MISSING",
    )
    stage_results.append(coverage_stage)

    artifacts = collect_artifacts(results_dir, timestamp, html_path)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = build_html(
        timestamp=timestamp,
        generated_at=generated_at,
        backend_pass_count=backend_pass,
        backend_fail_count=backend_fail,
        frontend_pass_count=frontend_pass,
        frontend_fail_count=frontend_fail,
        stage_results=stage_results,
        coverage_metrics=coverage_metrics,
        benchmark_entries=benchmark_entries,
        log_text=log_text,
        artifacts=artifacts,
    )

    html_path.write_text(html_content, encoding="utf-8")
    print(f"[OK] Relatorio consolidado salvo em: {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
if __name__ == "__main__":
    raise SystemExit(main())
