"""Security tests for LLM API key protection.

Verifies that:
- API keys are loaded from environment variables, never hardcoded
- Source files under src/ contain no hardcoded key patterns
- .env is listed in .gitignore
- requirements.txt does not reference packages with known critical CVEs

OWASP Reference: A02:2021 – Cryptographic Failures
"""

import ast
import re
import os
import sys
from pathlib import Path
import pytest

# Repository root (three levels above this file: security/ → backend/ → tests/ → repo root)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SRC_DIR = REPO_ROOT / "src"

# Patterns that indicate a hardcoded API key
HARDCODED_KEY_PATTERNS = [
    re.compile(r'\bsk-[A-Za-z0-9]{20,}'),          # OpenAI / Anthropic
    re.compile(r'\bAIza[A-Za-z0-9_\-]{35}'),        # Google API key
    re.compile(r'\bya29\.[A-Za-z0-9_\-]{30,}'),     # Google OAuth token
    re.compile(r'\banthropicKey\s*=\s*["\'][a-z0-9\-]+["\']', re.IGNORECASE),
    re.compile(r'\bgeminiKey\s*=\s*["\'][a-z0-9\-]+["\']', re.IGNORECASE),
]


def _collect_python_sources():
    """Return all .py files under src/."""
    return list(SRC_DIR.rglob("*.py"))


# ── Hardcoded Key Detection (AST + Regex) ─────────────────────────────────────


@pytest.mark.security
class TestNoHardcodedAPIKeys:
    """API keys must never appear as string literals in source code."""

    def test_no_hardcoded_keys_in_src_python(self):
        """Scan all Python files in src/ for hardcoded API key patterns."""
        violations = []
        for path in _collect_python_sources():
            try:
                source = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for pattern in HARDCODED_KEY_PATTERNS:
                matches = pattern.findall(source)
                if matches:
                    violations.append((str(path.relative_to(REPO_ROOT)), matches))

        assert not violations, (
            "[SECURITY] Hardcoded API key patterns found in source files:\n"
            + "\n".join(f"  {f}: {m}" for f, m in violations)
            + "\nOWASP A02 – Cryptographic Failures."
        )

    def test_api_key_loaded_from_environ_not_hardcoded(self):
        """LLM API keys must be read via os.environ or python-dotenv, not hardcoded."""
        # Gather all assignment-like lines referencing sensitive keys
        key_names = ("GEMINI_API_KEY", "ANTHROPIC_API_KEY", "LLM_API_KEY", "api_key")
        violations = []

        for path in _collect_python_sources():
            try:
                source = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for line_no, line in enumerate(source.splitlines(), start=1):
                line_stripped = line.strip()
                if any(k in line_stripped for k in key_names):
                    # Check if the value is a string literal (not os.environ or env.get)
                    hardcoded = re.search(
                        r'(?:api_key|GEMINI_API_KEY|ANTHROPIC_API_KEY|LLM_API_KEY)\s*=\s*["\'](?!")[^"\']{8,}["\']',
                        line_stripped,
                    )
                    if hardcoded:
                        violations.append(
                            f"{path.relative_to(REPO_ROOT)}:{line_no}: {line_stripped[:120]}"
                        )

        assert not violations, (
            "[SECURITY] API keys appear to be hardcoded in source:\n"
            + "\n".join(f"  {v}" for v in violations)
            + "\nOWASP A02 – Cryptographic Failures."
        )


# ── .env in .gitignore ────────────────────────────────────────────────────────


@pytest.mark.security
class TestDotEnvInGitignore:
    """.env file must be listed in .gitignore to prevent accidental key commits."""

    def test_env_file_in_gitignore(self):
        """Verify that .env is present in .gitignore."""
        gitignore_path = REPO_ROOT / ".gitignore"
        assert gitignore_path.exists(), (
            "[SECURITY] .gitignore file not found at repo root. "
            "Without .gitignore, .env secrets can be committed accidentally."
        )
        content = gitignore_path.read_text(encoding="utf-8")
        # Accept patterns like `.env`, `*.env`, `.env*`
        env_patterns = [r"^\.env$", r"^\*\.env", r"^\.env\*", r"^\.env "]
        matched = any(
            re.search(p, content, re.MULTILINE) for p in env_patterns
        )
        assert matched, (
            "[SECURITY] .env is NOT listed in .gitignore. "
            "API keys stored in .env may be accidentally committed to version control. "
            "OWASP A02 – Cryptographic Failures."
        )

    def test_env_file_not_committed(self):
        """Ensure .env is not tracked by git."""
        env_path = REPO_ROOT / ".env"
        if env_path.exists():
            import subprocess
            result = subprocess.run(
                ["git", "ls-files", ".env"],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
            )
            assert result.stdout.strip() == "", (
                "[SECURITY] .env file is tracked by git! "
                "It may contain API keys that are being committed to the repository. "
                "Run: git rm --cached .env && git commit -m 'Remove .env from tracking'"
            )


# ── AST-based Key Analysis ────────────────────────────────────────────────────


@pytest.mark.security
class TestASTKeyAnalysis:
    """Use AST analysis to detect string literals that look like API keys."""

    def test_no_key_like_string_literals_in_ast(self):
        """Traverse AST of all src Python files looking for key-like string values."""
        violations = []

        for path in _collect_python_sources():
            try:
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source)
            except (OSError, UnicodeDecodeError, SyntaxError):
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    val = node.value
                    for pattern in HARDCODED_KEY_PATTERNS:
                        if pattern.search(val):
                            violations.append(
                                f"{path.relative_to(REPO_ROOT)}:"
                                f"line {node.lineno}: '{val[:30]}...'"
                            )

        assert not violations, (
            "[SECURITY] API key-like string literals found in AST:\n"
            + "\n".join(f"  {v}" for v in violations)
            + "\nOWASP A02 – Cryptographic Failures."
        )


# ── requirements.txt Basic Audit ─────────────────────────────────────────────


@pytest.mark.security
class TestRequirementsSecurity:
    """requirements.txt must not pin packages with known critical vulnerabilities.

    NOTE: The CVE list below is intentionally minimal and illustrative. For a
    comprehensive audit, run `pip-audit` or `safety check` in CI. This static
    check is a lightweight safety net for the most common historical CVEs.
    """

    # Packages with known critical CVEs at specific versions (illustrative list).
    # Extend this list as new CVEs are discovered or use pip-audit in CI.
    KNOWN_VULNERABLE = {
        # package_name: [(bad_version_prefix, cve_id), ...]
        "flask": [("0.", "CVE-2023-30861")],
        "werkzeug": [("2.0.", "CVE-2023-46136"), ("2.1.", "CVE-2023-46136")],
        "pillow": [("9.0.", "CVE-2023-44271"), ("9.1.", "CVE-2023-44271")],
    }

    def test_requirements_txt_exists(self):
        """requirements.txt must be present at repo root."""
        req_path = REPO_ROOT / "requirements.txt"
        assert req_path.exists(), (
            "requirements.txt not found. "
            "Cannot audit package security."
        )

    def test_no_known_vulnerable_packages(self):
        """Check that requirements.txt does not pin known-vulnerable package versions."""
        req_path = REPO_ROOT / "requirements.txt"
        if not req_path.exists():
            pytest.skip("requirements.txt not found")

        content = req_path.read_text(encoding="utf-8")
        violations = []

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Parse "package==version" or "package>=version"
            match = re.match(r'^([A-Za-z0-9_\-]+)\s*[=<>!]{1,2}\s*([0-9][^\s]*)', line)
            if not match:
                continue
            pkg_name = match.group(1).lower()
            pkg_version = match.group(2)
            if pkg_name in self.KNOWN_VULNERABLE:
                for bad_prefix, cve in self.KNOWN_VULNERABLE[pkg_name]:
                    if pkg_version.startswith(bad_prefix):
                        violations.append(f"{pkg_name}=={pkg_version} ({cve})")

        assert not violations, (
            "[SECURITY] requirements.txt pins packages with known CVEs:\n"
            + "\n".join(f"  {v}" for v in violations)
            + "\nRecommendation: upgrade affected packages."
        )
