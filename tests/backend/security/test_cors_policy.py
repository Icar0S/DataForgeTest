"""Security tests for CORS policy.

Verifies that Cross-Origin Resource Sharing is restricted to allowed origins:
- Wildcard (*) must not be used in production
- Untrusted origins must be rejected or not reflected
- 'null' origin must not be allowed
- Access-Control-Allow-Credentials must not be combined with wildcard
- Only expected HTTP methods should be allowed

OWASP Reference: A05:2021 – Security Misconfiguration
"""

import pytest


@pytest.mark.security
class TestCORSWildcard:
    """CORS must not accept wildcard origins in production."""

    def test_no_wildcard_origin_on_health(self, client):
        """Health endpoint must not return wildcard ACAO header."""
        response = client.get("/", headers={"Origin": "http://evil.com"})
        acao = response.headers.get("Access-Control-Allow-Origin", "")
        assert acao != "*", (
            "[SECURITY] Access-Control-Allow-Origin is set to '*' on /. "
            "Wildcard CORS allows any origin to read API responses. "
            "OWASP A05 – Security Misconfiguration."
        )

    def test_no_wildcard_origin_on_ask(self, client):
        """Ask endpoint must not return wildcard ACAO header."""
        response = client.post(
            "/ask",
            json={"answers": {}},
            headers={"Origin": "http://evil.com"},
            content_type="application/json",
        )
        acao = response.headers.get("Access-Control-Allow-Origin", "")
        assert acao != "*", (
            "[SECURITY] Access-Control-Allow-Origin is set to '*' on /ask. "
            "Wildcard CORS allows any origin to read API responses."
        )


@pytest.mark.security
class TestCORSEvilOrigin:
    """Untrusted origins must not be reflected in ACAO header."""

    def test_evil_origin_not_reflected_health(self, client):
        """Origin http://evil.com must not be reflected on /."""
        evil_origin = "http://evil.com"
        response = client.get("/", headers={"Origin": evil_origin})
        acao = response.headers.get("Access-Control-Allow-Origin", "")
        assert acao != evil_origin, (
            f"[SECURITY] Origin '{evil_origin}' is reflected back on /. "
            "Reflecting untrusted origins enables cross-origin attacks. "
            "OWASP A05 – Security Misconfiguration."
        )

    def test_evil_origin_not_reflected_api(self, client):
        """Origin http://evil.com must not be reflected on /api/metrics/analyze."""
        evil_origin = "http://evil.com"
        response = client.post(
            "/api/metrics/analyze",
            json={},
            headers={"Origin": evil_origin},
            content_type="application/json",
        )
        acao = response.headers.get("Access-Control-Allow-Origin", "")
        assert acao != evil_origin, (
            f"[SECURITY] Origin '{evil_origin}' is reflected back on /api/metrics/analyze. "
            "OWASP A05 – Security Misconfiguration."
        )


@pytest.mark.security
class TestCORSNullOrigin:
    """Origin: null must not be allowed (used in sandboxed iframes)."""

    def test_null_origin_rejected(self, client):
        """'null' origin must not be accepted."""
        response = client.get("/", headers={"Origin": "null"})
        acao = response.headers.get("Access-Control-Allow-Origin", "")
        assert acao != "null", (
            "[SECURITY] Origin 'null' is accepted on /. "
            "This allows requests from sandboxed iframes (origin spoofing). "
            "OWASP A05 – Security Misconfiguration."
        )


@pytest.mark.security
class TestCORSCredentials:
    """Access-Control-Allow-Credentials must not be true when ACAO is *."""

    def test_credentials_not_combined_with_wildcard(self, client):
        """ACAC: true must not appear together with ACAO: * on any endpoint."""
        for path in ["/", "/api/metrics/analyze"]:
            method = "GET" if path == "/" else "POST"
            if method == "POST":
                response = client.post(
                    path, json={}, content_type="application/json",
                    headers={"Origin": "http://evil.com"}
                )
            else:
                response = client.get(path, headers={"Origin": "http://evil.com"})

            acao = response.headers.get("Access-Control-Allow-Origin", "")
            acac = response.headers.get("Access-Control-Allow-Credentials", "").lower()
            assert not (acao == "*" and acac == "true"), (
                f"[SECURITY] Access-Control-Allow-Credentials is 'true' combined with "
                f"Access-Control-Allow-Origin: '*' on {path}. "
                "This combination is rejected by browsers and indicates a misconfiguration. "
                "OWASP A05 – Security Misconfiguration."
            )


@pytest.mark.security
class TestCORSAllowedMethods:
    """Preflight OPTIONS should only advertise necessary HTTP methods."""

    def test_options_preflight_allowed_methods(self, client):
        """OPTIONS preflight must not advertise dangerous methods like PUT/DELETE."""
        response = client.options(
            "/ask",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        acam = response.headers.get("Access-Control-Allow-Methods", "")
        dangerous = {"DELETE", "PUT", "PATCH", "TRACE", "CONNECT"}
        advertised = {m.strip().upper() for m in acam.split(",") if m.strip()}
        unexpected = dangerous & advertised
        assert not unexpected, (
            f"[SECURITY] OPTIONS preflight on /ask advertises dangerous methods: {unexpected}. "
            "Only GET, POST, OPTIONS should be necessary. "
            "OWASP A05 – Security Misconfiguration."
        )
