"""
Production SLA tests — executed against the live Render deployment.

These tests ONLY run when the environment variable RUN_PRODUCTION_TESTS=true
is set.  In CI or local runs without that variable they are silently skipped.

Run with:
  RUN_PRODUCTION_TESTS=true pytest tests/backend/performance/test_sla_production.py -v
"""

import os
import sys
import io
import base64
import time
import concurrent.futures

import pytest
import requests
import pandas as pd

# Ensure project root is on the path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
)

_PRODUCTION_ENABLED = os.environ.get("RUN_PRODUCTION_TESTS", "").lower() == "true"
_BASE_URL = os.environ.get(
    "LOAD_TEST_HOST", "https://dataforgetest-backend.onrender.com"
)

_SKIP_REASON = "Skipped: RUN_PRODUCTION_TESTS not set"


def _skip_if_not_prod():
    if not _PRODUCTION_ENABLED:
        pytest.skip(_SKIP_REASON)


def _small_csv_b64(rows: int = 50) -> str:
    df = pd.DataFrame({
        "id": range(1, rows + 1),
        "name": [f"item_{i}" for i in range(1, rows + 1)],
        "score": [float(i) * 0.5 for i in range(1, rows + 1)],
    })
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return base64.b64encode(buf.getvalue().encode()).decode()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_production_cold_start_health():
    """GET / — accept up to 45 s for cold start on Render free tier."""
    _skip_if_not_prod()

    url = f"{_BASE_URL}/"
    start = time.monotonic()
    try:
        resp = requests.get(url, timeout=60)
        elapsed = time.monotonic() - start
    except requests.exceptions.Timeout:
        pytest.fail(f"[PERFORMANCE] Cold start timed out after 60s")

    assert elapsed <= 45, (
        f"[PERFORMANCE] Cold start excedeu 45s: {elapsed:.1f}s"
    )
    assert resp.status_code == 200, f"Unexpected status: {resp.status_code}"
    body = resp.json()
    assert body.get("status") == "Backend is running", (
        f"Unexpected body: {body}"
    )


def test_production_warm_health_response_time():
    """GET / x 5 — each warm request must respond < 2 s."""
    _skip_if_not_prod()

    url = f"{_BASE_URL}/"
    # Warm-up request (may include residual cold-start latency)
    requests.get(url, timeout=60)

    times = []
    for _ in range(5):
        t0 = time.monotonic()
        resp = requests.get(url, timeout=10)
        t1 = time.monotonic()
        assert resp.status_code == 200
        times.append(t1 - t0)

    mean_t = sum(times) / len(times)
    sorted_times = sorted(times)
    p95 = sorted_times[int(len(sorted_times) * 0.95)]

    assert mean_t < 2.0, (
        f"[SLA VIOLATION] Warm GET / mean={mean_t*1000:.0f}ms exceeds 2000ms SLA"
    )
    # p95 for 5 samples is effectively the max
    assert p95 < 2.0, (
        f"[SLA VIOLATION] Warm GET / p95={p95*1000:.0f}ms exceeds 2000ms SLA"
    )


def test_production_metrics_endpoint_sla():
    """POST /api/metrics/analyze with 50-row CSV — SLA: < 15 s."""
    _skip_if_not_prod()

    url = f"{_BASE_URL}/api/metrics/analyze"
    payload = {"file_content": _small_csv_b64(50), "filename": "sla_test.csv"}

    start = time.monotonic()
    resp = requests.post(url, json=payload, timeout=20)
    elapsed = time.monotonic() - start

    assert resp.status_code not in (500,), (
        f"Server error {resp.status_code}: {resp.text}"
    )
    assert elapsed < 15.0, (
        f"[SLA VIOLATION] POST /api/metrics/analyze took {elapsed:.1f}s (limit 15s)"
    )


def test_production_ask_endpoint_timeout():
    """POST /ask — must respond within 30 s with dsl/pyspark_code fields."""
    _skip_if_not_prod()

    url = f"{_BASE_URL}/ask"
    payload = {
        "answers": {
            "dataset_name": "sales",
            "source_path": "/data/sales.csv",
            "format": "csv",
        }
    }

    start = time.monotonic()
    try:
        resp = requests.post(url, json=payload, timeout=30)
        elapsed = time.monotonic() - start
    except requests.exceptions.Timeout:
        pytest.fail("[PERFORMANCE] POST /ask timed out after 30s")

    assert elapsed < 30.0, (
        f"[SLA VIOLATION] POST /ask took {elapsed:.1f}s (limit 30s)"
    )
    assert resp.status_code == 200, f"Unexpected status: {resp.status_code}"
    body = resp.json()
    assert "dsl" in body or "pyspark_code" in body, (
        f"Response missing 'dsl'/'pyspark_code': {body}"
    )


def test_production_concurrent_users_simulation():
    """5 concurrent GET / requests — all must complete < 5 s, 100% success rate."""
    _skip_if_not_prod()

    # Ensure server is warm
    requests.get(f"{_BASE_URL}/", timeout=60)

    url = f"{_BASE_URL}/"

    def fetch(_):
        t0 = time.monotonic()
        r = requests.get(url, timeout=10)
        return r.status_code, time.monotonic() - t0

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(fetch, range(5)))

    statuses = [s for s, _ in results]
    times = [t for _, t in results]

    success_count = sum(1 for s in statuses if s == 200)
    assert success_count == 5, (
        f"[FAILURE] Only {success_count}/5 requests succeeded: {statuses}"
    )
    assert max(times) < 5.0, (
        f"[SLA VIOLATION] Slowest concurrent request: {max(times):.2f}s (limit 5s)"
    )
