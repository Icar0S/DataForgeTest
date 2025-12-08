#!/usr/bin/env python3
"""
DebtGuardian Setup Checker

This script verifies that all components are properly installed and configured.
"""
import sys
import os
import subprocess

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def print_header(text):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_check(item, status, message=""):
    """Print a check result"""
    symbol = "✓" if status else "✗"
    status_text = "OK" if status else "FAIL"
    print(f"{symbol} {item:40} [{status_text}]")
    if message:
        print(f"  → {message}")


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    ok = version.major == 3 and version.minor >= 8
    msg = f"Python {version.major}.{version.minor}.{version.micro}"
    print_check("Python 3.8+", ok, msg)
    return ok


def check_dependency(module_name, import_name=None):
    """Check if a Python module is installed"""
    if import_name is None:
        import_name = module_name
    
    try:
        __import__(import_name)
        print_check(f"Python: {module_name}", True)
        return True
    except ImportError:
        print_check(f"Python: {module_name}", False, f"Run: pip install {module_name}")
        return False


def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        ok = result.returncode == 0
        version = result.stdout.strip() if ok else ""
        print_check("Ollama installed", ok, version or "Run: curl -fsSL https://ollama.ai/install.sh | sh")
        return ok
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print_check("Ollama installed", False, "Download from https://ollama.ai")
        return False


def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        ok = response.status_code == 200
        print_check("Ollama service running", ok, 
                   "Ollama is running" if ok else "Run: ollama serve")
        return ok
    except Exception:
        print_check("Ollama service running", False, "Run: ollama serve")
        return False


def check_model_available():
    """Check if Qwen2.5-Coder:7b is available"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            ok = "qwen2.5-coder:7b" in result.stdout
            print_check("Model: qwen2.5-coder:7b", ok,
                       "Model available" if ok else "Run: ollama pull qwen2.5-coder:7b")
            return ok
        else:
            print_check("Model: qwen2.5-coder:7b", False, "Cannot check models")
            return False
    except Exception:
        print_check("Model: qwen2.5-coder:7b", False, "Cannot check models")
        return False


def check_debtguardian_imports():
    """Check if DebtGuardian can be imported"""
    try:
        from debt_guardian.config import DebtGuardianConfig
        from debt_guardian.detector import DebtDetector
        from debt_guardian.schemas.td_schema import TechnicalDebtInstance
        print_check("DebtGuardian imports", True)
        return True
    except Exception as e:
        print_check("DebtGuardian imports", False, str(e))
        return False


def check_debtguardian_connection():
    """Check if DebtGuardian can connect to Ollama"""
    try:
        from debt_guardian.config import DebtGuardianConfig
        from debt_guardian.llm_client import OllamaClient
        
        config = DebtGuardianConfig()
        client = OllamaClient(config)
        ok = client.health_check()
        print_check("DebtGuardian → Ollama", ok,
                   "Connection OK" if ok else "Cannot connect")
        return ok
    except Exception as e:
        print_check("DebtGuardian → Ollama", False, str(e))
        return False


def run_quick_test():
    """Run a quick analysis test"""
    try:
        from debt_guardian.config import DebtGuardianConfig
        from debt_guardian.detector import DebtDetector
        
        print("\nRunning quick test analysis...")
        print("(This may take 10-20 seconds...)")
        
        config = DebtGuardianConfig(
            td_types=["design"],
            use_granular_prompting=True
        )
        detector = DebtDetector(config)
        
        test_diff = "+def test():\n+    pass"
        
        report = detector.detect_in_diff(
            code_diff=test_diff,
            file_path="test.py"
        )
        
        print_check("Quick test analysis", True, 
                   f"Analyzed successfully (found {report.debt_count} debts)")
        return True
        
    except Exception as e:
        print_check("Quick test analysis", False, str(e))
        return False


def main():
    """Run all checks"""
    print_header("DebtGuardian Setup Checker")
    print("\nThis script will verify your DebtGuardian installation.\n")
    
    all_ok = True
    
    # Phase 1: Python environment
    print_header("Phase 1: Python Environment")
    all_ok &= check_python_version()
    
    # Phase 2: Python dependencies
    print_header("Phase 2: Python Dependencies")
    all_ok &= check_dependency("Flask")
    all_ok &= check_dependency("pydantic")
    all_ok &= check_dependency("ollama")
    all_ok &= check_dependency("GitPython", "git")
    all_ok &= check_dependency("guardrails-ai", "guardrails")
    
    # Phase 3: Ollama setup
    print_header("Phase 3: Ollama Setup")
    ollama_installed = check_ollama_installed()
    all_ok &= ollama_installed
    
    if ollama_installed:
        ollama_running = check_ollama_running()
        all_ok &= ollama_running
        
        if ollama_running:
            all_ok &= check_model_available()
    
    # Phase 4: DebtGuardian
    print_header("Phase 4: DebtGuardian Framework")
    imports_ok = check_debtguardian_imports()
    all_ok &= imports_ok
    
    if imports_ok and ollama_installed and check_ollama_running():
        all_ok &= check_debtguardian_connection()
    
    # Phase 5: Integration test
    if all_ok:
        print_header("Phase 5: Integration Test")
        all_ok &= run_quick_test()
    
    # Summary
    print_header("Summary")
    
    if all_ok:
        print("\n✅ ALL CHECKS PASSED!")
        print("\nYour DebtGuardian installation is ready to use.")
        print("\nNext steps:")
        print("  1. Run example: python examples/analyze_sample.py")
        print("  2. Read docs: docs/DEBT_GUARDIAN_QUICKSTART.md")
        print("  3. Start testing on your projects!")
    else:
        print("\n⚠️  SOME CHECKS FAILED")
        print("\nPlease fix the issues marked with ✗ above.")
        print("\nCommon fixes:")
        print("  • Install missing dependencies: pip install -r requirements.txt")
        print("  • Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print("  • Start Ollama: ollama serve")
        print("  • Pull model: ollama pull qwen2.5-coder:7b")
        print("\nFor detailed setup instructions, see: SETUP_TESTING_GUIDE.md")
    
    print()
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
