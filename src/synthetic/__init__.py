"""Synthetic Dataset Generation module.

This module provides LLM-based synthetic data generation functionality.
"""

from .config import SyntheticConfig
from .generator import SyntheticDataGenerator
from .routes import synth_bp

__all__ = ["SyntheticConfig", "SyntheticDataGenerator", "synth_bp"]
