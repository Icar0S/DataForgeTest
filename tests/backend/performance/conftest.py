"""Fixtures for performance and benchmark tests."""

import os
import sys
import io
import pytest
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from src.api import app as flask_app


@pytest.fixture
def client():
    """Flask test client fixture."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def production_base_url():
    """Base URL for production tests."""
    return os.environ.get("LOAD_TEST_HOST", "https://dataforgetest-backend.onrender.com")


@pytest.fixture
def sample_csv_100():
    """Generate a 100-row CSV as bytes."""
    df = pd.DataFrame({
        "id": range(1, 101),
        "name": [f"item_{i}" for i in range(1, 101)],
        "score": [float(i) * 0.5 for i in range(1, 101)],
    })
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


@pytest.fixture
def sample_csv_500():
    """Generate a 500-row CSV with 5 mixed-type columns as bytes."""
    df = pd.DataFrame({
        "id": range(1, 501),
        "name": [f"record_{i}" for i in range(1, 501)],
        "value": [float(i) * 1.1 for i in range(1, 501)],
        "date": [f"2024-01-{(i % 28) + 1:02d}" for i in range(500)],
        "active": [i % 2 == 0 for i in range(1, 501)],
    })
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()
