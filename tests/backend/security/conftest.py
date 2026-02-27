"""Shared fixtures for backend security tests."""

import sys
import os
import pytest


def pytest_configure(config):
    """Register custom marks to avoid PytestUnknownMarkWarning."""
    config.addinivalue_line(
        "markers",
        "security: marks tests as security-related (select with -m security)",
    )

# Add src to Python path so Flask app can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))


@pytest.fixture(scope="session")
def app():
    """Create and configure the Flask application for testing."""
    from api import app as flask_app

    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False
    return flask_app


@pytest.fixture(scope="session")
def client(app):
    """Provide a Flask test client for the duration of the test session."""
    with app.test_client() as test_client:
        yield test_client
