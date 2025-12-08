# DebtGuardian Framework

## Overview

DebtGuardian is an LLM-based framework for detecting Technical Debt (TD) directly from source code changes. This implementation is based on the paper "Detecting Technical Debt in Source Code Changes using Large Language Models" and uses **Qwen2.5-Coder:7b** via Ollama for local execution.

**Key Achievement**: Qwen2.5-Coder:7b achieved **77% recall** in the original study, outperforming much larger models.

## Architecture

DebtGuardian implements a three-stage pipeline:

### Stage 1: Source Code Loading and Commit Analysis
- Connects to Git repositories
- Analyzes commit histories
- Detects modified files
- Extracts code diffs

### Stage 2: Debt Identification
- Constructs LLM prompts with code changes
- Uses structured TD schema (Pydantic)
- Supports multiple prompting strategies:
  - **Zero-shot**: No examples, relies on pretrained knowledge
  - **Few-shot**: Includes annotated examples
  - **Batch**: Multiple TD types in one prompt
  - **Granular**: One TD type per prompt (higher precision)
  - **Majority voting**: Aggregates multiple runs

### Stage 3: Output Validation
- Validates LLM responses using Guardrails-AI
- Enforces TD schema compliance
- Provides automatic reasks for violations
- Standardizes output format

## Technical Debt Types

DebtGuardian detects 7 types of technical debt based on the MLCQ dataset:

1. **DESIGN**: Poor architectural decisions, code smells, SOLID violations
2. **DOCUMENTATION**: Missing or inadequate documentation
3. **DEFECT**: Bugs, errors, potential issues
4. **TEST**: Missing tests, inadequate coverage
5. **COMPATIBILITY**: Backward/forward compatibility issues
6. **BUILD**: Build configuration, dependency problems
7. **REQUIREMENT**: Incomplete requirement implementation

## Installation

### Prerequisites

1. **Ollama** - Install from https://ollama.ai
2. **Python 3.8+** with pip
3. **Git** for repository analysis

### Install Ollama and Pull Model

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the Qwen2.5-Coder:7b model
ollama pull qwen2.5-coder:7b

# Verify Ollama is running
ollama list
```

### Install Python Dependencies

```bash
# From repository root
pip install -r requirements.txt

# Or install individually
pip install ollama pydantic>=2.0.0 guardrails-ai GitPython
```

## Configuration

### Environment Variables

Create or update `.env` file:

```bash
# DebtGuardian Configuration
OLLAMA_BASE_URL=http://localhost:11434
DEBT_GUARDIAN_MODEL=qwen2.5-coder:7b
DEBT_GUARDIAN_REPO_PATH=/path/to/your/repo

# Optional: Storage paths
DEBT_GUARDIAN_RESULTS_PATH=./storage/debt_guardian
```

### Python Configuration

```python
from debt_guardian import DebtGuardianConfig, DebtDetector

config = DebtGuardianConfig(
    llm_model="qwen2.5-coder:7b",
    ollama_base_url="http://localhost:11434",
    
    # Prompting strategies (choose one)
    use_granular_prompting=True,  # Recommended for precision
    use_batch_prompting=False,
    
    # Few-shot learning
    use_few_shot=False,  # Set True to use examples
    
    # Majority voting (boosts recall by 8.17%)
    enable_majority_voting=False,
    voting_rounds=3,
    
    # TD types to detect
    td_types=["design", "documentation", "defect", "test"],
    
    # Repository settings
    repo_path="/path/to/repo"
)

detector = DebtDetector(config)
```

## Usage

### 1. Analyze a Code Diff

```python
from debt_guardian import DebtGuardianConfig, DebtDetector

# Initialize
config = DebtGuardianConfig()
detector = DebtDetector(config)

# Analyze a diff
code_diff = """
+def calculate_total(items):
+    total = 0
+    for item in items:
+        total += item.price
+    return total
"""

report = detector.detect_in_diff(
    code_diff=code_diff,
    file_path="src/calculator.py"
)

# Print results
print(f"Found {report.debt_count} technical debt instances")
for debt in report.detected_debts:
    print(f"- {debt.debt_type}: {debt.symptom}")
    print(f"  Lines {debt.location.start_line}-{debt.location.end_line}")
    print(f"  Severity: {debt.severity}")
```

### 2. Analyze a Git Commit

```python
config = DebtGuardianConfig(
    repo_path="/path/to/repo"
)
detector = DebtDetector(config)

# Analyze specific commit
report = detector.analyze_commit("abc123def")

print(f"Commit {report.commit_sha}")
print(f"Total debts: {report.debt_count}")
print(f"By type: {report.debt_by_type}")
```

### 3. Analyze Repository History

```python
# Analyze last 10 commits
batch_report = detector.analyze_repository(max_commits=10)

print(f"Analyzed {batch_report.total_files} files")
print(f"Found {batch_report.total_debts} debts total")
print(f"Summary: {batch_report.summary}")
```

### 4. Save Report

```python
detector.save_report(report, filename="analysis_2024_12_08")
# Saves to: ./storage/debt_guardian/analysis_2024_12_08.json
```

## REST API

DebtGuardian provides a Flask REST API for integration.

### Start the API Server

```bash
cd src
python api.py
```

### API Endpoints

#### Health Check
```bash
GET /api/debt-guardian/health
```

Response:
```json
{
  "status": "healthy",
  "service": "DebtGuardian",
  "ollama": "connected",
  "model": "qwen2.5-coder:7b",
  "timestamp": "2024-12-08T12:00:00Z"
}
```

#### Analyze Code Diff
```bash
POST /api/debt-guardian/analyze/diff
Content-Type: application/json

{
  "code_diff": "...",
  "file_path": "src/example.py",
  "td_types": ["design", "test"],
  "commit_sha": "optional"
}
```

#### Analyze Commit
```bash
POST /api/debt-guardian/analyze/commit/<commit_sha>
```

#### Analyze Repository
```bash
POST /api/debt-guardian/analyze/repository
Content-Type: application/json

{
  "max_commits": 10
}
```

#### Get Configuration
```bash
GET /api/debt-guardian/config
```

#### Get TD Types
```bash
GET /api/debt-guardian/types
```

## Prompting Strategies

### Granular Prompting (Recommended)
- Analyzes one TD type at a time
- Higher precision
- Better for focused analysis

```python
config = DebtGuardianConfig(
    use_granular_prompting=True,
    td_types=["design", "test"]
)
```

### Batch Prompting
- Analyzes all TD types in one request
- Faster execution
- May reduce precision

```python
config = DebtGuardianConfig(
    use_batch_prompting=True
)
```

### Few-Shot Learning
- Provides examples to the LLM
- Improves pattern recognition
- Better for domain-specific TD

```python
config = DebtGuardianConfig(
    use_few_shot=True,
    use_granular_prompting=True
)
```

### Majority Voting
- Runs detection multiple times
- Aggregates results
- Boosts recall by ~8% (per paper)

```python
config = DebtGuardianConfig(
    enable_majority_voting=True,
    voting_rounds=3,
    voting_threshold=0.5  # 50% agreement
)
```

## Output Schema

### TechnicalDebtInstance

```python
{
  "debt_type": "design|documentation|defect|test|compatibility|build|requirement",
  "symptom": "Description of the problem",
  "location": {
    "file_path": "src/example.py",
    "start_line": 10,
    "end_line": 15
  },
  "severity": "low|medium|high|critical",
  "confidence": 0.85,
  "suggested_remediation": "How to fix it",
  "code_snippet": "The problematic code"
}
```

### TechnicalDebtReport

```python
{
  "commit_sha": "abc123",
  "file_path": "src/example.py",
  "detected_debts": [...],
  "analysis_timestamp": "2024-12-08T12:00:00Z",
  "model_used": "qwen2.5-coder:7b",
  "prompting_strategy": "granular",
  "total_lines_analyzed": 50
}
```

## Performance Considerations

### Model Performance
- **Qwen2.5-Coder:7b**: 77% recall (per paper)
- Runs locally on consumer hardware
- ~4GB VRAM required
- Response time: 2-10 seconds per analysis

### Optimization Tips

1. **Use Granular Prompting** for better precision
2. **Enable Majority Voting** to boost recall (+8%)
3. **Filter by Confidence** threshold (e.g., >0.7)
4. **Batch Process** files in parallel
5. **Cache Results** for analyzed commits

## Best Practices

### 1. Start with High-Priority TD Types
```python
config = DebtGuardianConfig(
    td_types=["defect", "test"],  # Critical first
    use_granular_prompting=True
)
```

### 2. Use 10-Line Threshold
Per the paper, a 10-line threshold achieves the best balance:
```python
config = DebtGuardianConfig(
    line_threshold=10
)
```

### 3. Filter Low-Confidence Results
```python
high_confidence = [
    debt for debt in report.detected_debts
    if debt.confidence > 0.7
]
```

### 4. Focus on High Severity
```python
critical_debts = [
    debt for debt in report.detected_debts
    if debt.severity in ["high", "critical"]
]
```

## Troubleshooting

### Ollama Not Connected
```bash
# Check if Ollama is running
ollama list

# Restart Ollama
ollama serve

# Check logs
curl http://localhost:11434/api/tags
```

### Model Not Found
```bash
# Pull the model
ollama pull qwen2.5-coder:7b

# Verify
ollama list | grep qwen
```

### Out of Memory
```python
# Reduce max_tokens
config = DebtGuardianConfig(
    max_tokens=2048  # Default is 4096
)
```

### Slow Performance
```python
# Disable majority voting
config = DebtGuardianConfig(
    enable_majority_voting=False
)

# Use batch prompting
config = DebtGuardianConfig(
    use_batch_prompting=True
)
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Technical Debt Detection

on: [pull_request]

jobs:
  debt-detection:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install Ollama
        run: curl -fsSL https://ollama.ai/install.sh | sh
      
      - name: Pull Model
        run: ollama pull qwen2.5-coder:7b
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install Dependencies
        run: pip install -r requirements.txt
      
      - name: Run DebtGuardian
        run: python scripts/detect_debt.py
```

## Testing

### Run Unit Tests
```bash
pytest tests/test_debt_guardian.py -v
```

### Test with Sample Code
```bash
python examples/analyze_sample.py
```

## Contributing

See the main repository [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## References

- Paper: "Detecting Technical Debt in Source Code Changes using Large Language Models"
- Ollama: https://ollama.ai
- Qwen2.5-Coder: https://github.com/QwenLM/Qwen2.5-Coder
- Guardrails-AI: https://github.com/guardrails-ai/guardrails
- MLCQ Dataset: Referenced in the paper

## License

This implementation is part of the DataForgeTest project and follows its MIT license.

## Support

For issues specific to DebtGuardian:
1. Check Ollama connectivity
2. Verify model is pulled
3. Review logs in `./storage/debt_guardian/`
4. Open an issue on GitHub

---

**Built with ❤️ for the Software Quality Community**
