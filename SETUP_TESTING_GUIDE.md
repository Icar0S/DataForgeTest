# DebtGuardian Setup Guide for Testing

## Purpose

This guide will help you test the DebtGuardian framework on other projects. Once successfully tested here, the configuration can be replicated to other repositories.

## Prerequisites

Before starting, ensure you have:
- Python 3.8 or higher
- Git
- At least 8GB of RAM (4GB for the model + 4GB for the OS)
- About 10GB of free disk space (5GB for Ollama + model)

## Step-by-Step Setup

### 1. Install Ollama

Ollama is a tool that lets you run Large Language Models locally.

#### On macOS:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### On Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### On Windows:
Download and install from: https://ollama.ai/download

#### Verify Installation:
```bash
ollama --version
```

### 2. Pull the Qwen2.5-Coder Model

This downloads the 7B parameter model (~4.7GB):

```bash
ollama pull qwen2.5-coder:7b
```

**Note**: First download may take 5-30 minutes depending on your internet speed.

#### Verify Model is Downloaded:
```bash
ollama list
```

You should see `qwen2.5-coder:7b` in the list.

### 3. Start Ollama Service

In a **new terminal window**, start the Ollama service:

```bash
ollama serve
```

**Keep this terminal open while using DebtGuardian.**

#### Alternative: Run as Background Service

On Linux/macOS:
```bash
# Start in background
nohup ollama serve > /tmp/ollama.log 2>&1 &

# Check it's running
curl http://localhost:11434/api/tags
```

### 4. Install Python Dependencies

From the DataForgeTest repository root:

```bash
pip install -r requirements.txt
```

This installs:
- `ollama` - Python client for Ollama
- `pydantic>=2.0.0` - Data validation
- `guardrails-ai` - Output validation
- `GitPython` - Git repository analysis

### 5. Verify Installation

Run the test suite:

```bash
# Basic unit tests (don't require Ollama)
python -m pytest tests/test_debt_guardian.py::TestSchemas -v
python -m pytest tests/test_debt_guardian.py::TestConfig -v
python -m pytest tests/test_debt_guardian.py::TestPrompts -v

# Integration tests (require Ollama to be running)
python -m pytest tests/test_debt_guardian.py::TestIntegration -v
```

All tests should pass (or skip if Ollama is not running for integration tests).

### 6. Test with Example

Run the example analysis:

```bash
python examples/analyze_sample.py
```

**Expected Output:**
```
============================================================
DebtGuardian Example: Code Diff Analysis
============================================================

Code Diff to Analyze:
------------------------------------------------------------
... (code diff) ...
------------------------------------------------------------

Configuring DebtGuardian...
✓ Using model: qwen2.5-coder:7b
✓ Prompting strategy: granular
✓ TD types: design, documentation, defect, test

Initializing detector...
✓ Detector initialized

Analyzing code diff for technical debt...
This may take 10-30 seconds...

============================================================
Analysis Results
============================================================
...
```

## Using DebtGuardian

### Option 1: Python API

```python
from debt_guardian.config import DebtGuardianConfig
from debt_guardian.detector import DebtDetector

# Configure
config = DebtGuardianConfig(
    llm_model="qwen2.5-coder:7b",
    use_granular_prompting=True,
    td_types=["design", "test", "defect"]
)

# Initialize
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
print(f"Found {report.debt_count} issues")
for debt in report.detected_debts:
    print(f"- {debt.debt_type}: {debt.symptom}")
```

### Option 2: REST API

Start the Flask server:

```bash
cd src
python api.py
```

Test the API:

```bash
# Health check
curl http://localhost:5000/api/debt-guardian/health

# Analyze code
curl -X POST http://localhost:5000/api/debt-guardian/analyze/diff \
  -H "Content-Type: application/json" \
  -d '{
    "code_diff": "+def foo():\n+    pass",
    "file_path": "test.py"
  }'
```

### Option 3: Analyze Git Repository

```python
from debt_guardian.config import DebtGuardianConfig
from debt_guardian.detector import DebtDetector

config = DebtGuardianConfig(
    repo_path="/path/to/your/repo"
)
detector = DebtDetector(config)

# Analyze last 5 commits
batch_report = detector.analyze_repository(max_commits=5)

print(f"Analyzed {batch_report.total_files} files")
print(f"Total debts: {batch_report.total_debts}")
print(f"By type: {batch_report.summary['debt_by_type']}")
```

## Configuration Options

### Prompting Strategies

**Granular (Recommended for Precision):**
```python
config = DebtGuardianConfig(
    use_granular_prompting=True,  # One TD type at a time
    td_types=["design", "test"]
)
```

**Batch (Faster):**
```python
config = DebtGuardianConfig(
    use_batch_prompting=True,  # All TD types at once
    td_types=["design", "test", "defect"]
)
```

**Few-Shot (Better Pattern Recognition):**
```python
config = DebtGuardianConfig(
    use_few_shot=True,  # Provides examples to LLM
    use_granular_prompting=True
)
```

**Majority Voting (Higher Recall):**
```python
config = DebtGuardianConfig(
    enable_majority_voting=True,
    voting_rounds=3,  # Run 3 times and vote
    voting_threshold=0.5  # 50% agreement
)
```

### Environment Variables

Create a `.env` file:

```bash
# Ollama configuration
OLLAMA_BASE_URL=http://localhost:11434
DEBT_GUARDIAN_MODEL=qwen2.5-coder:7b

# For repository analysis
DEBT_GUARDIAN_REPO_PATH=/path/to/repo

# Storage
DEBT_GUARDIAN_RESULTS_PATH=./storage/debt_guardian
```

## Testing on Other Projects

To test DebtGuardian on another project:

### Method 1: Analyze Repository Directly

```python
from debt_guardian.config import DebtGuardianConfig
from debt_guardian.detector import DebtDetector

config = DebtGuardianConfig(
    repo_path="/path/to/other/project",
    td_types=["design", "defect", "test"],
    use_granular_prompting=True
)

detector = DebtDetector(config)

# Analyze recent commits
report = detector.analyze_repository(max_commits=10)

# Save results
detector.save_report(report, filename="project_analysis")
```

### Method 2: Copy Configuration Files

1. Copy these files to the target project:
   - `src/debt_guardian/` (entire directory)
   - `requirements.txt` (merge dependencies)
   - `examples/analyze_sample.py`

2. Install dependencies in target project:
   ```bash
   pip install ollama pydantic>=2.0.0 guardrails-ai GitPython
   ```

3. Update imports if needed for the target project structure

4. Run analysis

## Troubleshooting

### Issue: "Cannot connect to Ollama"

**Solution:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve

# Or restart
pkill ollama
ollama serve
```

### Issue: "Model not found"

**Solution:**
```bash
# Pull the model again
ollama pull qwen2.5-coder:7b

# Verify
ollama list
```

### Issue: Analysis is very slow

**Possible causes and solutions:**

1. **First run**: Model is being loaded into memory (one-time delay)
2. **Low memory**: Close other applications
3. **CPU-only mode**: Ollama runs faster with GPU, but works fine on CPU
4. **Try batch mode** for faster analysis:
   ```python
   config = DebtGuardianConfig(use_batch_prompting=True)
   ```

### Issue: Out of memory errors

**Solution:**
```python
# Reduce token limit
config = DebtGuardianConfig(
    max_tokens=2048  # Default is 4096
)

# Or analyze fewer files at once
report = detector.analyze_repository(max_commits=3)
```

### Issue: Too many false positives

**Solution:**
```python
# Filter by confidence
high_conf_debts = [
    d for d in report.detected_debts 
    if d.confidence > 0.75
]

# Filter by severity
critical_debts = [
    d for d in report.detected_debts
    if d.severity in ["high", "critical"]
]
```

## Performance Expectations

Based on the research paper and testing:

- **Model Size**: ~4.7GB download
- **Memory Usage**: ~4GB RAM while running
- **Analysis Speed**: 5-15 seconds per file
- **Accuracy**: 77% recall (per paper)
- **Best Configuration**: Granular prompting with few-shot examples

## Next Steps After Testing

Once you've successfully tested DebtGuardian:

1. **Document Results**: Note accuracy and performance on your test cases
2. **Tune Configuration**: Adjust TD types, strategies based on needs
3. **Integrate into Workflow**: Add to CI/CD, pre-commit hooks, etc.
4. **Scale to Other Projects**: Apply the same configuration
5. **Share Feedback**: Report issues or improvements

## Additional Resources

- [Full Documentation](../docs/DEBT_GUARDIAN.md)
- [Quick Start Guide](../docs/DEBT_GUARDIAN_QUICKSTART.md)
- [API Reference](../docs/DEBT_GUARDIAN.md#rest-api)
- [Research Paper Summary](../docs/DEBT_GUARDIAN.md#research-paper)

## Support

If you encounter issues:

1. Check Ollama logs: `tail -f /tmp/ollama.log`
2. Check application logs: `./storage/debt_guardian/`
3. Run diagnostics: `python examples/analyze_sample.py`
4. Open an issue on GitHub with:
   - Error message
   - Python version
   - OS and RAM
   - Ollama version

---

**Good luck testing DebtGuardian! 🚀**
