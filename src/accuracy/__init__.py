"""Data Accuracy module for comparing and correcting datasets."""

from .config import AccuracyConfig
from .processor import (
    normalize_column_name,
    strip_accents,
    normalize_key_value,
    coerce_numeric,
    read_dataset,
    handle_duplicates,
    compare_and_correct
)
from .routes import accuracy_bp

__all__ = [
    "AccuracyConfig",
    "accuracy_bp",
    "normalize_column_name",
    "strip_accents",
    "normalize_key_value",
    "coerce_numeric",
    "read_dataset",
    "handle_duplicates",
    "compare_and_correct"
]
