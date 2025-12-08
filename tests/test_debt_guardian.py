"""
Tests for DebtGuardian framework

Note: These tests require Ollama to be running with qwen2.5-coder:7b model.
"""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from debt_guardian.config import DebtGuardianConfig
from debt_guardian.schemas.td_schema import (
    TechnicalDebtInstance,
    TechnicalDebtReport,
    CodeLocation,
    TechnicalDebtType
)


class TestSchemas:
    """Test Pydantic schemas"""
    
    def test_technical_debt_types(self):
        """Test TD type definitions"""
        types = TechnicalDebtType.all_types()
        assert len(types) == 7
        assert "design" in types
        assert "documentation" in types
        assert "test" in types
    
    def test_code_location_valid(self):
        """Test valid code location"""
        location = CodeLocation(
            file_path="src/test.py",
            start_line=10,
            end_line=15
        )
        assert location.file_path == "src/test.py"
        assert location.start_line == 10
        assert location.end_line == 15
    
    def test_code_location_invalid_range(self):
        """Test invalid line range"""
        with pytest.raises(ValueError):
            CodeLocation(
                file_path="src/test.py",
                start_line=15,
                end_line=10
            )
    
    def test_technical_debt_instance(self):
        """Test TD instance creation"""
        debt = TechnicalDebtInstance(
            debt_type="design",
            symptom="God class with too many responsibilities",
            location=CodeLocation(
                file_path="src/test.py",
                start_line=10,
                end_line=50
            ),
            severity="high",
            confidence=0.85
        )
        assert debt.debt_type == "design"
        assert debt.severity == "high"
        assert debt.confidence == 0.85
    
    def test_technical_debt_report(self):
        """Test TD report creation"""
        debt = TechnicalDebtInstance(
            debt_type="test",
            symptom="Missing unit tests",
            location=CodeLocation(
                file_path="src/test.py",
                start_line=1,
                end_line=10
            ),
            severity="medium",
            confidence=0.9
        )
        
        report = TechnicalDebtReport(
            file_path="src/test.py",
            detected_debts=[debt],
            analysis_timestamp="2024-12-08T12:00:00Z",
            model_used="qwen2.5-coder:7b",
            prompting_strategy="granular",
            total_lines_analyzed=10
        )
        
        assert report.debt_count == 1
        assert report.debt_by_type == {"test": 1}
        assert report.high_severity_count == 0


class TestConfig:
    """Test configuration"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = DebtGuardianConfig()
        assert config.llm_model == "qwen2.5-coder:7b"
        assert config.llm_provider == "ollama"
        assert config.use_granular_prompting is True
        assert len(config.td_types) == 7
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = DebtGuardianConfig(
            llm_model="custom-model",
            td_types=["design", "test"],
            use_batch_prompting=True,
            use_granular_prompting=False
        )
        assert config.llm_model == "custom-model"
        assert len(config.td_types) == 2
        assert config.use_batch_prompting is True
    
    def test_invalid_config_both_strategies(self):
        """Test that both strategies cannot be enabled"""
        with pytest.raises(ValueError):
            DebtGuardianConfig(
                use_batch_prompting=True,
                use_granular_prompting=True
            )
    
    def test_voting_config_validation(self):
        """Test majority voting validation"""
        with pytest.raises(ValueError):
            DebtGuardianConfig(
                enable_majority_voting=True,
                voting_rounds=1
            )


class TestPrompts:
    """Test prompt templates"""
    
    def test_prompt_templates_exist(self):
        """Test that prompt templates are available"""
        from debt_guardian.prompts import PromptTemplates
        templates = PromptTemplates()
        assert templates.SYSTEM_PROMPT is not None
        assert len(templates.SYSTEM_PROMPT) > 0
    
    def test_zero_shot_single_type(self):
        """Test zero-shot single type prompt"""
        from debt_guardian.prompts import PromptTemplates
        
        prompt = PromptTemplates.zero_shot_single_type(
            code_diff="+ print('hello')",
            file_path="test.py",
            td_type="design"
        )
        
        assert "design" in prompt.lower()
        assert "test.py" in prompt
        assert "print('hello')" in prompt
    
    def test_few_shot_examples(self):
        """Test few-shot examples exist"""
        from debt_guardian.prompts import PromptTemplates
        
        design_examples = PromptTemplates.get_examples_for_type("design")
        assert len(design_examples) > 0
        
        test_examples = PromptTemplates.get_examples_for_type("test")
        assert len(test_examples) > 0


@pytest.mark.integration
class TestIntegration:
    """Integration tests (require Ollama)"""
    
    def test_ollama_connection(self):
        """Test connection to Ollama"""
        from debt_guardian.llm_client import OllamaClient
        from debt_guardian.config import DebtGuardianConfig
        
        config = DebtGuardianConfig()
        try:
            client = OllamaClient(config)
            # If this doesn't raise, connection is OK
            assert client is not None
        except ConnectionError:
            pytest.skip("Ollama not running")
    
    def test_detector_initialization(self):
        """Test detector initialization"""
        from debt_guardian.detector import DebtDetector
        from debt_guardian.config import DebtGuardianConfig
        
        config = DebtGuardianConfig()
        try:
            detector = DebtDetector(config)
            assert detector is not None
            assert detector.llm_client is not None
        except ConnectionError:
            pytest.skip("Ollama not running")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
