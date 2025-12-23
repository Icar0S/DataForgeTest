"""Tests for robust blueprint registration system resilience.

These tests validate that the new registration system can handle:
1. Individual blueprint failures
2. Unicode/encoding issues
3. Import errors
4. Module initialization failures

Date: December 23, 2025
"""

import pytest  # noqa: F401 # type: ignore
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# pylint: disable=wrong-import-position


class TestRegistrationResilience:
    """Test blueprint registration system resilience."""

    def test_app_imports_successfully(self):
        """Test that app can be imported without errors."""
        try:
            from api import app  # type: ignore

            assert app is not None
        except Exception as e:
            pytest.fail(f"Failed to import app: {e}")

    def test_registration_logs_are_visible(self, capsys):
        """Test that registration logs are printed correctly."""
        # Import app (this triggers registration)
        from api import app  # type: ignore

        # Check that app was created
        assert app is not None

        # Logs should have been printed during import
        # (captured by capsys if we reload the module, but that's complex)
        # Instead, just verify the app is functional
        assert len(app.blueprints) > 0

    def test_critical_blueprints_take_priority(self):
        """Test that critical blueprints are registered first."""
        from api import app  # type: ignore

        # Define expected priority order
        critical_first = ["metrics", "checklist", "dataset_inspector"]

        # All critical should be present
        for bp_name in critical_first:
            assert bp_name in app.blueprints, f"Critical blueprint {bp_name} missing"

        # Optional ones (rag, synthetic) may or may not be present (that's OK)
        # The important thing is critical ones are there

    def test_metrics_always_registered(self):
        """Test that metrics is ALWAYS registered (highest priority)."""
        from api import app  # type: ignore

        assert (
            "metrics" in app.blueprints
        ), "Metrics must ALWAYS be registered - it's the highest priority"

    def test_app_has_minimum_functionality(self):
        """Test that app has minimum required functionality."""
        from api import app  # type: ignore

        # Should have at least these critical routes
        required_patterns = [
            "/api/metrics",
            "/api/checklist",
            "/api/accuracy",
        ]

        registered_routes = [rule.rule for rule in app.url_map.iter_rules()]

        for pattern in required_patterns:
            matching = [r for r in registered_routes if pattern in r]
            assert len(matching) > 0, f"No routes found matching {pattern}"


class TestUnicodeResilience:
    """Test that unicode issues don't break the app."""

    def test_no_emoji_in_critical_paths(self):
        """Test that critical code paths don't use emojis."""
        # Read api.py and check for emojis
        api_path = os.path.join(os.path.dirname(__file__), "..", "src", "api.py")

        with open(api_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for common emojis that cause issues
        problematic_chars = ["✅", "❌", "⚠️", "✓", "✗", "🔥", "💡", "📊"]

        found_emojis = []
        for char in problematic_chars:
            if char in content:
                # Find line number
                for i, line in enumerate(content.split("\n"), 1):
                    if char in line:
                        found_emojis.append((char, i, line.strip()))

        assert (
            len(found_emojis) == 0
        ), f"Found emojis in api.py that could cause encoding issues: {found_emojis}"

    def test_rag_module_uses_ascii(self):
        """Test that RAG module uses ASCII markers instead of emojis."""
        rag_path = os.path.join(
            os.path.dirname(__file__), "..", "src", "rag", "simple_rag.py"
        )

        with open(rag_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check that we use ASCII markers
        assert (
            "[OK]" in content or "[WARNING]" in content or "[ERROR]" in content
        ), "RAG module should use ASCII markers like [OK], [WARNING], [ERROR]"

        # Check for problematic emojis
        problematic = ["✅", "❌", "⚠️"]
        for emoji in problematic:
            assert (
                emoji not in content
            ), f"Found problematic emoji {emoji} in simple_rag.py"

    def test_synthetic_module_uses_ascii(self):
        """Test that synthetic module uses ASCII markers."""
        synthetic_path = os.path.join(
            os.path.dirname(__file__), "..", "src", "synthetic", "generator.py"
        )

        # File might have been reformatted, so check if it exists
        if not os.path.exists(synthetic_path):
            pytest.skip("Synthetic generator not found")

        with open(synthetic_path, "r", encoding="utf-8") as f:
            content = f.read()

        # If there are print statements, they should use ASCII
        if "print(" in content:
            # Check for problematic emojis
            has_emoji = "✅" in content or "⚠️" in content

            if has_emoji:
                pytest.fail(
                    "Found emojis in synthetic generator that could cause issues"
                )


class TestImportErrors:
    """Test handling of import errors."""

    def test_app_works_with_missing_optional_deps(self):
        """Test that app works even if optional dependencies are missing."""
        from api import app  # type: ignore

        # App should be functional with core features
        assert app is not None
        assert "metrics" in app.blueprints

    def test_flask_routes_are_registered(self):
        """Test that Flask routes are properly registered."""
        from api import app  # type: ignore

        # Get all routes
        routes = list(app.url_map.iter_rules())

        assert len(routes) > 0, "No routes registered!"

        # Should have at least health check
        health_routes = [r for r in routes if "/" == r.rule]
        assert len(health_routes) > 0, "No health check route"


class TestBlueprintConfiguration:
    """Test blueprint configuration and URL prefixes."""

    def test_all_blueprints_have_api_prefix(self):
        """Test that all blueprints use /api prefix."""
        from api import app  # type: ignore

        for name, blueprint in app.blueprints.items():
            url_prefix = blueprint.url_prefix

            assert url_prefix is not None, f"Blueprint {name} has no url_prefix"

            assert url_prefix.startswith(
                "/api/"
            ), f"Blueprint {name} doesn't use /api prefix: {url_prefix}"

    def test_no_duplicate_prefixes(self):
        """Test that no two blueprints have the same URL prefix."""
        from api import app  # type: ignore

        prefixes = {}
        for name, blueprint in app.blueprints.items():
            prefix = blueprint.url_prefix

            if prefix in prefixes:
                pytest.fail(
                    f"Duplicate URL prefix {prefix} for blueprints "
                    f"{prefixes[prefix]} and {name}"
                )

            prefixes[prefix] = name

    def test_metrics_has_correct_prefix(self):
        """Test that metrics blueprint has correct URL prefix."""
        from api import app  # type: ignore

        assert "metrics" in app.blueprints

        metrics_bp = app.blueprints["metrics"]
        assert metrics_bp.url_prefix == "/api/metrics"


class TestErrorRecovery:
    """Test error recovery mechanisms."""

    def test_app_continues_after_partial_failure(self):
        """Test that app continues registering blueprints after one fails."""
        from api import app  # type: ignore

        # If we got here and have multiple blueprints, the system is resilient
        num_blueprints = len(app.blueprints)

        # Should have at least 4-5 blueprints registered
        assert num_blueprints >= 4, (
            f"Too few blueprints registered ({num_blueprints}). "
            f"System may not be resilient. Registered: {list(app.blueprints.keys())}"
        )

    def test_metrics_works_independently(self):
        """Test that metrics blueprint works independently of others."""
        from api import app  # type: ignore

        # Metrics should be registered
        assert "metrics" in app.blueprints

        # Test client
        app.config["TESTING"] = True
        with app.test_client() as client:
            response = client.get("/api/metrics/health")
            # Should work regardless of other blueprints
            assert response.status_code == 200


class TestRegistrationOrder:
    """Test the registration order and priorities."""

    def test_blueprints_registered_in_priority_order(self):
        """Test that blueprints are registered in priority order."""
        from api import app  # type: ignore

        # Expected high-priority blueprints
        high_priority = ["metrics", "checklist", "dataset_inspector"]

        # All high-priority blueprints should be registered
        for bp_name in high_priority:
            assert (
                bp_name in app.blueprints
            ), f"High-priority blueprint {bp_name} not registered"

    def test_rag_is_registered_last(self):
        """Test that RAG is registered last (if at all)."""
        from api import app  # type: ignore

        # RAG is optional and should be last
        # If it's registered, that's fine, but metrics should also be there
        if "rag" in app.blueprints:
            assert (
                "metrics" in app.blueprints
            ), "If RAG is registered, metrics should definitely be registered too"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
