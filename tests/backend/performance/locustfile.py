"""
Locust load test file for DataForgeTest backend.

Usage:
  locust -f tests/backend/performance/locustfile.py \\
         --host=https://dataforgetest-backend.onrender.com
"""

import os
import base64
import io
import json
import pandas as pd
from locust import HttpUser, task, between


def _make_csv_b64(rows: int = 50) -> str:
    """Return a base64-encoded CSV string with *rows* rows."""
    df = pd.DataFrame({
        "id": range(1, rows + 1),
        "name": [f"item_{i}" for i in range(1, rows + 1)],
        "score": [float(i) * 0.5 for i in range(1, rows + 1)],
    })
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return base64.b64encode(buf.getvalue().encode()).decode()


_CSV_B64 = _make_csv_b64(50)

_DEFAULT_HOST = os.environ.get(
    "LOAD_TEST_HOST", "https://dataforgetest-backend.onrender.com"
)


class DataForgeBasicUser(HttpUser):
    """Simulates light usage: health checks only. Weight=5 (majority of users)."""

    weight = 5
    host = _DEFAULT_HOST
    wait_time = between(2, 5)

    def on_start(self):
        """Verify backend is reachable before running tasks."""
        with self.client.get("/", catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"[on_start] Health check failed: HTTP {resp.status_code}")
            else:
                resp.success()

    @task(3)
    def health_check(self):
        """GET / — root health check."""
        with self.client.get("/", catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"[health_check] Unexpected status: {resp.status_code}")
            elif "status" not in resp.text:
                resp.failure("[health_check] Response missing 'status' field")
            else:
                resp.success()

    @task(2)
    def metrics_health(self):
        """GET /api/metrics/health — metrics module health."""
        with self.client.get("/api/metrics/health", catch_response=True) as resp:
            if resp.status_code not in (200, 404):
                resp.failure(f"[metrics_health] Unexpected status: {resp.status_code}")
            else:
                resp.success()


class DataForgeMetricsUser(HttpUser):
    """Simulates dataset analysis workflows. Weight=3."""

    weight = 3
    host = _DEFAULT_HOST
    wait_time = between(5, 15)

    def on_start(self):
        """Verify backend is reachable before running tasks."""
        with self.client.get("/", catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"[on_start] Health check failed: HTTP {resp.status_code}")
            else:
                resp.success()

    @task(2)
    def analyze_metrics(self):
        """POST /api/metrics/analyze with a small CSV payload."""
        payload = {"file_content": _CSV_B64, "filename": "test.csv"}
        with self.client.post(
            "/api/metrics/analyze",
            json=payload,
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 400, 404, 422):
                resp.failure(
                    f"[analyze_metrics] Unexpected status: {resp.status_code}"
                )
            else:
                resp.success()

    @task(1)
    def inspect_dataset(self):
        """POST /api/dataset_inspector/inspect with a simple dataset."""
        payload = {"file_content": _CSV_B64, "filename": "test.csv"}
        with self.client.post(
            "/api/dataset_inspector/inspect",
            json=payload,
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 400, 404, 422):
                resp.failure(
                    f"[inspect_dataset] Unexpected status: {resp.status_code}"
                )
            else:
                resp.success()


class DataForgeLLMUser(HttpUser):
    """Simulates LLM / RAG usage. Weight=1 (few power users)."""

    weight = 1
    host = _DEFAULT_HOST
    wait_time = between(10, 30)

    def on_start(self):
        """Verify backend is reachable before running tasks."""
        with self.client.get("/", catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"[on_start] Health check failed: HTTP {resp.status_code}")
            else:
                resp.success()

    @task(2)
    def ask_pyspark(self):
        """POST /ask — generate PySpark code via LLM."""
        payload = {
            "answers": {
                "dataset_name": "sales",
                "source_path": "/data/sales.csv",
                "format": "csv",
            }
        }
        with self.client.post(
            "/ask",
            json=payload,
            catch_response=True,
            timeout=60,
        ) as resp:
            if resp.status_code not in (200, 400, 500):
                resp.failure(f"[ask_pyspark] Unexpected status: {resp.status_code}")
            elif resp.status_code == 200:
                try:
                    body = resp.json()
                    if "dsl" not in body and "pyspark_code" not in body:
                        resp.failure("[ask_pyspark] Response missing 'dsl'/'pyspark_code'")
                    else:
                        resp.success()
                except Exception:
                    resp.failure("[ask_pyspark] Could not parse JSON response")
            else:
                resp.success()

    @task(1)
    def rag_chat(self):
        """POST /api/rag/chat — RAG question answering."""
        payload = {"message": "What is data quality?"}
        with self.client.post(
            "/api/rag/chat",
            json=payload,
            catch_response=True,
            timeout=45,
        ) as resp:
            if resp.status_code not in (200, 400, 404, 500):
                resp.failure(f"[rag_chat] Unexpected status: {resp.status_code}")
            else:
                resp.success()
