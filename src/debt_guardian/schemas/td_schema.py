"""
Pydantic schemas for Technical Debt detection.

These schemas define the structure of TD instances as described in the paper.
They are used for both LLM output validation and Guardrails-AI integration.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class TechnicalDebtType:
    """
    Technical Debt type definitions based on MLCQ dataset.
    """
    DESIGN = "design"
    DOCUMENTATION = "documentation"
    DEFECT = "defect"
    TEST = "test"
    COMPATIBILITY = "compatibility"
    BUILD = "build"
    REQUIREMENT = "requirement"
    
    @classmethod
    def all_types(cls) -> List[str]:
        return [
            cls.DESIGN,
            cls.DOCUMENTATION,
            cls.DEFECT,
            cls.TEST,
            cls.COMPATIBILITY,
            cls.BUILD,
            cls.REQUIREMENT
        ]


class CodeLocation(BaseModel):
    """
    Location of technical debt in the code.
    """
    file_path: str = Field(
        description="Path to the file containing the debt"
    )
    start_line: int = Field(
        description="Starting line number of the debt",
        ge=1
    )
    end_line: int = Field(
        description="Ending line number of the debt",
        ge=1
    )
    
    @field_validator('end_line')
    @classmethod
    def validate_line_range(cls, v, info):
        if 'start_line' in info.data and v < info.data['start_line']:
            raise ValueError('end_line must be >= start_line')
        return v


class TechnicalDebtInstance(BaseModel):
    """
    Single instance of technical debt.
    
    This schema aligns with the structure described in Figure 2 of the paper.
    """
    debt_type: Literal[
        "design", "documentation", "defect", "test", 
        "compatibility", "build", "requirement"
    ] = Field(
        description="Type of technical debt detected"
    )
    
    symptom: str = Field(
        description="Description of the debt symptom or indicator",
        min_length=10
    )
    
    location: CodeLocation = Field(
        description="Location in the code where debt was found"
    )
    
    severity: Literal["low", "medium", "high", "critical"] = Field(
        default="medium",
        description="Severity level of the technical debt"
    )
    
    confidence: float = Field(
        default=0.8,
        description="Confidence score of the detection (0-1)",
        ge=0.0,
        le=1.0
    )
    
    suggested_remediation: Optional[str] = Field(
        default=None,
        description="Suggested approach to resolve the debt"
    )
    
    code_snippet: Optional[str] = Field(
        default=None,
        description="The problematic code snippet"
    )


class TechnicalDebtReport(BaseModel):
    """
    Complete report of technical debt detection for a code change.
    """
    commit_sha: Optional[str] = Field(
        default=None,
        description="Git commit SHA if analyzing committed changes"
    )
    
    file_path: str = Field(
        description="Path to the analyzed file"
    )
    
    detected_debts: List[TechnicalDebtInstance] = Field(
        default_factory=list,
        description="List of detected technical debt instances"
    )
    
    analysis_timestamp: str = Field(
        description="ISO timestamp of when analysis was performed"
    )
    
    model_used: str = Field(
        description="LLM model used for detection"
    )
    
    prompting_strategy: str = Field(
        description="Prompting strategy used (zero-shot, few-shot, etc.)"
    )
    
    total_lines_analyzed: int = Field(
        default=0,
        description="Total number of lines analyzed",
        ge=0
    )
    
    @property
    def debt_count(self) -> int:
        """Total number of detected debts"""
        return len(self.detected_debts)
    
    @property
    def debt_by_type(self) -> dict:
        """Count of debts by type"""
        result = {}
        for debt in self.detected_debts:
            result[debt.debt_type] = result.get(debt.debt_type, 0) + 1
        return result
    
    @property
    def high_severity_count(self) -> int:
        """Count of high/critical severity debts"""
        return sum(
            1 for debt in self.detected_debts 
            if debt.severity in ["high", "critical"]
        )


class BatchDebtReport(BaseModel):
    """
    Batch report for multiple files or commits.
    """
    reports: List[TechnicalDebtReport] = Field(
        default_factory=list,
        description="Individual reports for each analyzed file"
    )
    
    summary: dict = Field(
        default_factory=dict,
        description="Summary statistics across all reports"
    )
    
    @property
    def total_debts(self) -> int:
        """Total debts across all reports"""
        return sum(report.debt_count for report in self.reports)
    
    @property
    def total_files(self) -> int:
        """Total files analyzed"""
        return len(self.reports)
