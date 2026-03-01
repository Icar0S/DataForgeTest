"""Security tests for authentication and authorization.

Verifies that:
- No admin/internal endpoints are left unauthenticated
- The /ask endpoint cannot be abused to execute arbitrary code on the server
- The absence of authentication is documented as a critical security risk

OWASP Reference: A01:2021 – Broken Access Control / A07 – Identification and Authentication Failures
"""

import pytest


# All routes registered in the application
_KNOWN_WRITE_ENDPOINTS = [
    ("POST", "/ask"),
    ("POST", "/api/metrics/upload"),
    ("POST", "/api/metrics/analyze"),
    ("POST", "/api/synth/generate"),
    ("POST", "/api/rag/query"),
    ("POST", "/api/checklist/runs"),
    ("POST", "/api/accuracy/upload"),
    ("POST", "/api/gold/upload"),
    ("POST", "/api/dataset_inspector/upload"),
]


@pytest.mark.security
class TestNoAuthentication:
    """Document the absence of authentication as a critical security risk.

    KNOWN VULNERABILITY: DataForgeTest has no authentication layer.
    All write endpoints are accessible without credentials.
    These tests FAIL intentionally to surface the risk.
    """

    @pytest.mark.xfail(
        strict=False,
        reason="No authentication layer implemented yet – OWASP A01/A07 known vulnerability. "
               "Tracked for future fix: add JWT/API-key auth via Flask-JWT-Extended."
    )
    @pytest.mark.parametrize("method,path", _KNOWN_WRITE_ENDPOINTS)
    def test_endpoint_requires_authentication(self, client, method, path):
        """Every write endpoint should require some form of authentication token.

        CRITICAL SECURITY RISK: This platform currently has NO authentication.
        Any user on the internet can invoke all write endpoints without credentials.
        Recommendation: add JWT / API-key authentication via Flask-JWT-Extended
        or similar. OWASP A07 – Identification and Authentication Failures.
        """
        if method == "POST":
            response = client.post(
                path,
                json={},
                content_type="application/json",
                # No Authorization header — should fail with 401 or 403
            )
        else:
            response = client.get(path)

        if response.status_code not in (401, 403):
            pytest.fail(
                f"[SECURITY] Endpoint {method} {path} is accessible without authentication. "
                f"Got status {response.status_code} instead of 401/403. "
                "CRITICAL: No authentication layer is present. "
                "All API endpoints are publicly writable. "
                "OWASP A01 – Broken Access Control / A07 – Authentication Failures."
            )


@pytest.mark.security
class TestCodeExecutionViaAsk:
    """The /ask endpoint must not allow arbitrary Python/shell code execution."""

    CODE_EXECUTION_PAYLOADS = [
        {"answers": {"rules": "__import__('os').system('id')"}},
        {"answers": {"rules": "eval('__import__(\"os\").getcwd()')"}},
        {"answers": {"rules": "exec('import subprocess; subprocess.check_output([\"id\"])')"}},
        {"answers": {"dataset_name": "$(id)"}},
    ]

    @pytest.mark.parametrize("payload", CODE_EXECUTION_PAYLOADS)
    def test_ask_does_not_execute_injected_code(self, client, payload):
        """Code execution payloads must not produce system command output."""
        response = client.post(
            "/ask",
            json=payload,
            content_type="application/json",
        )
        body = response.get_data(as_text=True)
        execution_markers = ("uid=", "gid=", "/root", "/home/", "groups=")
        for marker in execution_markers:
            assert marker not in body, (
                f"[SECURITY] Code execution via /ask payload! "
                f"Marker '{marker}' found in response. Payload: {payload}. "
                "OWASP A03 – Injection."
            )


@pytest.mark.security
class TestAdminEndpointsProtected:
    """No administrative endpoint must be exposed without protection."""

    _ADMIN_PATHS = [
        "/admin",
        "/admin/",
        "/api/admin",
        "/debug",
        "/api/debug",
        "/config",
        "/api/config",
        "/env",
        "/api/env",
    ]

    @pytest.mark.parametrize("path", _ADMIN_PATHS)
    def test_admin_path_not_accessible(self, client, path):
        """Common admin paths must return 404 (not found) or 403 (forbidden)."""
        response = client.get(path)
        assert response.status_code in (404, 403, 405), (
            f"[SECURITY] Admin/debug path {path} returned status {response.status_code}. "
            "This endpoint should not be accessible. "
            "OWASP A01 – Broken Access Control."
        )


@pytest.mark.security
class TestRAGQueryWithoutAuth:
    """RAG query endpoint must not be abused for data exfiltration."""

    @pytest.mark.xfail(
        strict=False,
        reason="No authentication layer implemented yet – OWASP A01/A07 known vulnerability."
    )
    def test_rag_query_accessible_without_auth(self, client):
        """Document that /api/rag/query is unauthenticated.

        SECURITY RISK: The RAG knowledge base can be queried by anyone.
        This test documents the vulnerability and will fail until auth is added.
        """
        response = client.post(
            "/api/rag/query",
            json={"query": "show me all documents"},
            content_type="application/json",
        )
        if response.status_code not in (401, 403):
            pytest.fail(
                f"[SECURITY] /api/rag/query is accessible without authentication "
                f"(status {response.status_code}). "
                "The internal knowledge base can be read by any unauthenticated user. "
                "OWASP A01 – Broken Access Control."
            )
