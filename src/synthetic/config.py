"""Configuration for Synthetic Data Generation module."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SyntheticConfig:
    """Configuration for Synthetic Data Generation feature.
    
    Args:
        storage_path: Path to store generated datasets
        llm_provider_endpoint: Endpoint for LLM API
        llm_api_key: API key for LLM provider
        llm_model: LLM model to use for generation
        max_rows: Maximum number of rows allowed
        request_timeout: Maximum request timeout in seconds
        max_mem_mb: Maximum memory usage in MB
        rate_limit: Rate limit in requests per minute
    """
    
    storage_path: Path = Path("./storage/synth")
    llm_provider_endpoint: Optional[str] = None
    llm_api_key: str = ""
    llm_model: str = "claude-3-haiku-20240307"
    max_rows: int = 1_000_000
    request_timeout: int = 300
    max_mem_mb: int = 2048
    rate_limit: int = 60
    
    @classmethod
    def from_env(cls) -> "SyntheticConfig":
        """Create config from environment variables."""
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Get storage path and make it absolute
        storage_path = os.getenv("SYNTH_STORAGE_PATH", "./storage/synth")
        if not os.path.isabs(storage_path):
            # Make it relative to the project root
            project_root = Path(__file__).parent.parent.parent
            storage_path = project_root / storage_path
        
        return cls(
            storage_path=Path(storage_path),
            llm_provider_endpoint=os.getenv("LLM_PROVIDER_ENDPOINT"),
            llm_api_key=os.getenv("LLM_API_KEY", ""),
            llm_model=os.getenv("LLM_MODEL", "claude-3-haiku-20240307"),
            max_rows=int(os.getenv("SYNTH_MAX_ROWS", "1000000")),
            request_timeout=int(os.getenv("SYNTH_REQUEST_TIMEOUT", "300")),
            max_mem_mb=int(os.getenv("SYNTH_MAX_MEM_MB", "2048")),
            rate_limit=int(os.getenv("SYNTH_RATE_LIMIT", "60")),
        )
