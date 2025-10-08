"""Tests for Metrics feature."""

import pytest
import json
import tempfile
from pathlib import Path
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from metrics.config import MetricsConfig
from metrics.processor import (
    calculate_completeness_metrics,
    calculate_uniqueness_metrics,
    calculate_validity_metrics,
    calculate_consistency_metrics,
    calculate_all_metrics,
    generate_quality_report,
)


class TestMetricsProcessor:
    """Test metrics calculation functions."""

    def test_calculate_completeness_metrics(self):
        """Test completeness metrics calculation."""
        df = pd.DataFrame({
            "col1": [1, 2, None, 4],
            "col2": ["a", "b", "c", "d"],
            "col3": [None, None, None, None],
        })

        metrics = calculate_completeness_metrics(df)

        # Overall completeness: 7 filled / 12 total = 58.33%
        assert metrics["overall_completeness"] == pytest.approx(58.33, rel=0.1)
        assert metrics["total_cells"] == 12
        assert metrics["missing_cells"] == 5
        assert metrics["filled_cells"] == 7

        # col1: 3/4 = 75%
        assert metrics["column_completeness"]["col1"]["completeness"] == 75.0
        # col2: 4/4 = 100%
        assert metrics["column_completeness"]["col2"]["completeness"] == 100.0
        # col3: 0/4 = 0%
        assert metrics["column_completeness"]["col3"]["completeness"] == 0.0

    def test_calculate_uniqueness_metrics(self):
        """Test uniqueness metrics calculation."""
        df = pd.DataFrame({
            "id": [1, 2, 3, 3, 4],
            "name": ["Alice", "Bob", "Charlie", "Charlie", "David"],
        })

        metrics = calculate_uniqueness_metrics(df)

        # 4 unique rows out of 5 total = 80%
        assert metrics["overall_uniqueness"] == 80.0
        assert metrics["total_rows"] == 5
        assert metrics["unique_rows"] == 4
        assert metrics["duplicate_rows"] == 1

        # id column: 4 unique values out of 5 = 80%
        assert metrics["column_uniqueness"]["id"]["uniqueness"] == 80.0
        # name column: 4 unique values out of 5 = 80%
        assert metrics["column_uniqueness"]["name"]["uniqueness"] == 80.0

    def test_calculate_validity_metrics(self):
        """Test validity metrics calculation."""
        df = pd.DataFrame({
            "numbers": [1, 2, 3, float('inf')],
            "strings": ["valid", "", "also valid", "  "],
        })

        metrics = calculate_validity_metrics(df)

        # Numbers: 3 valid out of 4 = 75%
        assert metrics["column_validity"]["numbers"]["validity"] == 75.0
        assert metrics["column_validity"]["numbers"]["valid_count"] == 3

        # Strings: 2 valid (empty and whitespace-only are invalid) = 50%
        assert metrics["column_validity"]["strings"]["validity"] == 50.0

    def test_calculate_consistency_metrics(self):
        """Test consistency metrics calculation."""
        df = pd.DataFrame({
            "numbers": [1, 2, 3, 4],
            "mixed_strings": ["abc", "abcd", "ab", "abcde"],
        })

        metrics = calculate_consistency_metrics(df)

        # Numbers should have high consistency
        assert metrics["column_consistency"]["numbers"]["consistency"] == 100.0
        
        # Mixed strings should have lower consistency due to length variance
        assert metrics["column_consistency"]["mixed_strings"]["consistency"] < 100.0

    def test_calculate_all_metrics(self):
        """Test all metrics calculation."""
        df = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": ["a", "b", "c"],
        })

        metrics = calculate_all_metrics(df)

        assert "completeness" in metrics
        assert "uniqueness" in metrics
        assert "validity" in metrics
        assert "consistency" in metrics
        assert "dataset_info" in metrics

        assert metrics["dataset_info"]["rows"] == 3
        assert metrics["dataset_info"]["columns"] == 2

    def test_generate_quality_report(self):
        """Test quality report generation."""
        df = pd.DataFrame({
            "col1": [1, 2, None, 4],
            "col2": ["a", "b", "c", "c"],
        })

        report = generate_quality_report(df)

        assert "metrics" in report
        assert "recommendations" in report
        assert "overall_quality_score" in report
        assert "generated_at" in report

        # Quality score should be between 0 and 100
        assert 0 <= report["overall_quality_score"] <= 100

        # Should have recommendations for low completeness
        assert len(report["recommendations"]) > 0


class TestMetricsConfig:
    """Test metrics configuration."""

    def test_config_defaults(self):
        """Test default configuration."""
        config = MetricsConfig()

        assert config.max_upload_mb == 50
        assert config.sample_size == 10
        assert ".csv" in config.allowed_file_types

    def test_config_from_env(self):
        """Test configuration from environment."""
        os.environ["MAX_UPLOAD_MB"] = "100"
        os.environ["METRICS_SAMPLE_SIZE"] = "20"

        config = MetricsConfig.from_env()

        assert config.max_upload_mb == 100
        assert config.sample_size == 20

        # Clean up
        del os.environ["MAX_UPLOAD_MB"]
        del os.environ["METRICS_SAMPLE_SIZE"]


class TestMetricsAPI:
    """Test metrics API endpoints."""

    @pytest.fixture
    def app(self):
        """Create test Flask app."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
        from metrics.routes import metrics_bp
        from flask import Flask

        app = Flask(__name__)
        app.register_blueprint(metrics_bp)
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/metrics/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["ok"] is True
        assert data["service"] == "metrics"

    def test_upload_no_file(self, client):
        """Test upload without file."""
        response = client.post("/api/metrics/upload")
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_upload_and_analyze(self, client):
        """Test file upload and analysis."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("col1,col2,col3\n")
            f.write("1,a,x\n")
            f.write("2,b,y\n")
            f.write("3,c,z\n")
            temp_path = f.name

        try:
            # Upload file
            with open(temp_path, "rb") as f:
                response = client.post(
                    "/api/metrics/upload",
                    data={"file": (f, "test.csv")},
                    content_type="multipart/form-data",
                )

            assert response.status_code == 200
            upload_data = json.loads(response.data)
            assert "sessionId" in upload_data
            assert "columns" in upload_data
            assert len(upload_data["columns"]) == 3

            session_id = upload_data["sessionId"]

            # Analyze dataset
            response = client.post(
                "/api/metrics/analyze",
                json={"sessionId": session_id},
                content_type="application/json",
            )

            assert response.status_code == 200
            analysis_data = json.loads(response.data)
            assert "metrics" in analysis_data
            assert "overall_quality_score" in analysis_data

        finally:
            # Clean up
            os.unlink(temp_path)
