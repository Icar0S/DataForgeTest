"""Configuration for RAG system."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class RAGConfig:
    """Configuration for RAG system.

    Args:
        storage_path: Path to store vector index
        llm_api_key: API key for LLM provider
        llm_model: Name of LLM model to use
        embed_model: Name of embedding model
        chunk_size: Size of text chunks for indexing
        chunk_overlap: Overlap between chunks
        top_k: Number of chunks to retrieve
        max_upload_mb: Maximum upload file size in MB
        allowed_file_types: List of allowed file extensions
    """

    storage_path: Path = Path("./storage/vectorstore")
    llm_api_key: str = ""
    llm_model: str = "llama-3-instruct"
    embed_model: str = "text-embedding-3-large"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 4
    max_upload_mb: int = 10
    allowed_file_types: List[str] = [".pdf", ".txt", ".md", ".csv"]

    @classmethod
    def from_env(cls) -> "RAGConfig":
        """Create config from environment variables."""
        import os
        from dotenv import load_dotenv

        load_dotenv()

        return cls(
            storage_path=Path(os.getenv("VECTOR_STORE_PATH", "./storage/vectorstore")),
            llm_api_key=os.getenv("LLM_API_KEY", ""),
            llm_model=os.getenv("LLM_MODEL", "llama-3-instruct"),
            embed_model=os.getenv("EMBED_MODEL", "text-embedding-3-large"),
            chunk_size=int(os.getenv("CHUNK_SIZE", "512")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
            top_k=int(os.getenv("TOP_K", "4")),
            max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", "10")),
            allowed_file_types=os.getenv(
                "ALLOWED_FILE_TYPES", ".pdf,.txt,.md,.csv"
            ).split(","),
        )
