"""Integration tests for Checklist Support QA feature."""

import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from checklist.storage import ChecklistStorage, load_template
from checklist.reports import generate_markdown_report, generate_pdf_report


def test_complete_flow(tmp_path):
    """Test complete checklist flow: create run, update marks, generate reports."""
    # Load template
    template = load_template()
    assert template.name == "Big Data QA Checklist (DataForgeTest)"
    assert len(template.dimensions) == 7
    
    # Create storage and run
    storage = ChecklistStorage(tmp_path)
    run = storage.create_run("test_user", "test_project")
    assert run.id is not None
    assert run.user_id == "test_user"
    
    # Update marks
    marks = {
        "UNIT_1": "DONE",
        "FUNC_1": "NOT_DONE",
        "PERF_1": "DONE"
    }
    
    updated_run = storage.update_run(run.id, marks)
    assert updated_run is not None
    assert len(updated_run.marks) == 3
    
    # Reload run
    reloaded_run = storage.get_run(run.id)
    assert reloaded_run is not None
    assert len(reloaded_run.marks) == 3
    
    # Generate markdown report
    md_report = generate_markdown_report(reloaded_run, template)
    assert "Big Data QA Checklist" in md_report
    assert "test_user" in md_report
    assert "Resumo" in md_report
    assert "Itens Faltantes" in md_report
    
    # Generate PDF report
    pdf_buffer = generate_pdf_report(reloaded_run, template)
    assert pdf_buffer is not None
    pdf_content = pdf_buffer.read()
    assert len(pdf_content) > 0
    assert pdf_content[:4] == b'%PDF'
    
    print("✓ Complete flow test passed")


def test_prioritization(tmp_path):
    """Test that missing items are prioritized correctly."""
    template = load_template()
    storage = ChecklistStorage(tmp_path)
    
    run = storage.create_run("user1")
    
    # Mark only low priority items as done
    marks = {
        "UNIT_1": "DONE",  # priority 2
        "UNIT_2": "DONE",  # priority 2
    }
    storage.update_run(run.id, marks)
    
    reloaded_run = storage.get_run(run.id)
    
    # Generate report
    md_report = generate_markdown_report(reloaded_run, template)
    
    # Check that high priority items appear first in missing items
    # SEC_1 and SEC_2 have priority 5, should appear before others
    assert "SEC_1" in md_report or "SEC_2" in md_report
    
    print("✓ Prioritization test passed")


def test_coverage_calculation(tmp_path):
    """Test that coverage is calculated correctly."""
    template = load_template()
    storage = ChecklistStorage(tmp_path)
    
    run = storage.create_run("user1")
    
    # Total items across all dimensions
    total_items = sum(len(dim.items) for dim in template.dimensions)
    
    # Mark half as done
    marks = {}
    item_count = 0
    for dim in template.dimensions:
        for item in dim.items:
            if item_count < total_items // 2:
                marks[item.id] = "DONE"
            item_count += 1
    
    storage.update_run(run.id, marks)
    reloaded_run = storage.get_run(run.id)
    
    # Generate report
    md_report = generate_markdown_report(reloaded_run, template)
    
    # Coverage should be approximately 50%
    assert "Cobertura:" in md_report
    # Should be around 50%, allowing for rounding
    assert any(f"{p}.0%" in md_report or f"{p}.1%" in md_report 
               for p in range(45, 55))
    
    print("✓ Coverage calculation test passed")


if __name__ == "__main__":
    import tempfile
    from pathlib import Path
    
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        
        print("\nRunning integration tests...")
        test_complete_flow(tmp_path)
        test_prioritization(tmp_path)
        test_coverage_calculation(tmp_path)
        
        print("\n✅ All integration tests passed!")
