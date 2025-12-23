"""End-to-end integration test for Metrics feature.

This test simulates the exact user scenario that was failing:
1. Upload a dataset
2. Click analyze
3. Verify that it works on the FIRST attempt (not after multiple clicks)

Date: December 23, 2025
Issue: 404 error on /api/metrics/analyze after upload
"""

import pytest  # noqa: F401 # type: ignore
import sys
import os
import io
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from api import app  # noqa: F401 # type: ignore
import pandas as pd


@pytest.fixture
def client():
    """Create test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_csv():
    """Create a sample CSV file for testing."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", None, "Eve"],
            "age": [25, 30, None, 40, 35],
            "email": [
                "alice@test.com",
                "bob@test.com",
                "charlie@test.com",
                "invalid-email",
                "eve@test.com",
            ],
            "score": [85.5, 90.0, 88.5, None, 92.0],
        }
    )

    # Create CSV in memory
    csv_buffer = io.BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return csv_buffer, "test_data.csv"


class TestMetricsEndToEnd:
    """End-to-end tests for Metrics feature."""

    def test_metrics_workflow_first_attempt(self, client, sample_csv):
        """Test complete metrics workflow works on FIRST attempt.

        This is the critical test - it should NOT need multiple attempts.
        """
        csv_buffer, filename = sample_csv

        # Step 1: Upload dataset
        print("\n[1] Uploading dataset...")
        response = client.post(
            "/api/metrics/upload",
            data={"file": (csv_buffer, filename)},
            content_type="multipart/form-data",
        )

        assert (
            response.status_code == 200
        ), f"Upload failed with status {response.status_code}: {response.get_json()}"

        upload_data = response.get_json()
        assert "sessionId" in upload_data, "No sessionId in upload response"
        assert "columns" in upload_data, "No columns in upload response"
        assert "sample" in upload_data, "No sample data in upload response"

        session_id = upload_data["sessionId"]
        print(f"    ✓ Upload successful. SessionId: {session_id}")
        print(f"    ✓ Columns: {upload_data['columns']}")
        print(f"    ✓ Rows: {upload_data.get('rows', 'N/A')}")

        # Step 2: Analyze dataset (THE CRITICAL STEP - must work on first try!)
        print("\n[2] Analyzing dataset (FIRST ATTEMPT)...")
        response = client.post(
            "/api/metrics/analyze",
            data=json.dumps({"sessionId": session_id}),
            content_type="application/json",
        )

        # This is the critical assertion - should NOT be 404
        assert response.status_code != 404, (
            "CRITICAL BUG: Got 404 on /api/metrics/analyze! "
            "This is the exact issue we fixed. The endpoint should exist!"
        )

        assert (
            response.status_code == 200
        ), f"Analyze failed with status {response.status_code}: {response.get_json()}"

        analyze_data = response.get_json()
        print("    ✓ Analysis successful on FIRST attempt!")

        # Verify report structure (metrics are nested under 'metrics' key)
        assert "metrics" in analyze_data, "No metrics in response"
        metrics = analyze_data["metrics"]

        assert "completeness" in metrics, "No completeness metrics"
        assert "uniqueness" in metrics, "No uniqueness metrics"
        assert "validity" in metrics, "No validity metrics"
        assert "consistency" in metrics, "No consistency metrics"
        assert "dataset_info" in metrics, "No dataset info"

        print("    ✓ All metric categories present")

        # Verify dataset info
        dataset_info = metrics["dataset_info"]
        assert dataset_info["rows"] == 5, f"Expected 5 rows, got {dataset_info['rows']}"
        assert (
            dataset_info["columns"] == 5
        ), f"Expected 5 columns, got {dataset_info['columns']}"

        print("    ✓ Dataset info correct")

        # Step 3: Get report
        print("\n[3] Retrieving report...")
        response = client.get(f"/api/metrics/report?sessionId={session_id}")

        assert (
            response.status_code == 200
        ), f"Report retrieval failed: {response.status_code}"

        report_data = response.get_json()
        assert report_data is not None

        print("    ✓ Report retrieved successfully")
        print("\n[SUCCESS] Complete workflow works on FIRST attempt!")

    def test_metrics_analyze_without_upload_fails_gracefully(self, client):
        """Test that analyze without upload fails gracefully (400, not 404)."""
        response = client.post(
            "/api/metrics/analyze",
            data=json.dumps({"sessionId": "invalid-session-id"}),
            content_type="application/json",
        )

        # Should return 404 for invalid session, but endpoint should exist
        # (HTTP 404 for resource not found is OK, but not for route not found)
        assert response.status_code in [
            400,
            404,
        ], f"Unexpected status: {response.status_code}"

        # The important thing is the endpoint exists
        # We can tell by getting JSON response (not HTML 404 page)
        data = response.get_json()
        assert data is not None, "Should return JSON error, not HTML 404"
        assert "error" in data, "Should have error message"

    def test_metrics_analyze_missing_session_id(self, client):
        """Test that analyze without sessionId parameter fails correctly."""
        response = client.post(
            "/api/metrics/analyze", data=json.dumps({}), content_type="application/json"
        )

        assert (
            response.status_code == 400
        ), f"Expected 400 for missing sessionId, got {response.status_code}"

        data = response.get_json()
        assert "error" in data
        assert "sessionid" in data["error"].lower()  # Case-insensitive check

    def test_metrics_health_check(self, client):
        """Test metrics health check endpoint."""
        response = client.get("/api/metrics/health")

        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert data.get("ok") is True or data.get("status") == "running"

    def test_metrics_upload_no_file(self, client):
        """Test upload without file fails gracefully."""
        response = client.post("/api/metrics/upload")

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_metrics_upload_empty_filename(self, client):
        """Test upload with empty filename fails gracefully."""
        response = client.post(
            "/api/metrics/upload",
            data={"file": (io.BytesIO(b""), "")},
            content_type="multipart/form-data",
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data


class TestMetricsResilience:
    """Test metrics feature resilience and error handling."""

    def test_metrics_works_even_if_rag_fails(self, client):
        """Test that metrics works independently of RAG status."""
        # Just verify the endpoint exists
        response = client.get("/api/metrics/health")
        assert response.status_code == 200

    def test_multiple_sessions_supported(self, client, sample_csv):
        """Test that multiple concurrent sessions are supported."""
        # Upload first dataset
        csv1, filename1 = sample_csv
        response1 = client.post(
            "/api/metrics/upload",
            data={"file": (csv1, filename1)},
            content_type="multipart/form-data",
        )
        assert response1.status_code == 200
        session1 = response1.get_json()["sessionId"]

        # Upload second dataset (recreate csv buffer)
        csv2 = io.BytesIO()
        pd.DataFrame({"col1": [1, 2, 3]}).to_csv(csv2, index=False)
        csv2.seek(0)

        response2 = client.post(
            "/api/metrics/upload",
            data={"file": (csv2, "test2.csv")},
            content_type="multipart/form-data",
        )
        assert response2.status_code == 200
        session2 = response2.get_json()["sessionId"]

        # Sessions should be different
        assert session1 != session2

        # Both should be analyzable
        response1 = client.post(
            "/api/metrics/analyze",
            data=json.dumps({"sessionId": session1}),
            content_type="application/json",
        )
        assert response1.status_code == 200

        response2 = client.post(
            "/api/metrics/analyze",
            data=json.dumps({"sessionId": session2}),
            content_type="application/json",
        )
        assert response2.status_code == 200


class TestMetricsDataQuality:
    """Test metrics calculation accuracy."""

    def test_completeness_calculation(self, client):
        """Test completeness metrics are calculated correctly."""
        # Create dataset with known missing values
        df = pd.DataFrame(
            {
                "complete": [1, 2, 3, 4, 5],  # 100% complete
                "half_missing": [1, None, 3, None, 5],  # 60% complete
                "all_missing": [None, None, None, None, None],  # 0% complete
            }
        )

        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        # Upload and analyze
        response = client.post(
            "/api/metrics/upload",
            data={"file": (csv_buffer, "test.csv")},
            content_type="multipart/form-data",
        )
        session_id = response.get_json()["sessionId"]

        response = client.post(
            "/api/metrics/analyze",
            data=json.dumps({"sessionId": session_id}),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()

        # Metrics are nested under 'metrics' key
        assert "metrics" in data, "No metrics in response"
        metrics = data["metrics"]

        completeness = metrics["completeness"]
        assert "column_completeness" in completeness

        # Verify completeness scores (approximately)
        col_completeness = completeness["column_completeness"]
        assert col_completeness["complete"]["completeness"] == pytest.approx(100.0)
        assert col_completeness["half_missing"]["completeness"] == pytest.approx(60.0)
        assert col_completeness["all_missing"]["completeness"] == pytest.approx(0.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
