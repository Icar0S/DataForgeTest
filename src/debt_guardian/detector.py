"""
Main Technical Debt Detector

Orchestrates the complete DebtGuardian pipeline:
1. Source code loading and commit analysis
2. Debt identification using LLM
3. Output validation with Guardrails
"""
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Set
from pathlib import Path

from .config import DebtGuardianConfig
from .llm_client import OllamaClient
from .prompts import PromptTemplates
from .schemas import (
    TechnicalDebtInstance,
    TechnicalDebtReport,
    BatchDebtReport,
    CodeLocation
)
from .utils import GitAnalyzer
from .validators.output_validator import OutputValidator

logger = logging.getLogger(__name__)


class DebtDetector:
    """
    Main detector for identifying technical debt in code changes.
    
    Implements the DebtGuardian approach from the paper.
    """
    
    def __init__(self, config: DebtGuardianConfig):
        """
        Initialize the debt detector.
        
        Args:
            config: DebtGuardian configuration
        """
        self.config = config
        self.llm_client = OllamaClient(config)
        self.validator = OutputValidator(config) if config.enable_guardrails else None
        self.templates = PromptTemplates()
        
        # Initialize Git analyzer if repo path provided
        self.git_analyzer = None
        if config.repo_path:
            try:
                self.git_analyzer = GitAnalyzer(config.repo_path)
            except Exception as e:
                logger.warning(f"Could not initialize Git analyzer: {e}")
        
        # Create results directory
        Path(config.results_path).mkdir(parents=True, exist_ok=True)
    
    def detect_in_diff(
        self,
        code_diff: str,
        file_path: str,
        td_types: Optional[List[str]] = None,
        commit_sha: Optional[str] = None
    ) -> TechnicalDebtReport:
        """
        Detect technical debt in a code diff.
        
        Args:
            code_diff: The code diff to analyze
            file_path: Path to the file
            td_types: Optional list of TD types to detect (default: all)
            commit_sha: Optional commit SHA
            
        Returns:
            TechnicalDebtReport with detected debts
        """
        if td_types is None:
            td_types = self.config.td_types
        
        detected_debts = []
        
        # Choose prompting strategy
        if self.config.use_granular_prompting:
            # Granular: One TD type per request
            for td_type in td_types:
                debts = self._detect_single_type(code_diff, file_path, td_type)
                detected_debts.extend(debts)
                
        elif self.config.use_batch_prompting:
            # Batch: All TD types in one request
            debts = self._detect_batch(code_diff, file_path, td_types)
            detected_debts.extend(debts)
        
        else:
            # Default to granular
            for td_type in td_types:
                debts = self._detect_single_type(code_diff, file_path, td_type)
                detected_debts.extend(debts)
        
        # Apply majority voting if enabled
        if self.config.enable_majority_voting and len(detected_debts) > 0:
            detected_debts = self._apply_majority_voting(
                code_diff, file_path, td_types
            )
        
        # Count lines in diff
        total_lines = len([l for l in code_diff.split('\n') if l.startswith('+')])
        
        # Create report
        report = TechnicalDebtReport(
            commit_sha=commit_sha,
            file_path=file_path,
            detected_debts=detected_debts,
            analysis_timestamp=datetime.utcnow().isoformat(),
            model_used=self.config.llm_model,
            prompting_strategy=self._get_strategy_name(),
            total_lines_analyzed=total_lines
        )
        
        return report
    
    def _detect_single_type(
        self,
        code_diff: str,
        file_path: str,
        td_type: str
    ) -> List[TechnicalDebtInstance]:
        """
        Detect a single TD type using granular prompting.
        
        Args:
            code_diff: The code diff
            file_path: File path
            td_type: Type of TD to detect
            
        Returns:
            List of detected debt instances
        """
        try:
            # Choose zero-shot or few-shot
            if self.config.use_few_shot:
                examples = self.templates.get_examples_for_type(td_type)
                prompt = self.templates.few_shot_single_type(
                    code_diff, file_path, td_type, examples
                )
            else:
                prompt = self.templates.zero_shot_single_type(
                    code_diff, file_path, td_type
                )
            
            # Get LLM response
            response = self.llm_client.generate_structured(
                prompt,
                system_prompt=self.templates.SYSTEM_PROMPT
            )
            
            # Parse and validate
            debts = self._parse_response(response, file_path)
            
            logger.info(
                f"Detected {len(debts)} {td_type} debt instances in {file_path}"
            )
            
            return debts
            
        except Exception as e:
            logger.error(f"Error detecting {td_type} debt: {e}")
            return []
    
    def _detect_batch(
        self,
        code_diff: str,
        file_path: str,
        td_types: List[str]
    ) -> List[TechnicalDebtInstance]:
        """
        Detect multiple TD types using batch prompting.
        
        Args:
            code_diff: The code diff
            file_path: File path
            td_types: Types of TD to detect
            
        Returns:
            List of detected debt instances
        """
        try:
            prompt = self.templates.zero_shot_batch(
                code_diff, file_path, td_types
            )
            
            response = self.llm_client.generate_structured(
                prompt,
                system_prompt=self.templates.SYSTEM_PROMPT
            )
            
            debts = self._parse_response(response, file_path)
            
            logger.info(
                f"Detected {len(debts)} debt instances (batch) in {file_path}"
            )
            
            return debts
            
        except Exception as e:
            logger.error(f"Error in batch detection: {e}")
            return []
    
    def _parse_response(
        self,
        response: Dict,
        file_path: str
    ) -> List[TechnicalDebtInstance]:
        """
        Parse LLM response into TechnicalDebtInstance objects.
        
        Args:
            response: JSON response from LLM
            file_path: File path for validation
            
        Returns:
            List of TechnicalDebtInstance objects
        """
        debts = []
        
        try:
            debt_list = response.get('debts', [])
            
            for debt_data in debt_list:
                try:
                    # Validate and create instance
                    debt = TechnicalDebtInstance(**debt_data)
                    
                    # Additional validation with Guardrails if enabled
                    if self.validator:
                        debt = self.validator.validate_debt_instance(debt)
                    
                    debts.append(debt)
                    
                except Exception as e:
                    logger.warning(f"Invalid debt instance: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
        
        return debts
    
    def _apply_majority_voting(
        self,
        code_diff: str,
        file_path: str,
        td_types: List[str]
    ) -> List[TechnicalDebtInstance]:
        """
        Apply majority voting across multiple LLM runs.
        
        Args:
            code_diff: The code diff
            file_path: File path
            td_types: TD types to detect
            
        Returns:
            Filtered list of debt instances based on voting
        """
        all_detections = []
        
        # Run detection multiple times
        for i in range(self.config.voting_rounds):
            logger.info(f"Voting round {i+1}/{self.config.voting_rounds}")
            
            if self.config.use_granular_prompting:
                for td_type in td_types:
                    debts = self._detect_single_type(code_diff, file_path, td_type)
                    all_detections.append(debts)
            else:
                debts = self._detect_batch(code_diff, file_path, td_types)
                all_detections.append(debts)
        
        # Aggregate votes based on location similarity
        return self._aggregate_votes(all_detections)
    
    def _aggregate_votes(
        self,
        all_detections: List[List[TechnicalDebtInstance]]
    ) -> List[TechnicalDebtInstance]:
        """
        Aggregate detections from multiple runs using voting.
        
        Args:
            all_detections: List of detection results from each run
            
        Returns:
            Filtered list based on voting threshold
        """
        # Group similar detections by location and type
        detection_groups = {}
        
        for detection_list in all_detections:
            for debt in detection_list:
                key = self._get_debt_key(debt)
                if key not in detection_groups:
                    detection_groups[key] = []
                detection_groups[key].append(debt)
        
        # Filter based on voting threshold
        agreed_debts = []
        min_votes = int(self.config.voting_rounds * self.config.voting_threshold)
        
        for key, debts in detection_groups.items():
            if len(debts) >= min_votes:
                # Take the debt with highest confidence
                best_debt = max(debts, key=lambda d: d.confidence)
                agreed_debts.append(best_debt)
        
        logger.info(
            f"Majority voting: {len(agreed_debts)}/{sum(len(d) for d in all_detections)} "
            f"debts passed threshold"
        )
        
        return agreed_debts
    
    def _get_debt_key(self, debt: TechnicalDebtInstance) -> str:
        """
        Get a unique key for a debt instance for voting.
        
        Uses location and type with some tolerance for line numbers.
        """
        # Allow some tolerance in line numbers (within threshold)
        start_bucket = debt.location.start_line // self.config.line_threshold
        end_bucket = debt.location.end_line // self.config.line_threshold
        
        return f"{debt.debt_type}:{debt.location.file_path}:{start_bucket}:{end_bucket}"
    
    def _get_strategy_name(self) -> str:
        """Get the name of the current prompting strategy"""
        parts = []
        
        if self.config.use_zero_shot:
            parts.append("zero-shot")
        if self.config.use_few_shot:
            parts.append("few-shot")
        if self.config.use_batch_prompting:
            parts.append("batch")
        if self.config.use_granular_prompting:
            parts.append("granular")
        if self.config.enable_majority_voting:
            parts.append("voting")
        
        return "+".join(parts) if parts else "default"
    
    def analyze_commit(self, commit_sha: str) -> TechnicalDebtReport:
        """
        Analyze a specific commit for technical debt.
        
        Args:
            commit_sha: SHA of the commit to analyze
            
        Returns:
            TechnicalDebtReport
        """
        if not self.git_analyzer:
            raise ValueError("Git analyzer not initialized. Provide repo_path in config.")
        
        # Get commit
        commit = self.git_analyzer.repo.commit(commit_sha)
        
        # Get diffs
        file_diffs = self.git_analyzer.get_commit_diff(commit)
        
        # Analyze each file
        all_debts = []
        for file_path, diff in file_diffs.items():
            if self.git_analyzer.is_code_file(file_path):
                report = self.detect_in_diff(diff, file_path, commit_sha=commit_sha)
                all_debts.extend(report.detected_debts)
        
        # Create combined report
        return TechnicalDebtReport(
            commit_sha=commit_sha,
            file_path="multiple_files",
            detected_debts=all_debts,
            analysis_timestamp=datetime.utcnow().isoformat(),
            model_used=self.config.llm_model,
            prompting_strategy=self._get_strategy_name(),
            total_lines_analyzed=sum(
                len([l for l in d.split('\n') if l.startswith('+')])
                for d in file_diffs.values()
            )
        )
    
    def analyze_repository(
        self,
        max_commits: Optional[int] = None
    ) -> BatchDebtReport:
        """
        Analyze multiple commits in a repository.
        
        Args:
            max_commits: Maximum number of commits to analyze
            
        Returns:
            BatchDebtReport
        """
        if not self.git_analyzer:
            raise ValueError("Git analyzer not initialized. Provide repo_path in config.")
        
        max_commits = max_commits or self.config.max_commits_to_analyze
        commits = self.git_analyzer.get_recent_commits(max_count=max_commits)
        
        reports = []
        for commit in commits:
            try:
                report = self.analyze_commit(commit.hexsha)
                reports.append(report)
            except Exception as e:
                logger.error(f"Error analyzing commit {commit.hexsha[:8]}: {e}")
                continue
        
        # Calculate summary
        summary = {
            "total_commits": len(commits),
            "analyzed_commits": len(reports),
            "total_debts": sum(r.debt_count for r in reports),
            "debt_by_type": {},
            "high_severity_total": sum(r.high_severity_count for r in reports)
        }
        
        # Aggregate debt counts by type
        for report in reports:
            for debt_type, count in report.debt_by_type.items():
                summary["debt_by_type"][debt_type] = \
                    summary["debt_by_type"].get(debt_type, 0) + count
        
        return BatchDebtReport(reports=reports, summary=summary)
    
    def save_report(self, report: TechnicalDebtReport, filename: str):
        """
        Save a report to disk.
        
        Args:
            report: The report to save
            filename: Name of the file (without extension)
        """
        output_path = Path(self.config.results_path) / f"{filename}.json"
        
        with open(output_path, 'w') as f:
            json.dump(report.model_dump(), f, indent=2)
        
        logger.info(f"Report saved to {output_path}")
