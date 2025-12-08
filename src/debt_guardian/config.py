"""
Configuration for DebtGuardian Framework
"""
from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class DebtGuardianConfig:
    """
    Configuration for DebtGuardian framework.
    
    This configuration uses Qwen2.5-Coder:7b via Ollama for local LLM execution.
    According to the paper, this model achieved 77% recall in TD detection.
    """
    
    # LLM Configuration
    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5-coder:7b"  # 77% recall model from the study
    ollama_base_url: str = "http://localhost:11434"
    
    # Temperature and generation settings
    temperature: float = 0.1  # Low temperature for more deterministic outputs
    max_tokens: int = 4096
    
    # Prompting strategies
    use_zero_shot: bool = True
    use_few_shot: bool = False
    use_batch_prompting: bool = False  # Multiple TD types in one prompt
    use_granular_prompting: bool = True  # One TD type per prompt
    
    # Majority voting
    enable_majority_voting: bool = False
    voting_rounds: int = 3  # Number of LLM calls for voting
    voting_threshold: float = 0.5  # Minimum agreement ratio
    
    # Guardrails-AI validation
    enable_guardrails: bool = True
    max_reask_attempts: int = 3
    
    # Technical Debt types to detect
    td_types: List[str] = field(default_factory=lambda: [
        "design",
        "documentation", 
        "defect",
        "test",
        "compatibility",
        "build",
        "requirement"
    ])
    
    # Git repository settings
    repo_path: Optional[str] = None
    analyze_uncommitted: bool = True
    max_commits_to_analyze: int = 10
    
    # Line-level detection settings
    line_threshold: int = 10  # Best balance per paper
    
    # Processing settings
    batch_size: int = 5  # Files to process in batch
    timeout_seconds: int = 300
    
    # Storage paths
    results_path: str = "./storage/debt_guardian"
    cache_path: str = "./storage/debt_guardian/cache"
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.use_batch_prompting and self.use_granular_prompting:
            raise ValueError(
                "Cannot use both batch and granular prompting simultaneously. "
                "Choose one strategy."
            )
        
        if self.enable_majority_voting and self.voting_rounds < 2:
            raise ValueError(
                "Majority voting requires at least 2 rounds"
            )
        
        if not self.td_types:
            raise ValueError("At least one TD type must be specified")
