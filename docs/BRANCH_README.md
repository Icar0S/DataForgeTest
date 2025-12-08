# Experimental Branch: DebtGuardian Setup

Welcome to the **DebtGuardian experimental branch**! This branch contains a complete implementation of the DebtGuardian framework for AI-powered Technical Debt detection.

## 🎯 Purpose

This branch serves as a **testing ground** for the DebtGuardian framework before broader deployment. Once tested and validated on multiple projects, the framework can be:
- Merged into the main branch
- Deployed to other repositories
- Integrated into CI/CD pipelines

## ✅ What's Included

### Complete Framework Implementation
- **14 Python modules** (~1,500 lines of code)
- **6 REST API endpoints** for integration
- **12 unit tests** (all passing)
- **7 Technical Debt types** supported
- **5 prompting strategies** implemented

### Comprehensive Documentation
- **SETUP_TESTING_GUIDE.md** - Complete setup instructions
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **docs/DEBT_GUARDIAN.md** - Full documentation
- **docs/DEBT_GUARDIAN_QUICKSTART.md** - Quick start guide
- **src/debt_guardian/README.md** - Module docs

### Tools & Examples
- **check_setup.py** - Automated setup verification
- **examples/analyze_sample.py** - Working example
- **tests/test_debt_guardian.py** - Test suite

## 🚀 Quick Start (5 Minutes)

### 1. Install Ollama
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai
```

### 2. Pull the Model
```bash
ollama pull qwen2.5-coder:7b
```

This downloads ~4.7GB (one-time). Takes 5-30 minutes depending on internet speed.

### 3. Start Ollama
```bash
# In a separate terminal
ollama serve
```

Keep this running.

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Verify Setup
```bash
python check_setup.py
```

### 6. Run Example
```bash
python examples/analyze_sample.py
```

## 📖 Documentation

Start here based on your needs:

### First Time Users
→ **docs/DEBT_GUARDIAN_QUICKSTART.md** (5-minute guide)

### Testing on Other Projects
→ **SETUP_TESTING_GUIDE.md** (complete instructions)

### Technical Details
→ **IMPLEMENTATION_SUMMARY.md** (architecture & specs)

### Full Reference
→ **docs/DEBT_GUARDIAN.md** (complete documentation)

### Module Info
→ **src/debt_guardian/README.md** (module structure)

## 🧪 Testing Strategy

### Phase 1: Local Testing (Current)
Test the framework on sample code and small repositories.

**How to test:**
1. Run `check_setup.py` to verify installation
2. Run `python examples/analyze_sample.py` for a demo
3. Run `pytest tests/test_debt_guardian.py -v` for unit tests

### Phase 2: Real Project Testing (Next)
Apply the framework to actual projects and collect metrics.

**How to test on your project:**
```python
from debt_guardian.config import DebtGuardianConfig
from debt_guardian.detector import DebtDetector

config = DebtGuardianConfig(
    repo_path="/path/to/your/project",
    td_types=["design", "defect", "test"],
    use_granular_prompting=True
)

detector = DebtDetector(config)
report = detector.analyze_repository(max_commits=10)

print(f"Found {report.total_debts} technical debt instances")
```

### Phase 3: Validation & Refinement
Based on testing feedback:
- Adjust detection thresholds
- Fine-tune prompts
- Optimize performance
- Add features

### Phase 4: Deployment
After successful testing:
- Merge to main branch
- Deploy to production
- Integrate into CI/CD
- Add to other projects

## 🎓 Research Foundation

Based on the paper: **"Detecting Technical Debt in Source Code Changes using Large Language Models"**

Key Findings:
- **Qwen2.5-Coder:7b**: 77% recall
- **Granular prompting**: Best precision
- **Majority voting**: +8% recall boost
- **10-line threshold**: Optimal balance

## 🛠️ Framework Features

### Technical Debt Types
1. **Design** - Architecture issues, code smells
2. **Documentation** - Missing or inadequate docs
3. **Defect** - Bugs, security issues
4. **Test** - Missing tests, poor coverage
5. **Compatibility** - Deprecated APIs
6. **Build** - Build/dependency issues
7. **Requirement** - Incomplete features

### Prompting Strategies
1. **Zero-shot** - No examples (fast)
2. **Few-shot** - With examples (accurate)
3. **Batch** - Multiple types at once (efficient)
4. **Granular** - One type at a time (precise)
5. **Majority Voting** - Multiple runs (robust)

### Integration Options
1. **Python API** - Direct programmatic access
2. **REST API** - HTTP endpoints
3. **Git Integration** - Analyze repositories
4. **CLI Tools** - Command-line scripts

## 📊 Test Status

### Unit Tests
```bash
pytest tests/test_debt_guardian.py -v
```

**Results**: ✅ 12/12 tests passing
- Schema validation: 5 tests
- Configuration: 4 tests
- Prompts: 3 tests

### Integration Tests
```bash
pytest tests/test_debt_guardian.py::TestIntegration -v
```

**Requires**: Ollama running with qwen2.5-coder:7b

### Example Script
```bash
python examples/analyze_sample.py
```

**Expected**: ~20 seconds, shows TD detection in action

## 🔧 Configuration

### Basic Configuration
```python
from debt_guardian.config import DebtGuardianConfig

config = DebtGuardianConfig(
    llm_model="qwen2.5-coder:7b",
    use_granular_prompting=True,
    td_types=["design", "test"]
)
```

### Advanced Configuration
```python
config = DebtGuardianConfig(
    # LLM settings
    llm_model="qwen2.5-coder:7b",
    ollama_base_url="http://localhost:11434",
    temperature=0.1,
    max_tokens=4096,
    
    # Strategy
    use_granular_prompting=True,
    use_few_shot=True,
    enable_majority_voting=True,
    voting_rounds=3,
    
    # TD types
    td_types=["design", "defect", "test"],
    
    # Git
    repo_path="/path/to/repo",
    max_commits_to_analyze=10
)
```

### Environment Variables
```bash
# .env file
OLLAMA_BASE_URL=http://localhost:11434
DEBT_GUARDIAN_MODEL=qwen2.5-coder:7b
DEBT_GUARDIAN_REPO_PATH=/path/to/repo
```

## 🐛 Troubleshooting

### Issue: Cannot connect to Ollama
```bash
# Check if running
ps aux | grep ollama

# Start it
ollama serve
```

### Issue: Model not found
```bash
# Pull the model
ollama pull qwen2.5-coder:7b

# Verify
ollama list
```

### Issue: Out of memory
- Requires ~4GB free RAM
- Close other applications
- Or use smaller batch sizes

### Issue: Slow performance
- First run loads model (one-time)
- Subsequent runs: 5-15 seconds
- Use batch mode for speed

### More Help
See **SETUP_TESTING_GUIDE.md** troubleshooting section.

## 📝 Feedback & Issues

### What to Report
- Setup issues
- Detection accuracy
- Performance problems
- Feature requests
- Documentation clarity

### How to Report
1. Test thoroughly
2. Note your environment (OS, Python version, RAM)
3. Include error messages
4. Describe expected vs actual behavior
5. Open GitHub issue or comment on PR

## 🎯 Success Criteria

Before considering this branch ready for merge:

- [ ] Successfully tested on 3+ different projects
- [ ] Accuracy validated (compare with manual review)
- [ ] Performance acceptable (< 30s per file)
- [ ] Documentation clear (tested by new users)
- [ ] No critical bugs
- [ ] Positive feedback from testers

## 🔄 Branch Status

**Current Status**: ✅ **READY FOR TESTING**

**What's Complete**:
- ✅ All code implemented
- ✅ All tests passing
- ✅ Documentation complete
- ✅ Examples working
- ✅ Tools provided

**Next Steps**:
1. Test on real projects
2. Collect metrics and feedback
3. Refine based on results
4. Consider merge to main

## 💬 Questions?

- Read the docs: Start with SETUP_TESTING_GUIDE.md
- Run the checker: `python check_setup.py`
- Try the example: `python examples/analyze_sample.py`
- Check the tests: `pytest tests/test_debt_guardian.py -v`
- Review the code: `src/debt_guardian/`

## 🙏 Acknowledgments

- Research paper authors for the DebtGuardian approach
- Ollama team for local LLM infrastructure
- Qwen2.5-Coder developers for the model
- DataForgeTest community for the platform

---

**Branch**: `copilot/setup-experimental-llm-framework`
**Version**: 0.1.0 (Experimental)
**Status**: Ready for Testing
**Last Updated**: December 8, 2024

**Happy Testing! 🚀**
