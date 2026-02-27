"""Security tests for Docker and container configuration.

Verifies Docker best practices:
- Container does not run as root (USER instruction present in Dockerfile)
- Sensitive env vars are not hardcoded in docker-compose.yml
- Base image uses a pinned version tag, not 'latest'
- Only necessary ports are exposed

OWASP Reference: A05:2021 – Security Misconfiguration
"""

import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DOCKERFILE = REPO_ROOT / "Dockerfile"
DOCKER_COMPOSE = REPO_ROOT / "docker-compose.yml"


# ── Dockerfile Checks ─────────────────────────────────────────────────────────


@pytest.mark.security
class TestDockerfileUserInstruction:
    """The Dockerfile must not run the application as root."""

    def test_dockerfile_exists(self):
        """Dockerfile must exist at repository root."""
        assert DOCKERFILE.exists(), (
            "Dockerfile not found at repository root. Cannot audit container security."
        )

    def test_non_root_user_instruction_present(self):
        """Dockerfile must include a USER instruction to drop root privileges.

        SECURITY RISK: If no USER instruction is present, the container runs as root,
        which significantly increases the blast radius of any container escape.
        OWASP A05 – Security Misconfiguration.
        """
        if not DOCKERFILE.exists():
            pytest.skip("Dockerfile not found")

        content = DOCKERFILE.read_text(encoding="utf-8")
        # Match lines like: USER appuser, USER 1000, USER nobody
        user_instructions = re.findall(r'^\s*USER\s+\S+', content, re.MULTILINE | re.IGNORECASE)

        if not user_instructions:
            pytest.fail(
                "[SECURITY] No USER instruction found in Dockerfile. "
                "The container runs as root, which is a security risk. "
                "Add: RUN useradd -m appuser && USER appuser "
                "OWASP A05 – Security Misconfiguration."
            )

    def test_non_root_user_is_not_root(self):
        """The USER instruction must not explicitly set the user to root."""
        if not DOCKERFILE.exists():
            pytest.skip("Dockerfile not found")

        content = DOCKERFILE.read_text(encoding="utf-8")
        for line in content.splitlines():
            stripped = line.strip().upper()
            if stripped.startswith("USER"):
                user_value = stripped.split()[1] if len(stripped.split()) > 1 else ""
                assert user_value not in ("ROOT", "0"), (
                    f"[SECURITY] Dockerfile explicitly sets USER to root: '{line.strip()}'. "
                    "OWASP A05 – Security Misconfiguration."
                )


# ── Base Image Version ────────────────────────────────────────────────────────


@pytest.mark.security
class TestDockerfileBaseImage:
    """Base image must use a pinned version, not 'latest'."""

    def test_base_image_not_latest(self):
        """FROM instruction must not use the ':latest' tag."""
        if not DOCKERFILE.exists():
            pytest.skip("Dockerfile not found")

        content = DOCKERFILE.read_text(encoding="utf-8")
        from_lines = re.findall(r'^\s*FROM\s+\S+', content, re.MULTILINE | re.IGNORECASE)

        for from_line in from_lines:
            parts = from_line.strip().split()
            if len(parts) < 2:
                continue
            image = parts[1].lower()
            # Skip build stages (e.g., FROM base AS final)
            if ":latest" in image or (":" not in image and "@" not in image):
                # Allow scratch and other tag-less special images
                if image in ("scratch", "busybox", "alpine"):
                    continue
                assert ":latest" not in image, (
                    f"[SECURITY] Dockerfile base image uses ':latest' tag: '{from_line.strip()}'. "
                    "Pinning to ':latest' can pull in unreviewed breaking changes or vulnerabilities. "
                    "Use a specific version tag (e.g., python:3.12-slim). "
                    "OWASP A05 – Security Misconfiguration."
                )


# ── Exposed Ports ─────────────────────────────────────────────────────────────


@pytest.mark.security
class TestDockerfileExposedPorts:
    """Only required ports should be exposed in the Dockerfile."""

    _ALLOWED_PORTS = {5000, 8000, 8080}  # Flask default and common alternatives

    def test_only_necessary_ports_exposed(self):
        """Dockerfile must only EXPOSE application-necessary ports."""
        if not DOCKERFILE.exists():
            pytest.skip("Dockerfile not found")

        content = DOCKERFILE.read_text(encoding="utf-8")
        expose_lines = re.findall(r'^\s*EXPOSE\s+(.+)', content, re.MULTILINE | re.IGNORECASE)

        exposed = set()
        for line in expose_lines:
            for token in line.split():
                # Handle "PORT/tcp" format
                port_str = token.split("/")[0]
                try:
                    exposed.add(int(port_str))
                except ValueError:
                    pass

        unexpected = exposed - self._ALLOWED_PORTS
        assert not unexpected, (
            f"[SECURITY] Dockerfile exposes unexpected ports: {unexpected}. "
            f"Only {self._ALLOWED_PORTS} are expected for this application. "
            "OWASP A05 – Security Misconfiguration."
        )


# ── docker-compose.yml Checks ─────────────────────────────────────────────────


@pytest.mark.security
class TestDockerComposeSecrets:
    """Sensitive values must not be hardcoded in docker-compose.yml."""

    SENSITIVE_PATTERNS = [
        re.compile(r'\bsk-[A-Za-z0-9]{20,}'),       # OpenAI / Anthropic keys
        re.compile(r'\bAIza[A-Za-z0-9_\-]{35}'),    # Google API keys
        re.compile(r'\bya29\.[A-Za-z0-9_\-]{30,}'),  # Google OAuth
    ]

    def test_docker_compose_exists(self):
        """docker-compose.yml must exist at repo root."""
        assert DOCKER_COMPOSE.exists(), (
            "docker-compose.yml not found. Cannot audit compose security."
        )

    def test_no_hardcoded_secrets_in_compose(self):
        """docker-compose.yml must not contain hardcoded API key values."""
        if not DOCKER_COMPOSE.exists():
            pytest.skip("docker-compose.yml not found")

        content = DOCKER_COMPOSE.read_text(encoding="utf-8")
        violations = []
        for pattern in self.SENSITIVE_PATTERNS:
            matches = pattern.findall(content)
            if matches:
                violations.extend(matches)

        assert not violations, (
            "[SECURITY] Hardcoded API key patterns found in docker-compose.yml: "
            + str(violations)
            + "\nOWASP A02 – Cryptographic Failures."
        )

    def test_api_keys_use_env_substitution(self):
        """API key variables in docker-compose.yml must use ${VAR} substitution."""
        if not DOCKER_COMPOSE.exists():
            pytest.skip("docker-compose.yml not found")

        content = DOCKER_COMPOSE.read_text(encoding="utf-8")

        # Check that sensitive env var names are referenced via ${} not raw strings
        dangerous_lines = []
        for line_no, line in enumerate(content.splitlines(), start=1):
            stripped = line.strip()
            # Lines that set API keys to a literal string value (not a ${} reference)
            if re.search(
                r'(?:GEMINI_API_KEY|ANTHROPIC_API_KEY|LLM_API_KEY)\s*=\s*[^${\s][^\s]{5,}',
                stripped,
            ):
                dangerous_lines.append(f"  line {line_no}: {stripped}")

        assert not dangerous_lines, (
            "[SECURITY] docker-compose.yml sets API keys to literal values:\n"
            + "\n".join(dangerous_lines)
            + "\nUse environment variable substitution: GEMINI_API_KEY=${GEMINI_API_KEY}"
        )
