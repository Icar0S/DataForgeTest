"""Simple RAG configuration without complex dependencies."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List
import os


@dataclass
class RAGConfig:
    """Simple RAG configuration."""

    storage_path: Path = Path("./storage/vectorstore")
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 4
    max_upload_mb: int = 10
    allowed_file_types: List[str] = field(
        default_factory=lambda: [".pdf", ".txt", ".md", ".csv", ".docx"]
    )

    @classmethod
    def from_env(cls) -> "RAGConfig":
        """Create config from environment variables."""
        from dotenv import load_dotenv

        load_dotenv()

        return cls(
            storage_path=Path(os.getenv("VECTOR_STORE_PATH", "./storage/vectorstore")),
            chunk_size=int(os.getenv("CHUNK_SIZE", "512")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
            top_k=int(os.getenv("TOP_K", "4")),
            max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", "10")),
        )
