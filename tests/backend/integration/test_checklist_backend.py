"""Tests for Checklist Support QA backend."""

import sys
import os
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from src.checklist.models import (
    ChecklistTemplate,
    ChecklistDimension,
    ChecklistItem,
    ChecklistRun,
    ItemStatus,
    template_from_dict,
    template_to_dict,
    run_from_dict,
    run_to_dict,
)
from src.checklist.storage import ChecklistStorage, load_template
from src.checklist.reports import generate_markdown_report, generate_pdf_report


class TestModels:
    """Test data models."""

    def test_item_status_enum(self):
        """Test ItemStatus enum."""
        assert ItemStatus.DONE.value == "DONE"
        assert ItemStatus.NOT_DONE.value == "NOT_DONE"

    def test_checklist_item_creation(self):
        """Test ChecklistItem creation."""
        item = ChecklistItem(
            id="TEST_1",
            code="TEST_1",
            title="Test item",
            manual="Test manual",
            references=["[1]", "[2]"],
            priority_weight=3,
        )

        assert item.id == "TEST_1"
        assert item.code == "TEST_1"
        assert item.priority_weight == 3

    def test_template_conversion(self):
        """Test template to/from dict conversion."""
        item = ChecklistItem(
            id="TEST_1",
            code="TEST_1",
            title="Test item",
            manual="Test manual",
            references=["[1]"],
            priority_weight=2,
        )

        dimension = ChecklistDimension(
            id="test_dim", name="Test Dimension", items=[item]
        )

        template = ChecklistTemplate(name="Test Template", dimensions=[dimension])

        # Convert to dict
        data = template_to_dict(template)
        assert data["name"] == "Test Template"
        assert len(data["dimensions"]) == 1
        assert len(data["dimensions"][0]["items"]) == 1

        # Convert back
        template2 = template_from_dict(data)
        assert template2.name == template.name
        assert len(template2.dimensions) == 1
        assert template2.dimensions[0].items[0].id == "TEST_1"

    def test_run_conversion(self):
        """Test run to/from dict conversion."""
        run = ChecklistRun(id="run123", user_id="user456", project_id="proj789")
        run.marks["ITEM_1"] = ItemStatus.DONE
        run.marks["ITEM_2"] = ItemStatus.NOT_DONE

        # Convert to dict
        data = run_to_dict(run)
        assert data["id"] == "run123"
        assert data["user_id"] == "user456"
        assert data["marks"]["ITEM_1"] == "DONE"

        # Convert back
        run2 = run_from_dict(data)
        assert run2.id == run.id
        assert run2.marks["ITEM_1"] == ItemStatus.DONE


class TestStorage:
    """Test storage operations."""

    @pytest.fixture
    def temp_storage(self, tmp_path):
        """Create temporary storage."""
        return ChecklistStorage(tmp_path)

    def test_create_run(self, temp_storage):
        """Test creating a run."""
        run = temp_storage.create_run("user123", "proj456")

        assert run.id is not None
        assert run.user_id == "user123"
        assert run.project_id == "proj456"
        assert len(run.marks) == 0

    def test_get_run(self, temp_storage):
        """Test getting a run."""
        run1 = temp_storage.create_run("user123")

        run2 = temp_storage.get_run(run1.id)
        assert run2 is not None
        assert run2.id == run1.id
        assert run2.user_id == "user123"

    def test_get_nonexistent_run(self, temp_storage):
        """Test getting a non-existent run."""
        run = temp_storage.get_run("nonexistent")
        assert run is None

    def test_update_run(self, temp_storage):
        """Test updating a run."""
        run = temp_storage.create_run("user123")

        marks = {"ITEM_1": "DONE", "ITEM_2": "NOT_DONE"}

        updated_run = temp_storage.update_run(run.id, marks)

        assert updated_run is not None
        assert len(updated_run.marks) == 2
        assert updated_run.marks["ITEM_1"] == ItemStatus.DONE
        assert updated_run.marks["ITEM_2"] == ItemStatus.NOT_DONE

    def test_update_nonexistent_run(self, temp_storage):
        """Test updating a non-existent run."""
        updated = temp_storage.update_run("nonexistent", {})
        assert updated is None


class TestTemplate:
    """Test template loading."""

    def test_load_template(self):
        """Test loading the seed template."""
        template = load_template()

        assert template.name == "Big Data QA Checklist (DataForgeTest)"
        assert len(template.dimensions) > 0

        # Check first dimension
        assert template.dimensions[0].id == "unit_integration"
        assert template.dimensions[0].name == "Unit & Integration"
        assert len(template.dimensions[0].items) > 0

        # Check first item
        item = template.dimensions[0].items[0]
        assert item.id == "UNIT_1"
        assert item.code == "UNIT_1"
        assert item.priority_weight == 2
        assert len(item.references) > 0


class TestReports:
    """Test report generation."""

    @pytest.fixture
    def sample_run(self):
        """Create a sample run with some marks."""
        run = ChecklistRun(id="run123", user_id="user456", project_id="proj789")
        run.marks["UNIT_1"] = ItemStatus.DONE
        run.marks["FUNC_1"] = ItemStatus.NOT_DONE
        return run

    @pytest.fixture
    def sample_template(self):
        """Create a sample template."""
        return load_template()

    def test_generate_markdown_report(self, sample_run, sample_template):
        """Test Markdown report generation."""
        md = generate_markdown_report(sample_run, sample_template)

        assert "Big Data QA Checklist" in md
        assert "Resumo" in md
        assert "Cobertura por Dimensão" in md
        assert "Manual Completo" in md
        assert "user456" in md

    def test_generate_pdf_report(self, sample_run, sample_template):
        """Test PDF report generation."""
        pdf_buffer = generate_pdf_report(sample_run, sample_template)

        assert pdf_buffer is not None
        assert pdf_buffer.tell() == 0  # Buffer is at start

        # Read some content
        content = pdf_buffer.read(100)
        assert len(content) > 0
        assert content[:4] == b"%PDF"  # PDF magic number

    def test_markdown_with_recommendations(self, sample_run, sample_template):
        """Test Markdown report with recommendations."""
        recommendations = [
            {
                "title": "Test Recommendation",
                "content": "This is a test recommendation",
                "sources": ["[1]", "[2]"],
            }
        ]

        md = generate_markdown_report(sample_run, sample_template, recommendations)

        assert "Recomendações (LLM + RAG)" in md
        assert "Test Recommendation" in md
        assert "This is a test recommendation" in md


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
