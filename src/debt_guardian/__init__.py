"""
DebtGuardian - LLM-based Technical Debt Detection Framework

This module implements the DebtGuardian framework for detecting technical debt
in source code changes using Large Language Models (LLMs).

Based on the paper: "Detecting Technical Debt in Source Code Changes using Large Language Models"
"""

__version__ = "0.1.0"
__author__ = "DataForgeTest Team"

from .config import DebtGuardianConfig
from .detector import DebtDetector

__all__ = ['DebtGuardianConfig', 'DebtDetector']
