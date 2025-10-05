"""Tests for synthetic data generation backend."""

import pytest
from src.synthetic.validators import (
    validate_schema,
    validate_generate_request,
    validate_preview_request,
)
from src.synthetic.generator import SyntheticDataGenerator


class TestValidators:
    """Test validation functions."""

    def test_validate_schema_valid(self):
        """Test valid schema validation."""
        schema = {
            "columns": [
                {"name": "id", "type": "integer", "options": {"min": 1, "max": 100}},
                {"name": "name", "type": "string", "options": {}},
                {"name": "email", "type": "email", "options": {}},
            ]
        }
        is_valid, errors = validate_schema(schema)
        assert is_valid
        assert len(errors) == 0

    def test_validate_schema_missing_columns(self):
        """Test schema validation with missing columns."""
        schema = {}
        is_valid, errors = validate_schema(schema)
        assert not is_valid
        assert len(errors) > 0  # Just verify there are errors

    def test_validate_schema_empty_columns(self):
        """Test schema validation with empty columns."""
        schema = {"columns": []}
        is_valid, errors = validate_schema(schema)
        assert not is_valid
        assert any("at least one column" in err.lower() for err in errors)

    def test_validate_schema_duplicate_names(self):
        """Test schema validation with duplicate column names."""
        schema = {
            "columns": [
                {"name": "id", "type": "integer"},
                {"name": "id", "type": "string"},
            ]
        }
        is_valid, errors = validate_schema(schema)
        assert not is_valid
        assert any("duplicate" in err.lower() for err in errors)

    def test_validate_schema_unsupported_type(self):
        """Test schema validation with unsupported type."""
        schema = {"columns": [{"name": "test", "type": "unsupported_type"}]}
        is_valid, errors = validate_schema(schema)
        assert not is_valid
        assert any("unsupported type" in err.lower() for err in errors)

    def test_validate_schema_invalid_numeric_range(self):
        """Test schema validation with invalid numeric range."""
        schema = {
            "columns": [
                {"name": "value", "type": "integer", "options": {"min": 100, "max": 10}}
            ]
        }
        is_valid, errors = validate_schema(schema)
        assert not is_valid
        assert any("min must be less than max" in err.lower() for err in errors)

    def test_validate_schema_missing_date_options(self):
        """Test schema validation with missing date options."""
        schema = {"columns": [{"name": "created", "type": "date", "options": {}}]}
        is_valid, errors = validate_schema(schema)
        assert not is_valid
        assert any("start" in err.lower() and "end" in err.lower() for err in errors)

    def test_validate_generate_request_valid(self):
        """Test valid generate request."""
        request = {
            "schema": {"columns": [{"name": "id", "type": "integer", "options": {}}]},
            "rows": 1000,
            "fileType": "csv",
        }
        is_valid, errors = validate_generate_request(request, max_rows=1000000)
        assert is_valid
        assert len(errors) == 0

    def test_validate_generate_request_exceeds_max_rows(self):
        """Test generate request exceeding max rows."""
        request = {
            "schema": {"columns": [{"name": "id", "type": "integer", "options": {}}]},
            "rows": 2000000,
            "fileType": "csv",
        }
        is_valid, errors = validate_generate_request(request, max_rows=1000000)
        assert not is_valid
        assert any("1,000,000" in err for err in errors)

    def test_validate_generate_request_invalid_file_type(self):
        """Test generate request with invalid file type."""
        request = {
            "schema": {"columns": [{"name": "id", "type": "integer", "options": {}}]},
            "rows": 1000,
            "fileType": "invalid",
        }
        is_valid, errors = validate_generate_request(request, max_rows=1000000)
        assert not is_valid
        assert any("unsupported file type" in err.lower() for err in errors)

    def test_validate_preview_request_valid(self):
        """Test valid preview request."""
        request = {
            "schema": {"columns": [{"name": "id", "type": "integer", "options": {}}]},
            "rows": 50,
        }
        is_valid, errors = validate_preview_request(request)
        assert is_valid
        assert len(errors) == 0

    def test_validate_preview_request_too_many_rows(self):
        """Test preview request with too many rows."""
        request = {
            "schema": {"columns": [{"name": "id", "type": "integer", "options": {}}]},
            "rows": 200,
        }
        is_valid, errors = validate_preview_request(request)
        assert not is_valid
        assert any("between 1 and 100" in err.lower() for err in errors)


class TestSyntheticDataGenerator:
    """Test SyntheticDataGenerator class."""

    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = SyntheticDataGenerator(api_key="test-key", model="test-model")
        assert generator.api_key == "test-key"
        assert generator.model == "test-model"

    def test_build_prompt(self):
        """Test prompt building."""
        generator = SyntheticDataGenerator(api_key="test-key")
        schema = {
            "columns": [
                {"name": "id", "type": "integer", "options": {"min": 1, "max": 100}},
                {"name": "name", "type": "string", "options": {}},
            ]
        }

        prompt = generator._build_prompt(schema, 10, locale="pt_BR", seed=42)

        assert "10 rows" in prompt
        assert "id" in prompt
        assert "name" in prompt
        assert "pt_BR" in prompt
        assert "seed 42" in prompt

    def test_parse_csv_response(self):
        """Test CSV response parsing."""
        generator = SyntheticDataGenerator(api_key="test-key")

        csv_text = """1,John,john@example.com
2,Jane,jane@example.com
3,Bob,bob@example.com"""

        rows = generator._parse_csv_response(csv_text, num_columns=3)

        assert len(rows) == 3
        assert rows[0] == ["1", "John", "john@example.com"]
        assert rows[1] == ["2", "Jane", "jane@example.com"]

    def test_parse_csv_response_with_markdown(self):
        """Test CSV response parsing with markdown code blocks."""
        generator = SyntheticDataGenerator(api_key="test-key")

        csv_text = """```csv
1,John,john@example.com
2,Jane,jane@example.com
```"""

        rows = generator._parse_csv_response(csv_text, num_columns=3)

        assert len(rows) == 2
        assert rows[0] == ["1", "John", "john@example.com"]

    def test_coerce_types(self):
        """Test type coercion."""
        generator = SyntheticDataGenerator(api_key="test-key")

        schema = {
            "columns": [
                {"name": "id", "type": "integer"},
                {"name": "price", "type": "float"},
                {"name": "active", "type": "boolean"},
                {"name": "name", "type": "string"},
            ]
        }

        rows = [
            ["1", "19.99", "true", "Product A"],
            ["2", "29.99", "false", "Product B"],
        ]

        records = generator._coerce_types(rows, schema)

        assert len(records) == 2
        assert records[0]["id"] == 1
        assert records[0]["price"] == pytest.approx(19.99)
        assert records[0]["active"] is True
        assert records[0]["name"] == "Product A"
        assert records[1]["active"] is False

    def test_enforce_uniqueness(self):
        """Test uniqueness enforcement."""
        generator = SyntheticDataGenerator(api_key="test-key")

        schema = {
            "columns": [
                {"name": "id", "type": "integer", "options": {"unique": True}},
                {"name": "name", "type": "string"},
            ]
        }

        records = [
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"},
            {"id": 1, "name": "C"},  # Duplicate ID
            {"id": 3, "name": "D"},
        ]

        unique_records = generator._enforce_uniqueness(records, schema)

        assert len(unique_records) == 3  # Duplicate removed
        ids = [r["id"] for r in unique_records]
        assert ids == [1, 2, 3]

    def test_generate_mock_data(self):
        """Test mock data generation."""
        generator = SyntheticDataGenerator(api_key="")  # No API key

        schema = {
            "columns": [
                {"name": "id", "type": "integer", "options": {"min": 1, "max": 100}},
                {"name": "price", "type": "price", "options": {"min": 10, "max": 100}},
                {"name": "active", "type": "boolean"},
                {"name": "created", "type": "date"},
            ]
        }

        records = generator._generate_mock_data(schema, 10)

        assert len(records) == 10
        assert all("id" in r for r in records)
        assert all("price" in r for r in records)
        assert all("active" in r for r in records)
        assert all("created" in r for r in records)

        # Check types
        assert all(isinstance(r["id"], int) for r in records)
        assert all(isinstance(r["price"], float) for r in records)
        assert all(isinstance(r["active"], bool) for r in records)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
