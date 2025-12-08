"""
Output validator using Guardrails-AI.

Implements Step 3 from the paper: LLM output validation.
"""
import logging
from typing import Optional
from debt_guardian.config import DebtGuardianConfig
from debt_guardian.schemas.td_schema import TechnicalDebtInstance

logger = logging.getLogger(__name__)


class OutputValidator:
    """
    Validates LLM outputs using Guardrails-AI and schema validation.
    
    Note: This is a simplified validator. Full Guardrails-AI integration
    with RAIL specs can be added for more sophisticated validation and reasks.
    """
    
    def __init__(self, config: DebtGuardianConfig):
        """
        Initialize the output validator.
        
        Args:
            config: DebtGuardian configuration
        """
        self.config = config
    
    def validate_debt_instance(
        self,
        debt: TechnicalDebtInstance
    ) -> TechnicalDebtInstance:
        """
        Validate a technical debt instance.
        
        Performs validation checks and corrections on the debt instance.
        
        Args:
            debt: The debt instance to validate
            
        Returns:
            Validated (and possibly corrected) debt instance
        """
        # Pydantic already validates the basic structure
        # Here we add additional business logic validation
        
        # Validate line numbers are reasonable
        if debt.location.end_line < debt.location.start_line:
            logger.warning(
                f"Invalid line range: {debt.location.start_line}-{debt.location.end_line}. "
                "Swapping values."
            )
            debt.location.start_line, debt.location.end_line = \
                debt.location.end_line, debt.location.start_line
        
        # Validate symptom is not empty or too short
        if len(debt.symptom.strip()) < 10:
            logger.warning(f"Symptom too short: '{debt.symptom}'. Marking as low confidence.")
            debt.confidence = min(debt.confidence, 0.5)
        
        # Validate debt type is in allowed list
        if debt.debt_type not in self.config.td_types:
            logger.warning(
                f"Debt type '{debt.debt_type}' not in configured types. "
                f"Allowed: {self.config.td_types}"
            )
        
        # Adjust confidence based on severity
        if debt.severity == "critical" and debt.confidence < 0.7:
            logger.warning(
                f"Critical severity with low confidence ({debt.confidence}). "
                "Consider manual review."
            )
        
        # Ensure suggested remediation exists for high severity
        if debt.severity in ["high", "critical"] and not debt.suggested_remediation:
            logger.warning(
                f"High/critical severity debt without remediation suggestion. "
                "Consider adding one."
            )
        
        return debt
    
    def validate_line_numbers(
        self,
        start_line: int,
        end_line: int,
        total_lines: int
    ) -> tuple[int, int]:
        """
        Validate and correct line numbers.
        
        Args:
            start_line: Starting line number
            end_line: Ending line number
            total_lines: Total lines in the file
            
        Returns:
            Tuple of (corrected_start, corrected_end)
        """
        # Ensure positive line numbers
        start_line = max(1, start_line)
        end_line = max(1, end_line)
        
        # Ensure start <= end
        if start_line > end_line:
            start_line, end_line = end_line, start_line
        
        # Ensure within file bounds
        if total_lines > 0:
            start_line = min(start_line, total_lines)
            end_line = min(end_line, total_lines)
        
        # Apply line threshold from config
        if end_line - start_line + 1 > self.config.line_threshold * 2:
            logger.warning(
                f"Line range {start_line}-{end_line} exceeds reasonable threshold. "
                f"Consider reviewing."
            )
        
        return start_line, end_line
    
    def validate_confidence(self, confidence: float) -> float:
        """
        Validate and normalize confidence score.
        
        Args:
            confidence: Confidence value
            
        Returns:
            Normalized confidence (0-1)
        """
        # Clamp to 0-1 range
        confidence = max(0.0, min(1.0, confidence))
        
        # Warn about extreme values
        if confidence < 0.3:
            logger.warning(f"Very low confidence ({confidence}). Consider discarding.")
        
        return confidence


# Future enhancement: Full Guardrails-AI integration with RAIL specs
"""
Example RAIL specification for future integration:

<rail version="0.1">
<output>
    <object name="debts">
        <list name="debts">
            <object>
                <string
                    name="debt_type"
                    description="Type of technical debt"
                    choices="design,documentation,defect,test,compatibility,build,requirement"
                    on-fail-choice="reask"
                />
                <string
                    name="symptom"
                    description="Description of the debt symptom"
                    length="10 200"
                    on-fail-length="reask"
                />
                <object name="location">
                    <string name="file_path" />
                    <integer name="start_line" format="positive" on-fail-format="fix" />
                    <integer name="end_line" format="positive" on-fail-format="fix" />
                </object>
                <string
                    name="severity"
                    choices="low,medium,high,critical"
                    on-fail-choice="reask"
                />
                <float
                    name="confidence"
                    format="range: 0 1"
                    on-fail-format="fix"
                />
                <string name="suggested_remediation" required="false" />
                <string name="code_snippet" required="false" />
            </object>
        </list>
    </object>
</output>

<prompt>
    Analyze the code change and identify technical debt instances.
    Return results in the specified JSON structure.
    
    {{code_diff}}
</prompt>
</rail>

Usage:
from guardrails import Guard
guard = Guard.from_rail('td_detection.rail')
validated_output = guard(llm_call, ...)
"""
