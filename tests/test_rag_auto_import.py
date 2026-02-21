"""Tests for SimpleRAG auto-import from docs_to_import folder."""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Allow imports from the src directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from rag.config_simple import RAGConfig  # noqa: E402
from rag.simple_rag import SimpleRAG  # noqa: E402


def _make_config(storage_path: str) -> RAGConfig:
    config = RAGConfig()
    config.storage_path = Path(storage_path)
    return config


class TestAutoImportFromDocsFolder:
    """SimpleRAG auto-imports docs_to_import when no documents.json exists."""

    def test_auto_import_txt_and_md(self, tmp_path):
        """Documents are imported from txt/md files when storage is empty."""
        # Create a fake docs_to_import dir with two plain text files
        docs_dir = tmp_path / "docs_to_import"
        docs_dir.mkdir()
        (docs_dir / "guide.txt").write_text("Data quality guide: be accurate.", encoding="utf-8")
        (docs_dir / "notes.md").write_text("# Notes\nValidation is important.", encoding="utf-8")

        storage_dir = tmp_path / "storage" / "vectorstore"
        storage_dir.mkdir(parents=True)

        config = _make_config(str(storage_dir))
        rag = SimpleRAG.__new__(SimpleRAG)
        rag.config = config
        rag.storage_path = storage_dir
        rag.documents = {}
        rag.document_chunks = {}

        # Point _find_docs_to_import to our fake dir by patching
        original_find = SimpleRAG._find_docs_to_import

        def _mock_find(_instance):  # pylint: disable=unused-argument
            return docs_dir

        SimpleRAG._find_docs_to_import = _mock_find
        try:
            rag._auto_import_or_fallback()
        finally:
            SimpleRAG._find_docs_to_import = original_find

        assert len(rag.documents) == 2
        filenames = {d["metadata"]["filename"] for d in rag.documents.values()}
        assert "guide.txt" in filenames
        assert "notes.md" in filenames

    def test_auto_import_creates_chunks(self, tmp_path):
        """Chunks are generated for every imported document."""
        docs_dir = tmp_path / "docs_to_import"
        docs_dir.mkdir()
        (docs_dir / "spark.txt").write_text(
            "Apache Spark is a distributed computing framework " * 30,
            encoding="utf-8",
        )

        storage_dir = tmp_path / "storage" / "vectorstore"
        storage_dir.mkdir(parents=True)

        config = _make_config(str(storage_dir))
        rag = SimpleRAG.__new__(SimpleRAG)
        rag.config = config
        rag.storage_path = storage_dir
        rag.documents = {}
        rag.document_chunks = {}

        original_find = SimpleRAG._find_docs_to_import

        def _mock_find(_instance):
            return docs_dir

        SimpleRAG._find_docs_to_import = _mock_find
        try:
            rag._auto_import_or_fallback()
        finally:
            SimpleRAG._find_docs_to_import = original_find

        assert len(rag.document_chunks) == 1
        doc_id = next(iter(rag.document_chunks))
        assert len(rag.document_chunks[doc_id]) > 0

    def test_auto_import_saves_documents_json(self, tmp_path):
        """documents.json is written to storage after auto-import."""
        docs_dir = tmp_path / "docs_to_import"
        docs_dir.mkdir()
        (docs_dir / "info.txt").write_text("RAG information here.", encoding="utf-8")

        storage_dir = tmp_path / "storage" / "vectorstore"
        storage_dir.mkdir(parents=True)

        config = _make_config(str(storage_dir))
        rag = SimpleRAG.__new__(SimpleRAG)
        rag.config = config
        rag.storage_path = storage_dir
        rag.documents = {}
        rag.document_chunks = {}

        original_find = SimpleRAG._find_docs_to_import

        def _mock_find(_instance):
            return docs_dir

        SimpleRAG._find_docs_to_import = _mock_find
        try:
            rag._auto_import_or_fallback()
        finally:
            SimpleRAG._find_docs_to_import = original_find

        docs_file = storage_dir / "documents.json"
        assert docs_file.exists(), "documents.json should be saved after auto-import"
        data = json.loads(docs_file.read_text(encoding="utf-8"))
        assert "documents" in data
        assert "chunks" in data
        assert len(data["documents"]) == 1

    def test_fallback_used_when_no_docs_folder(self, tmp_path):
        """Hardcoded fallback docs are loaded when docs_to_import is absent."""
        storage_dir = tmp_path / "storage" / "vectorstore"
        storage_dir.mkdir(parents=True)

        config = _make_config(str(storage_dir))
        rag = SimpleRAG.__new__(SimpleRAG)
        rag.config = config
        rag.storage_path = storage_dir
        rag.documents = {}
        rag.document_chunks = {}

        original_find = SimpleRAG._find_docs_to_import

        def _mock_find(_instance):
            return None  # simulate no docs_to_import folder

        SimpleRAG._find_docs_to_import = _mock_find
        try:
            rag._auto_import_or_fallback()
        finally:
            SimpleRAG._find_docs_to_import = original_find

        # Should have fallback documents
        assert len(rag.documents) > 0

    def test_load_documents_rebuilds_missing_chunks(self, tmp_path):
        """Missing chunks are rebuilt from document content when loading."""
        storage_dir = tmp_path / "storage" / "vectorstore"
        storage_dir.mkdir(parents=True)

        # Write a documents.json without 'chunks' (as imported by the utility script)
        docs_data = {
            "documents": {
                "abc123": {
                    "id": "abc123",
                    "content": "Data validation ensures quality " * 20,
                    "metadata": {"filename": "test.txt", "size": 100},
                }
            }
        }
        docs_file = storage_dir / "documents.json"
        docs_file.write_text(json.dumps(docs_data), encoding="utf-8")

        config = _make_config(str(storage_dir))
        rag = SimpleRAG(config)

        assert "abc123" in rag.document_chunks
        assert len(rag.document_chunks["abc123"]) > 0

    def test_search_works_after_auto_import(self, tmp_path):
        """Search returns relevant results after auto-import."""
        docs_dir = tmp_path / "docs_to_import"
        docs_dir.mkdir()
        (docs_dir / "spark.txt").write_text(
            "Apache Spark is used for big data processing and distributed computing.",
            encoding="utf-8",
        )
        (docs_dir / "quality.txt").write_text(
            "Data quality refers to accuracy, completeness, and consistency of data.",
            encoding="utf-8",
        )

        storage_dir = tmp_path / "storage" / "vectorstore"
        storage_dir.mkdir(parents=True)

        config = _make_config(str(storage_dir))
        rag = SimpleRAG.__new__(SimpleRAG)
        rag.config = config
        rag.storage_path = storage_dir
        rag.documents = {}
        rag.document_chunks = {}

        original_find = SimpleRAG._find_docs_to_import

        def _mock_find(_instance):
            return docs_dir

        SimpleRAG._find_docs_to_import = _mock_find
        try:
            rag._auto_import_or_fallback()
        finally:
            SimpleRAG._find_docs_to_import = original_find

        results = rag.search("data quality")
        assert len(results) > 0
        assert any("quality" in r["text"].lower() for r in results)
