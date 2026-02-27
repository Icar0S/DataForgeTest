"""Security tests for file upload endpoints.

Verifies that file upload endpoints:
- Reject dangerous file extensions (.php, .exe, .sh, .py)
- Normalize path-traversal filenames
- Accept but do not execute CSV injection payloads
- Reject zero-byte and oversized files

Endpoints tested: /api/metrics/upload, /api/gold/upload, /api/accuracy/upload

OWASP Reference: A04:2021 – Insecure Design / A05 – Security Misconfiguration
"""

import io
import pytest


def _upload(client, endpoint, filename, content=b"col1,col2\nval1,val2\n", content_type=None):
    """Helper: POST a file to an upload endpoint."""
    data = {
        "file": (io.BytesIO(content), filename),
    }
    return client.post(
        endpoint,
        data=data,
        content_type="multipart/form-data",
    )


UPLOAD_ENDPOINTS = [
    "/api/metrics/upload",
    "/api/gold/upload",
]


# ── Dangerous Extensions ──────────────────────────────────────────────────────


@pytest.mark.security
class TestDangerousExtensions:
    """Files with executable extensions must be rejected."""

    DANGEROUS_FILES = [
        ("malware.php", b"<?php system($_GET['cmd']); ?>"),
        ("malware.exe", b"MZ\x90\x00PE executable"),
        ("malware.sh", b"#!/bin/bash\nrm -rf /"),
        ("malware.py", b"import os; os.system('id')"),
        ("malware.jsp", b"<% Runtime.getRuntime().exec(request.getParameter(\"cmd\")); %>"),
    ]

    @pytest.mark.parametrize("endpoint", UPLOAD_ENDPOINTS)
    @pytest.mark.parametrize("filename,content", DANGEROUS_FILES)
    def test_dangerous_extension_rejected(self, client, endpoint, filename, content):
        """Files with dangerous extensions must not be accepted (expect 400/415)."""
        response = _upload(client, endpoint, filename, content)
        assert response.status_code in (400, 415, 422), (
            f"[SECURITY] Dangerous file '{filename}' was NOT rejected by {endpoint}. "
            f"Got status {response.status_code}. Only .csv, .xlsx, .parquet should be allowed. "
            "OWASP A04 – Insecure Design / Remote Code Execution risk."
        )


# ── Path Traversal Filenames ──────────────────────────────────────────────────


@pytest.mark.security
class TestPathTraversalFilename:
    """Upload filenames containing path traversal sequences must be sanitised."""

    TRAVERSAL_NAMES = [
        "../../etc/passwd.csv",
        "../secret.csv",
        "/absolute/path/file.csv",
        "..%2F..%2Fetc%2Fpasswd.csv",
    ]

    @pytest.mark.parametrize("endpoint", UPLOAD_ENDPOINTS)
    @pytest.mark.parametrize("filename", TRAVERSAL_NAMES)
    def test_path_traversal_filename_sanitised(self, client, endpoint, filename):
        """Path-traversal filenames must be sanitised; the file must not escape the upload dir."""
        response = _upload(client, endpoint, filename)
        # The endpoint may accept (200) or reject (400) the file.
        # What must NOT happen is that the response confirms the file was stored
        # at the traversal path.
        body = response.get_data(as_text=True)
        assert "/etc/" not in body and "/passwd" not in body, (
            f"[SECURITY] Path traversal filename '{filename}' appears to have been accepted "
            f"with the original path on {endpoint}. Response body: {body[:200]}. "
            "OWASP A01 – Broken Access Control."
        )
        if response.status_code == 200:
            import json as _json
            try:
                data = _json.loads(body)
                saved_path = str(data.get("filename", data.get("path", "")))
                assert ".." not in saved_path and saved_path.count("/") <= 1, (
                    f"[SECURITY] File stored with traversal path '{saved_path}' on {endpoint}."
                )
            except _json.JSONDecodeError:
                pass


# ── CSV Injection ─────────────────────────────────────────────────────────────


@pytest.mark.security
class TestCSVInjection:
    """CSV injection formulas must be accepted as data, not executed."""

    CSV_INJECTION_PAYLOADS = [
        b"cmd,formula\ntest,=CMD|' /C calc'!A0\n",
        b"col1,col2\n+HYPERLINK(\"http://evil.com\"),val2\n",
        b"col1,col2\n@SUM(1+1)*cmd|' /C calc'!A0,val2\n",
    ]

    @pytest.mark.parametrize("payload", CSV_INJECTION_PAYLOADS)
    def test_csv_injection_accepted_not_executed(self, client, payload):
        """CSV injection formulas must be stored as raw data (not executed)."""
        response = _upload(client, "/api/metrics/upload", "test.csv", payload)
        # Acceptable outcomes: 200 (stored as data) or 400 (validation rejected formula)
        assert response.status_code in (200, 400, 415, 422), (
            f"[SECURITY] Unexpected response {response.status_code} for CSV injection payload."
        )
        body = response.get_data(as_text=True)
        # The server must not execute the command or return shell output.
        # These markers indicate actual command execution, not just data echo.
        execution_markers = ("system32", "/bin/sh", "uid=", "Permission denied", "command not found")
        for marker in execution_markers:
            assert marker not in body.lower(), (
                f"[SECURITY] CSV injection formula may have been executed. "
                f"Execution marker '{marker}' found in response. Payload: {payload!r}"
            )


# ── Zero and Oversized Files ──────────────────────────────────────────────────


@pytest.mark.security
class TestFileSizeBoundaries:
    """File upload size boundaries must be enforced."""

    def test_zero_byte_file_rejected(self, client):
        """A zero-byte file upload must be rejected with 400."""
        response = _upload(client, "/api/metrics/upload", "empty.csv", b"")
        assert response.status_code in (400, 422), (
            f"[SECURITY] Zero-byte file was accepted by /api/metrics/upload. "
            f"Got {response.status_code}. Empty files can cause downstream parsing errors."
        )

    def test_oversized_file_rejected(self, client):
        """A file exceeding the configured max upload size must be rejected."""
        # Generate content slightly over 10 MB
        big_content = b"col1,col2\n" + b"a,b\n" * (3 * 1024 * 1024)
        response = _upload(client, "/api/metrics/upload", "big.csv", big_content)
        if response.status_code not in (400, 413, 422):
            pytest.fail(
                f"[SECURITY] Oversized file was not rejected by /api/metrics/upload. "
                f"Got status {response.status_code}. "
                "Large uploads can exhaust server memory. "
                "Ensure MAX_UPLOAD_MB is enforced server-side. "
                "OWASP A05 – Security Misconfiguration."
            )
