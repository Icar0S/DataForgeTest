# Security Test Suite – DataForgeTest Backend

This directory contains automated security tests for the DataForgeTest platform.

## How to Run

```bash
# Run all security tests with verbose output
pytest tests/backend/security/ -v -m security

# Run a single file
pytest tests/backend/security/test_http_security_headers.py -v

# Run with short summary of failures only
pytest tests/backend/security/ -m security --tb=short
```

## Test Files

| File | What it Tests | OWASP Category |
|------|--------------|----------------|
| `test_http_security_headers.py` | Mandatory HTTP security headers on all endpoints | A05 – Security Misconfiguration |
| `test_cors_policy.py` | CORS origin restrictions, wildcard prevention | A05 – Security Misconfiguration |
| `test_input_validation_injection.py` | SQL injection, command injection, path traversal, XSS, prompt injection | A03 – Injection |
| `test_sensitive_data_exposure.py` | Stack trace leakage, API key exposure, version disclosure | A02 – Cryptographic Failures |
| `test_rate_limiting_dos.py` | Server stability under load, rate limiting, oversized payloads | A05 – Security Misconfiguration |
| `test_file_upload_security.py` | Dangerous file extensions, path traversal filenames, CSV injection, size limits | A04 – Insecure Design |
| `test_authentication_authorization.py` | Unauthenticated endpoint access, code execution via /ask, admin path exposure | A01 – Broken Access Control |
| `test_llm_api_key_protection.py` | Hardcoded key detection (AST + regex), .gitignore validation, CVE audit | A02 – Cryptographic Failures |
| `test_docker_security.py` | Non-root USER in Dockerfile, pinned base image, compose secret handling | A05 – Security Misconfiguration |

## Vulnerabilities Covered

### Currently **FAILING** tests (known vulnerabilities to fix)

The following tests fail intentionally to document existing security gaps:

1. **`test_http_security_headers.py`** – All header tests fail because Flask does not set
   `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Content-Security-Policy`,
   `Referrer-Policy`, or `Strict-Transport-Security` by default.
   **Fix**: Add a `@app.after_request` hook in `src/api.py` (or use `flask-talisman`).

2. **`test_cors_policy.py`** – `CORS(app)` in `src/api.py` is configured with no
   origin whitelist, so it reflects the wildcard `*` to all origins.
   **Fix**: Replace `CORS(app)` with `CORS(app, origins=["https://yourdomain.com"])`.

3. **`test_rate_limiting_dos.py`** – `test_rate_limiting_present_on_ask` and
   `test_rate_limiting_present_on_metrics` fail because no rate limiting is implemented.
   **Fix**: Add `Flask-Limiter` with per-IP limits on write endpoints.
   `test_large_body_rejected_on_ask` fails because `MAX_CONTENT_LENGTH` is not set.
   **Fix**: Add `app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024` to `src/api.py`.

4. **`test_authentication_authorization.py`** – All `test_endpoint_requires_authentication`
   and `test_rag_query_accessible_without_auth` tests fail because DataForgeTest has no
   authentication layer. Every endpoint is publicly accessible.
   **Fix**: Implement JWT or API-key authentication via `Flask-JWT-Extended`.

5. **`test_docker_security.py`** – `test_non_root_user_instruction_present` fails because
   the Dockerfile has no `USER` instruction; the container runs as root.
   **Fix**: Add `RUN useradd -m appuser && USER appuser` before the `CMD` line.

### Currently **PASSING** tests

- `test_sensitive_data_exposure.py` – Stack traces are not exposed; API keys do not appear in responses.
- `test_input_validation_injection.py` – Injection payloads do not execute or leak system output.
- `test_file_upload_security.py` – Dangerous extensions are rejected; filenames are sanitised via `secure_filename`.
- `test_llm_api_key_protection.py` – No hardcoded keys found; `.env` is in `.gitignore`.
- `test_docker_security.py` (except USER instruction) – Base image is pinned; compose uses env-var substitution.

## conftest.py

Provides a session-scoped `client` fixture that creates a Flask test client from `src/api.py`.
All test classes receive `client` via pytest dependency injection.

```python
# Usage in any test:
def test_example(self, client):
    response = client.get("/")
    assert response.status_code == 200
```
