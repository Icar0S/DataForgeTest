"""Configuration for Metrics feature."""

import os
from pathlib import Path
from typing import Set


class MetricsConfig:
    """Configuration for metrics processing."""

    def __init__(
        self,
        storage_path: Path = Path("./uploads/metrics"),
        max_upload_mb: int = 50,
        allowed_file_types: Set[str] = None,
        sample_size: int = 10,
    ):
        """Initialize configuration.

        Args:
            storage_path: Path to store uploaded files
            max_upload_mb: Maximum file size in MB
            allowed_file_types: Set of allowed file extensions
            sample_size: Number of rows to sample for preview
        """
        self.storage_path = storage_path
        self.max_upload_mb = max_upload_mb
        self.allowed_file_types = allowed_file_types or {
            ".csv",
            ".xlsx",
            ".xls",
            ".parquet",
        }
        self.sample_size = sample_size

    @classmethod
    def from_env(cls) -> "MetricsConfig":
        """Create configuration from environment variables."""
        return cls(
            storage_path=Path(os.getenv("METRICS_STORAGE_PATH", "./uploads/metrics")),
            max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", "50")),
            sample_size=int(os.getenv("METRICS_SAMPLE_SIZE", "10")),
        )
