# DebtGuardian - LLM-Based Technical Debt Detection

## Overview

DebtGuardian is an experimental framework for detecting technical debt in source code changes using Large Language Models. This implementation is based on the paper "Detecting Technical Debt in Source Code Changes using Large Language Models."

**Key Feature**: Uses **Qwen2.5-Coder:7b** via Ollama for local, privacy-preserving analysis (77% recall in the study).

## Directory Structure

```
debt_guardian/
├── __init__.py           # Main package exports
├── config.py             # Configuration management
├── detector.py           # Main TD detection orchestrator
├── llm_client.py         # Ollama LLM integration
│
├── schemas/              # Pydantic data models
│   ├── __init__.py
│   └── td_schema.py      # Technical debt schemas
│
├── prompts/              # LLM prompt templates
│   ├── __init__.py
│   └── templates.py      # Zero-shot, few-shot, batch prompts
│
├── validators/           # Output validation
│   ├── __init__.py
│   └── output_validator.py  # Guardrails integration
│
├── utils/                # Utility modules
│   ├── __init__.py
│   └── git_utils.py      # Git repository analysis
│
└── api/                  # REST API
    ├── __init__.py
    └── blueprint.py      # Flask endpoints
```

## Quick Start

```python
from debt_guardian import DebtGuardianConfig, DebtDetector

# Initialize
config = DebtGuardianConfig()
detector = DebtDetector(config)

# Analyze code
report = detector.detect_in_diff(
    code_diff="+ def foo(): pass",
    file_path="test.py"
)

print(f"Found {report.debt_count} debts")
```

## Features

### Stage 1: Code Analysis
- Git repository integration
- Commit history analysis
- Diff extraction
- File change detection

### Stage 2: LLM Detection
- **Prompting Strategies**:
  - Zero-shot (no examples)
  - Few-shot (with examples)
  - Batch (multiple types at once)
  - Granular (one type at a time)
- **Majority voting** for improved accuracy

### Stage 3: Validation
- Pydantic schema validation
- Guardrails-AI integration
- Automatic error correction
- Structured output formatting

## Technical Debt Types

Detects 7 types based on MLCQ dataset:
1. **Design** - Architecture issues
2. **Documentation** - Missing docs
3. **Defect** - Bugs and errors
4. **Test** - Test coverage gaps
5. **Compatibility** - Version issues
6. **Build** - Build problems
7. **Requirement** - Incomplete features

## Configuration

```python
config = DebtGuardianConfig(
    # LLM settings
    llm_model="qwen2.5-coder:7b",
    ollama_base_url="http://localhost:11434",
    temperature=0.1,
    
    # Prompting strategy
    use_granular_prompting=True,  # Recommended
    use_few_shot=False,
    
    # Majority voting
    enable_majority_voting=False,
    voting_rounds=3,
    
    # TD types to detect
    td_types=["design", "test", "defect"],
    
    # Repository
    repo_path="/path/to/repo"
)
```

## REST API Endpoints

- `GET /api/debt-guardian/health` - Health check
- `POST /api/debt-guardian/analyze/diff` - Analyze code diff
- `POST /api/debt-guardian/analyze/commit/<sha>` - Analyze commit
- `POST /api/debt-guardian/analyze/repository` - Analyze repo
- `GET /api/debt-guardian/config` - Get configuration
- `GET /api/debt-guardian/types` - List TD types

## Output Schema

```python
{
  "debt_type": "design|documentation|defect|test|...",
  "symptom": "Description of the issue",
  "location": {
    "file_path": "src/file.py",
    "start_line": 10,
    "end_line": 15
  },
  "severity": "low|medium|high|critical",
  "confidence": 0.85,
  "suggested_remediation": "How to fix",
  "code_snippet": "The problematic code"
}
```

## Performance

- **Model**: Qwen2.5-Coder:7b
- **Recall**: 77% (per paper)
- **Analysis time**: 5-15 seconds per file
- **Memory**: ~4GB RAM
- **Storage**: ~5GB for model

## Requirements

- Python 3.8+
- Ollama with qwen2.5-coder:7b
- 4GB+ free RAM
- Git (for repository analysis)

## Dependencies

```
ollama
pydantic>=2.0.0
guardrails-ai
GitPython
Flask
Flask-CORS
```

## Installation

1. Install Ollama: https://ollama.ai
2. Pull model: `ollama pull qwen2.5-coder:7b`
3. Install deps: `pip install -r requirements.txt`
4. Start Ollama: `ollama serve`

## Testing

```bash
# Run unit tests
pytest tests/test_debt_guardian.py -v

# Run example
python examples/analyze_sample.py

# Integration tests (requires Ollama)
pytest tests/test_debt_guardian.py::TestIntegration -v
```

## Documentation

- [Full Guide](../../docs/DEBT_GUARDIAN.md)
- [Quick Start](../../docs/DEBT_GUARDIAN_QUICKSTART.md)
- [API Reference](../../docs/DEBT_GUARDIAN.md#rest-api)

## Research Paper

This implementation is based on:
> "Detecting Technical Debt in Source Code Changes using Large Language Models"

Key findings:
- Granular prompting > batch prompting
- Code-specialized models > general models
- Majority voting: +8.17% recall
- 10-line threshold: optimal balance

## Known Limitations

1. **Model Size**: Requires 4GB RAM
2. **Performance**: 5-15s per analysis
3. **Language Support**: Best for Python, Java, JS
4. **False Positives**: Tune confidence threshold
5. **Context Window**: Limited to ~4K tokens

## Future Enhancements

- [ ] Full Guardrails-AI RAIL integration
- [ ] Support for more LLM providers
- [ ] Caching for analyzed code
- [ ] Parallel batch processing
- [ ] Web UI for visualization
- [ ] Custom TD type definitions
- [ ] Historical trend analysis

## Contributing

This is an experimental feature. Contributions welcome:
1. Test with your codebase
2. Report issues
3. Suggest improvements
4. Add support for more TD types

## License

Part of DataForgeTest project - MIT License

## Support

For issues:
1. Check Ollama is running
2. Verify model is pulled
3. Review logs in `storage/debt_guardian/`
4. Open GitHub issue

## Acknowledgments

- Research paper authors
- Ollama team
- Qwen2.5-Coder developers
- Guardrails-AI project
- DataForgeTest community

---

**Experimental Branch**: This is a research/experimental setup for testing the framework before broader deployment.
