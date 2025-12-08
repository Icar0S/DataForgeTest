"""
Example: Analyze a code diff for technical debt

This example demonstrates how to use DebtGuardian to analyze
a code change for technical debt.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from debt_guardian import DebtGuardianConfig, DebtDetector


def main():
    """Run the example"""
    
    print("=" * 60)
    print("DebtGuardian Example: Code Diff Analysis")
    print("=" * 60)
    print()
    
    # Sample code diff with potential technical debt
    code_diff = """
@@ -1,5 +1,15 @@
+def process_user_data(data):
+    # TODO: Add error handling
+    result = []
+    for item in data:
+        # No validation of item structure
+        result.append({
+            'name': item['name'],
+            'email': item['email'],
+            'age': item['age']
+        })
+    return result
+
+# Missing unit tests for this function
"""
    
    print("Code Diff to Analyze:")
    print("-" * 60)
    print(code_diff)
    print("-" * 60)
    print()
    
    # Configure DebtGuardian
    print("Configuring DebtGuardian...")
    config = DebtGuardianConfig(
        llm_model="qwen2.5-coder:7b",
        ollama_base_url="http://localhost:11434",
        use_granular_prompting=True,  # High precision
        use_few_shot=False,  # Zero-shot for this example
        td_types=["design", "documentation", "defect", "test"],
        enable_guardrails=True
    )
    print(f"✓ Using model: {config.llm_model}")
    print(f"✓ Prompting strategy: {'granular' if config.use_granular_prompting else 'batch'}")
    print(f"✓ TD types: {', '.join(config.td_types)}")
    print()
    
    # Initialize detector
    print("Initializing detector...")
    try:
        detector = DebtDetector(config)
        print("✓ Detector initialized")
    except Exception as e:
        print(f"✗ Error initializing detector: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Pull the model: ollama pull qwen2.5-coder:7b")
        print("3. Check connectivity: curl http://localhost:11434/api/tags")
        return
    print()
    
    # Run detection
    print("Analyzing code diff for technical debt...")
    print("This may take 10-30 seconds...")
    print()
    
    try:
        report = detector.detect_in_diff(
            code_diff=code_diff,
            file_path="src/user_processor.py"
        )
        
        # Display results
        print("=" * 60)
        print("Analysis Results")
        print("=" * 60)
        print()
        
        print(f"File: {report.file_path}")
        print(f"Model: {report.model_used}")
        print(f"Strategy: {report.prompting_strategy}")
        print(f"Lines analyzed: {report.total_lines_analyzed}")
        print(f"Timestamp: {report.analysis_timestamp}")
        print()
        
        print(f"Technical Debt Detected: {report.debt_count} instances")
        print()
        
        if report.debt_count == 0:
            print("✓ No technical debt detected!")
        else:
            # Group by type
            print("By Type:")
            for debt_type, count in report.debt_by_type.items():
                print(f"  - {debt_type}: {count}")
            print()
            
            # Display each debt
            for i, debt in enumerate(report.detected_debts, 1):
                print(f"Debt #{i}: {debt.debt_type.upper()}")
                print("-" * 40)
                print(f"Symptom: {debt.symptom}")
                print(f"Location: Lines {debt.location.start_line}-{debt.location.end_line}")
                print(f"Severity: {debt.severity}")
                print(f"Confidence: {debt.confidence:.2f}")
                if debt.suggested_remediation:
                    print(f"Remediation: {debt.suggested_remediation}")
                if debt.code_snippet:
                    print(f"Code:")
                    print(f"  {debt.code_snippet[:100]}...")
                print()
        
        # Summary
        print("=" * 60)
        print("Summary")
        print("=" * 60)
        high_severity = report.high_severity_count
        if high_severity > 0:
            print(f"⚠️  {high_severity} high/critical severity issues found!")
            print("   These should be addressed immediately.")
        else:
            print("✓ No high-severity issues detected.")
        print()
        
    except Exception as e:
        print(f"✗ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("Example completed successfully!")


if __name__ == "__main__":
    main()
