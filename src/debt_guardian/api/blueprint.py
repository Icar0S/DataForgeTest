"""
Flask blueprint for DebtGuardian API endpoints.

Provides REST API for technical debt detection.
"""
import os
import json
import logging
from flask import Blueprint, request, jsonify
from pathlib import Path
from datetime import datetime

from ..config import DebtGuardianConfig
from ..detector import DebtDetector
from ..schemas import TechnicalDebtReport

logger = logging.getLogger(__name__)

# Create blueprint
debt_guardian_bp = Blueprint('debt_guardian', __name__, url_prefix='/api/debt-guardian')


def get_detector():
    """
    Get or create a DebtDetector instance.
    
    Returns:
        DebtDetector instance
    """
    # For now, use default config
    # In production, this could be cached or configured via environment
    config = DebtGuardianConfig(
        repo_path=os.getenv('DEBT_GUARDIAN_REPO_PATH'),
        ollama_base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
        llm_model=os.getenv('DEBT_GUARDIAN_MODEL', 'qwen2.5-coder:7b')
    )
    
    return DebtDetector(config)


@debt_guardian_bp.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    
    Returns:
        JSON response with health status
    """
    try:
        detector = get_detector()
        ollama_healthy = detector.llm_client.health_check()
        
        return jsonify({
            'status': 'healthy' if ollama_healthy else 'degraded',
            'service': 'DebtGuardian',
            'ollama': 'connected' if ollama_healthy else 'disconnected',
            'model': detector.config.llm_model,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@debt_guardian_bp.route('/analyze/diff', methods=['POST'])
def analyze_diff():
    """
    Analyze a code diff for technical debt.
    
    Expected JSON body:
    {
        "code_diff": "...",
        "file_path": "src/example.py",
        "td_types": ["design", "documentation"],  // optional
        "commit_sha": "abc123"  // optional
    }
    
    Returns:
        TechnicalDebtReport as JSON
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        code_diff = data.get('code_diff')
        file_path = data.get('file_path')
        
        if not code_diff or not file_path:
            return jsonify({
                'error': 'Missing required fields: code_diff, file_path'
            }), 400
        
        td_types = data.get('td_types')
        commit_sha = data.get('commit_sha')
        
        # Get detector and analyze
        detector = get_detector()
        report = detector.detect_in_diff(
            code_diff=code_diff,
            file_path=file_path,
            td_types=td_types,
            commit_sha=commit_sha
        )
        
        return jsonify(report.model_dump())
        
    except Exception as e:
        logger.error(f"Error in analyze_diff: {e}")
        return jsonify({'error': str(e)}), 500


@debt_guardian_bp.route('/analyze/commit/<commit_sha>', methods=['POST'])
def analyze_commit(commit_sha):
    """
    Analyze a specific commit for technical debt.
    
    Requires DEBT_GUARDIAN_REPO_PATH to be set.
    
    Returns:
        TechnicalDebtReport as JSON
    """
    try:
        detector = get_detector()
        
        if not detector.config.repo_path:
            return jsonify({
                'error': 'Repository path not configured. Set DEBT_GUARDIAN_REPO_PATH.'
            }), 400
        
        report = detector.analyze_commit(commit_sha)
        
        return jsonify(report.model_dump())
        
    except Exception as e:
        logger.error(f"Error in analyze_commit: {e}")
        return jsonify({'error': str(e)}), 500


@debt_guardian_bp.route('/analyze/repository', methods=['POST'])
def analyze_repository():
    """
    Analyze multiple commits in a repository.
    
    Expected JSON body:
    {
        "max_commits": 10  // optional
    }
    
    Returns:
        BatchDebtReport as JSON
    """
    try:
        detector = get_detector()
        
        if not detector.config.repo_path:
            return jsonify({
                'error': 'Repository path not configured. Set DEBT_GUARDIAN_REPO_PATH.'
            }), 400
        
        data = request.get_json() or {}
        max_commits = data.get('max_commits')
        
        report = detector.analyze_repository(max_commits=max_commits)
        
        return jsonify(report.model_dump())
        
    except Exception as e:
        logger.error(f"Error in analyze_repository: {e}")
        return jsonify({'error': str(e)}), 500


@debt_guardian_bp.route('/config', methods=['GET'])
def get_config():
    """
    Get current configuration.
    
    Returns:
        Configuration as JSON
    """
    try:
        detector = get_detector()
        
        return jsonify({
            'llm_provider': detector.config.llm_provider,
            'llm_model': detector.config.llm_model,
            'ollama_base_url': detector.config.ollama_base_url,
            'td_types': detector.config.td_types,
            'prompting_strategy': {
                'zero_shot': detector.config.use_zero_shot,
                'few_shot': detector.config.use_few_shot,
                'batch': detector.config.use_batch_prompting,
                'granular': detector.config.use_granular_prompting,
                'majority_voting': detector.config.enable_majority_voting
            },
            'repo_path': detector.config.repo_path,
            'results_path': detector.config.results_path
        })
        
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({'error': str(e)}), 500


@debt_guardian_bp.route('/types', methods=['GET'])
def get_td_types():
    """
    Get available technical debt types.
    
    Returns:
        List of TD types with descriptions
    """
    return jsonify({
        'types': [
            {
                'name': 'design',
                'description': 'Poor architectural decisions, code smells, violations of design principles'
            },
            {
                'name': 'documentation',
                'description': 'Missing or inadequate documentation, comments, or explanations'
            },
            {
                'name': 'defect',
                'description': 'Bugs, errors, or potential issues in the code'
            },
            {
                'name': 'test',
                'description': 'Missing tests, inadequate test coverage, or poor test quality'
            },
            {
                'name': 'compatibility',
                'description': 'Issues with backward/forward compatibility or deprecated APIs'
            },
            {
                'name': 'build',
                'description': 'Problems with build configuration, dependencies, or deployment'
            },
            {
                'name': 'requirement',
                'description': 'Missing or incomplete implementation of requirements'
            }
        ]
    })


@debt_guardian_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@debt_guardian_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500
