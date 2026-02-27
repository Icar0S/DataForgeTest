"""Security tests for HTTP response headers.

Verifies that all API endpoints return mandatory security headers:
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection
- Strict-Transport-Security (HSTS)
- Content-Security-Policy
- Referrer-Policy

OWASP Reference: A05:2021 – Security Misconfiguration
"""

import pytest

ENDPOINTS = [
    ("GET", "/"),
    ("POST", "/ask"),
    ("POST", "/api/metrics/analyze"),
    ("POST", "/api/synth/generate"),
    ("POST", "/api/rag/query"),
    ("GET", "/api/checklist/"),
    ("GET", "/api/accuracy/"),
    ("GET", "/api/gold/"),
    ("GET", "/api/dataset_inspector/"),
]

# Minimal request bodies required so routes return non-404 responses
_BODY = {
    "/ask": {"answers": {}},
    "/api/metrics/analyze": {},
    "/api/synth/generate": {},
    "/api/rag/query": {"query": "test"},
}


def _call(client, method, path):
    body = _BODY.get(path)
    if method == "POST":
        return client.post(path, json=body or {}, content_type="application/json")
    return client.get(path)


@pytest.mark.security
class TestXContentTypeOptions:
    """X-Content-Type-Options must be present and set to 'nosniff'."""

    @pytest.mark.parametrize("method,path", ENDPOINTS)
    def test_x_content_type_options(self, client, method, path):
        response = _call(client, method, path)
        header = response.headers.get("X-Content-Type-Options", "")
        assert header.lower() == "nosniff", (
            f"[SECURITY] X-Content-Type-Options header missing or wrong on {path}. "
            f"Got: '{header}'. Expected: 'nosniff'. "
            "OWASP A05 – Security Misconfiguration."
        )


@pytest.mark.security
class TestXFrameOptions:
    """X-Frame-Options must be DENY or SAMEORIGIN to prevent clickjacking."""

    @pytest.mark.parametrize("method,path", ENDPOINTS)
    def test_x_frame_options(self, client, method, path):
        response = _call(client, method, path)
        header = response.headers.get("X-Frame-Options", "").upper()
        assert header in ("DENY", "SAMEORIGIN"), (
            f"[SECURITY] X-Frame-Options header missing or wrong on {path}. "
            f"Got: '{header}'. Expected: 'DENY' or 'SAMEORIGIN'. "
            "OWASP A05 – Security Misconfiguration / Clickjacking."
        )


@pytest.mark.security
class TestXXSSProtection:
    """X-XSS-Protection should be present (legacy browsers)."""

    @pytest.mark.parametrize("method,path", ENDPOINTS)
    def test_x_xss_protection(self, client, method, path):
        response = _call(client, method, path)
        header = response.headers.get("X-XSS-Protection", "")
        assert header, (
            f"[SECURITY] X-XSS-Protection header missing on {path}. "
            "OWASP A03:2021 – Injection / XSS."
        )
        assert "1" in header, (
            f"[SECURITY] X-XSS-Protection is not enabled on {path}. Got: '{header}'."
        )


@pytest.mark.security
class TestContentSecurityPolicy:
    """Content-Security-Policy must be present on all endpoints."""

    @pytest.mark.parametrize("method,path", ENDPOINTS)
    def test_content_security_policy(self, client, method, path):
        response = _call(client, method, path)
        header = response.headers.get("Content-Security-Policy", "")
        assert header, (
            f"[SECURITY] Content-Security-Policy header missing on {path}. "
            "OWASP A05 – Security Misconfiguration."
        )


@pytest.mark.security
class TestReferrerPolicy:
    """Referrer-Policy must be present to avoid leaking sensitive URLs."""

    @pytest.mark.parametrize("method,path", ENDPOINTS)
    def test_referrer_policy(self, client, method, path):
        response = _call(client, method, path)
        header = response.headers.get("Referrer-Policy", "")
        assert header, (
            f"[SECURITY] Referrer-Policy header missing on {path}. "
            "This may leak sensitive URL data to third parties."
        )


@pytest.mark.security
class TestStrictTransportSecurity:
    """HSTS header should be present to enforce HTTPS."""

    @pytest.mark.parametrize("method,path", ENDPOINTS)
    def test_hsts_header_present(self, client, method, path):
        response = _call(client, method, path)
        header = response.headers.get("Strict-Transport-Security", "")
        assert header, (
            f"[SECURITY] Strict-Transport-Security (HSTS) header missing on {path}. "
            "This allows downgrade attacks from HTTPS to HTTP. "
            "OWASP A05 – Security Misconfiguration."
        )
