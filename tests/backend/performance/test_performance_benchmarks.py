"""
Local performance benchmarks using pytest-benchmark.

These tests use the Flask test client (no real network calls) and measure
raw processing time against defined SLAs.

Run with:
  pytest tests/backend/performance/test_performance_benchmarks.py -v \\
         --benchmark-json=results/benchmark.json
"""

import os
import sys
import io
import json
import concurrent.futures

import pytest
import pandas as pd

# Ensure project root is on the path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _csv_bytes(rows: int = 100, cols: int = 3) -> bytes:
    """Generate a simple CSV as bytes."""
    df = pd.DataFrame({
        "id": range(1, rows + 1),
        "name": [f"item_{i}" for i in range(1, rows + 1)],
        "score": [float(i) * 0.5 for i in range(1, rows + 1)],
    })
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


def _csv_bytes_mixed(rows: int = 500) -> bytes:
    """Generate a mixed-type CSV as bytes."""
    df = pd.DataFrame({
        "id": range(1, rows + 1),
        "name": [f"record_{i}" for i in range(1, rows + 1)],
        "value": [float(i) * 1.1 for i in range(1, rows + 1)],
        "date": [f"2024-01-{(i % 28) + 1:02d}" for i in range(rows)],
        "active": [i % 2 == 0 for i in range(1, rows + 1)],
    })
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Benchmarks
# ---------------------------------------------------------------------------

def test_benchmark_health_endpoint(benchmark, client):
    """Benchmark GET / — SLA: mean < 50 ms."""
    def call():
        return client.get("/")

    result = benchmark(call)

    assert result.status_code == 200

    stats = benchmark.stats
    assert stats["mean"] < 0.050, (
        f"[SLA VIOLATION] GET / mean={stats['mean']*1000:.1f}ms exceeds 50ms SLA"
    )


def test_benchmark_ask_endpoint_no_llm(benchmark, client):
    """Benchmark POST /ask with no LLM configured — SLA: mean < 200 ms."""
    os.environ.pop("LLM_PROVIDER", None)

    payload = {"answers": {}}

    def call():
        return client.post("/ask", json=payload)

    result = benchmark(call)

    # Accept any non-500 response (LLM may be absent)
    assert result.status_code != 500, "Flask returned an unhandled 500 error"

    stats = benchmark.stats
    assert stats["mean"] < 0.200, (
        f"[SLA VIOLATION] POST /ask mean={stats['mean']*1000:.1f}ms exceeds 200ms SLA"
    )


def test_benchmark_metrics_analyze(benchmark, client, sample_csv_100):
    """Benchmark POST /api/metrics/analyze with 100-row CSV — SLA: mean < 2 s."""
    import base64
    csv_b64 = base64.b64encode(sample_csv_100).decode()
    payload = {"file_content": csv_b64, "filename": "bench.csv"}

    def call():
        return client.post("/api/metrics/analyze", json=payload)

    result = benchmark(call)

    assert result.status_code not in (500,), (
        f"Unexpected 500 on /api/metrics/analyze: {result.data}"
    )

    stats = benchmark.stats
    assert stats["mean"] < 2.000, (
        f"[SLA VIOLATION] POST /api/metrics/analyze mean={stats['mean']*1000:.0f}ms exceeds 2000ms SLA"
    )


def test_benchmark_dataset_inspector(benchmark, client, sample_csv_500):
    """Benchmark POST /api/dataset_inspector/inspect with 500-row dataset — SLA: mean < 3 s."""
    import base64
    csv_b64 = base64.b64encode(sample_csv_500).decode()
    payload = {"file_content": csv_b64, "filename": "bench500.csv"}

    def call():
        return client.post("/api/dataset_inspector/inspect", json=payload)

    result = benchmark(call)

    assert result.status_code not in (500,), (
        f"Unexpected 500 on /api/dataset_inspector/inspect: {result.data}"
    )

    stats = benchmark.stats
    assert stats["mean"] < 3.000, (
        f"[SLA VIOLATION] POST /api/dataset_inspector/inspect mean={stats['mean']*1000:.0f}ms exceeds 3000ms SLA"
    )


def test_benchmark_synthetic_generate_small(benchmark, client):
    """Benchmark POST /api/synthetic/generate with 100-row schema — SLA: mean < 1 s."""
    os.environ.pop("LLM_PROVIDER", None)

    payload = {
        "schema": [
            {"name": "id", "type": "int"},
            {"name": "name", "type": "string"},
            {"name": "score", "type": "float"},
        ],
        "num_rows": 100,
    }

    def call():
        return client.post("/api/synthetic/generate", json=payload)

    result = benchmark(call)

    assert result.status_code not in (500,), (
        f"Unexpected 500 on /api/synthetic/generate: {result.data}"
    )

    stats = benchmark.stats
    assert stats["mean"] < 1.000, (
        f"[SLA VIOLATION] POST /api/synthetic/generate mean={stats['mean']*1000:.0f}ms exceeds 1000ms SLA"
    )


def test_benchmark_rag_search(benchmark, client):
    """Benchmark POST /api/rag/chat with simple query — SLA: mean < 500 ms."""
    payload = {"message": "data quality"}

    def call():
        return client.post("/api/rag/chat", json=payload)

    result = benchmark(call)

    assert result.status_code not in (500,), (
        f"Unexpected 500 on /api/rag/chat: {result.data}"
    )

    stats = benchmark.stats
    assert stats["mean"] < 0.500, (
        f"[SLA VIOLATION] POST /api/rag/chat mean={stats['mean']*1000:.0f}ms exceeds 500ms SLA"
    )


def test_benchmark_concurrent_requests(client, sample_csv_100):
    """Send 10 concurrent requests to /api/metrics/analyze — all must complete < 10 s, no 500s."""
    import base64
    import time

    csv_b64 = base64.b64encode(sample_csv_100).decode()
    payload = {"file_content": csv_b64, "filename": "concurrent_bench.csv"}

    def single_request(_):
        return client.post("/api/metrics/analyze", json=payload)

    start = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        futures = [pool.submit(single_request, i) for i in range(10)]
        responses = [f.result() for f in concurrent.futures.as_completed(futures)]
    elapsed = time.monotonic() - start

    assert elapsed < 10.0, (
        f"[SLA VIOLATION] 10 concurrent requests took {elapsed:.2f}s (limit 10s)"
    )

    status_codes = [r.status_code for r in responses]
    assert 500 not in status_codes, (
        f"[FAILURE] Some requests returned 500: {status_codes}"
    )
