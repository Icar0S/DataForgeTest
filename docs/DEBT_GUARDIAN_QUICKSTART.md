# DebtGuardian Quick Start Guide

## What is DebtGuardian?

DebtGuardian is an AI-powered framework that automatically detects **Technical Debt** in your code changes using a Large Language Model running **locally** on your machine. No cloud services required!

### Key Features
- 🚀 **Local LLM**: Uses Qwen2.5-Coder:7b via Ollama (no API keys needed)
- 🎯 **High Accuracy**: 77% recall in research study
- 📊 **7 TD Types**: Design, documentation, defects, tests, and more
- 🔧 **CI/CD Ready**: Integrate into your development workflow

## 5-Minute Setup

### Step 1: Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai/download

### Step 2: Pull the Model

```bash
ollama pull qwen2.5-coder:7b
```

This downloads the ~4.7GB model. Wait for it to complete.

### Step 3: Start Ollama

```bash
ollama serve
```

Keep this terminal open.

### Step 4: Install Python Dependencies

```bash
cd /path/to/DataForgeTest
pip install -r requirements.txt
```

### Step 5: Verify Installation

```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Run example
python examples/analyze_sample.py
```

## Your First Analysis

### Option 1: Python API

```python
from debt_guardian import DebtGuardianConfig, DebtDetector

# Configure
config = DebtGuardianConfig()
detector = DebtDetector(config)

# Analyze code
code_diff = """
+def calculate(x, y):
+    return x / y  # No zero check!
"""

report = detector.detect_in_diff(
    code_diff=code_diff,
    file_path="calculator.py"
)

# Show results
for debt in report.detected_debts:
    print(f"{debt.debt_type}: {debt.symptom}")
```

### Option 2: REST API

**Start the server:**
```bash
cd src
python api.py
```

**Analyze code:**
```bash
curl -X POST http://localhost:5000/api/debt-guardian/analyze/diff \
  -H "Content-Type: application/json" \
  -d '{
    "code_diff": "+def calc(x,y):\n+    return x/y",
    "file_path": "calc.py"
  }'
```

### Option 3: Analyze Git Repository

```python
from debt_guardian import DebtGuardianConfig, DebtDetector

config = DebtGuardianConfig(
    repo_path="/path/to/your/repo"
)
detector = DebtDetector(config)

# Analyze last 5 commits
report = detector.analyze_repository(max_commits=5)
print(f"Found {report.total_debts} technical debt instances")
```

## Understanding Results

Each detected technical debt includes:

```json
{
  "debt_type": "defect",
  "symptom": "Division by zero not handled",
  "location": {
    "file_path": "calculator.py",
    "start_line": 2,
    "end_line": 2
  },
  "severity": "high",
  "confidence": 0.92,
  "suggested_remediation": "Add zero check before division"
}
```

### Technical Debt Types

1. **DESIGN** - Code smells, SOLID violations
2. **DOCUMENTATION** - Missing docs, unclear comments
3. **DEFECT** - Bugs, security issues
4. **TEST** - Missing or inadequate tests
5. **COMPATIBILITY** - Deprecated APIs
6. **BUILD** - Dependency problems
7. **REQUIREMENT** - Incomplete features

## Advanced Configuration

### Use Few-Shot Learning

```python
config = DebtGuardianConfig(
    use_few_shot=True,  # Provides examples to LLM
    use_granular_prompting=True
)
```

### Enable Majority Voting

```python
config = DebtGuardianConfig(
    enable_majority_voting=True,
    voting_rounds=3,  # Run 3 times and vote
    voting_threshold=0.5  # 50% agreement needed
)
```

### Focus on Specific TD Types

```python
config = DebtGuardianConfig(
    td_types=["defect", "test"]  # Only check these
)
```

## Troubleshooting

### "Cannot connect to Ollama"
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start it
ollama serve
```

### "Model not found"
```bash
# Pull the model
ollama pull qwen2.5-coder:7b

# Verify
ollama list
```

### Slow Performance
- First run downloads the model (one-time)
- Subsequent analyses: 5-15 seconds
- Enable batch prompting for speed:
  ```python
  config = DebtGuardianConfig(use_batch_prompting=True)
  ```

### Out of Memory
- Requires ~4GB free RAM
- Close other applications
- Or reduce context:
  ```python
  config = DebtGuardianConfig(max_tokens=2048)
  ```

## Integration Examples

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
python scripts/check_debt.py
if [ $? -ne 0 ]; then
    echo "❌ Technical debt detected!"
    exit 1
fi
```

### GitHub Actions

```yaml
- name: Check Technical Debt
  run: |
    ollama pull qwen2.5-coder:7b
    python scripts/check_debt.py
```

### VS Code Task

```json
{
  "label": "Check Technical Debt",
  "type": "shell",
  "command": "python examples/analyze_sample.py"
}
```

## Next Steps

1. 📖 Read full docs: [docs/DEBT_GUARDIAN.md](DEBT_GUARDIAN.md)
2. 🔧 Try different configurations
3. 🧪 Run tests: `pytest tests/test_debt_guardian.py`
4. 🚀 Integrate into your workflow

## Need Help?

- Check logs in `./storage/debt_guardian/`
- Open an issue on GitHub
- Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Performance Benchmarks

Based on the research paper:
- **Qwen2.5-Coder:7b**: 77% recall
- **Granular prompting**: Best precision
- **Majority voting**: +8% recall boost
- **10-line threshold**: Optimal balance

---

**Happy Debt Hunting! 🔍**
