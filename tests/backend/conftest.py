"""Global conftest for all backend tests."""
import sys
import os

# Ensure src/ is always on the path for all backend tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

import pytest


@pytest.fixture(scope="session")
def app():
    """Global Flask test app fixture."""
    from api import app as flask_app
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False
    return flask_app


@pytest.fixture(scope="session")
def client(app):
    """Global Flask test client fixture."""
    with app.test_client() as test_client:
        yield test_client
