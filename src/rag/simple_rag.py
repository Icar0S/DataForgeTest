"""Simple RAG implementation using basic vector search."""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional


class SimpleRAG:
    """Simple RAG implementation without complex dependencies."""

    def __init__(self, config):
        """Initialize simple RAG."""
        self.config = config
        self.storage_path = Path(config.storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Simple in-memory storage for documents
        self.documents = {}
        self.document_chunks = {}

        # Load existing documents
        self._load_documents()

    def _load_documents(self):
        """Load documents from storage."""
        docs_file = self.storage_path / "documents.json"
        if docs_file.exists():
            try:
                with open(docs_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.documents = data.get("documents", {})
                    self.document_chunks = data.get("chunks", {})
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Error loading documents: {e}")

    def _save_documents(self):
        """Save documents to storage."""
        docs_file = self.storage_path / "documents.json"
        try:
            with open(docs_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"documents": self.documents, "chunks": self.document_chunks},
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error saving documents: {e}")

    def add_document(self, content: str, metadata: Dict) -> str:
        """Add a document to the RAG system."""
        doc_id = str(uuid.uuid4())

        # Store document
        self.documents[doc_id] = {
            "content": content,
            "metadata": metadata,
            "id": doc_id,
        }

        # Create chunks
        chunks = self._create_chunks(content)
        self.document_chunks[doc_id] = chunks

        # Save to storage
        self._save_documents()

        return doc_id

    def _create_chunks(self, text: str) -> List[Dict]:
        """Create simple text chunks."""
        chunks = []
        words = text.split()

        # Simple chunking by word count
        chunk_size_words = self.config.chunk_size // 4  # Rough estimate
        overlap_words = self.config.chunk_overlap // 4

        for i in range(0, len(words), chunk_size_words - overlap_words):
            chunk_words = words[i : i + chunk_size_words]
            chunk_text = " ".join(chunk_words)

            chunks.append(
                {
                    "text": chunk_text,
                    "start_idx": i,
                    "end_idx": min(i + chunk_size_words, len(words)),
                }
            )

        return chunks

    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """Simple keyword-based search."""
        if top_k is None:
            top_k = self.config.top_k

        results = []
        query_words = set(query.lower().split())

        for doc_id, chunks in self.document_chunks.items():
            doc_metadata = self.documents[doc_id]["metadata"]

            for chunk in chunks:
                chunk_words = set(chunk["text"].lower().split())

                # Simple similarity score based on word overlap
                overlap = len(query_words.intersection(chunk_words))
                if overlap > 0:
                    score = overlap / len(query_words.union(chunk_words))

                    results.append(
                        {
                            "text": chunk["text"],
                            "score": score,
                            "doc_id": doc_id,
                            "metadata": doc_metadata,
                        }
                    )

        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def get_sources(self) -> List[Dict]:
        """Get information about all documents."""
        return [
            {
                "id": doc_id,
                "filename": doc["metadata"].get("filename", "unknown"),
                "size": doc["metadata"].get("size", 0),
            }
            for doc_id, doc in self.documents.items()
        ]

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            if doc_id in self.document_chunks:
                del self.document_chunks[doc_id]
            self._save_documents()
            return True
        return False
