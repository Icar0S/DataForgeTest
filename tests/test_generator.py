"""Test script for DSL generation and PySpark code generation."""
import sys
import os
import json

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.dsl_parser.generator import generate_dsl
from src.code_generator.pyspark_generator import generate_pyspark_code
from tests.sample_answers import SAMPLE_ANSWERS, SAMPLE_ANSWERS_WITH_ERRORS

if __name__ == "__main__":
    print("\n--- Testing with valid sample answers ---")
    dsl_valid = generate_dsl(SAMPLE_ANSWERS)
    print("Generated DSL:")
    print(json.dumps(dsl_valid, indent=4))

    print("\nGenerated PySpark Code (from valid DSL):")
    pyspark_code_valid = generate_pyspark_code(dsl_valid)
    print(pyspark_code_valid)

    # Assertions for cross_column_comparison in DSL
    CROSS_COLUMN_RULE_FOUND_DSL = False
    for rule in dsl_valid.get("rules", []):
        if rule.get("type") == "cross_column_comparison":
            col1 = rule.get("column1")
            operator = rule.get("operator")
            col2 = rule.get("column2")
            if (col1 == "start_date" and operator == "<" and
                    col2 == "end_date"):
                CROSS_COLUMN_RULE_FOUND_DSL = True
            if (col1 == "price" and operator == ">" and
                    col2 == "cost"):
                CROSS_COLUMN_RULE_FOUND_DSL = True
    assert CROSS_COLUMN_RULE_FOUND_DSL, (
        "Cross-column comparison rule not found or incorrect in DSL.")
    print("DSL cross-column comparison rule assertion PASSED.")

    # Assertions for cross_column_comparison in PySpark code
    EXPECTED_MSG = "Checking cross-column comparison: start_date < end_date"
    assert EXPECTED_MSG in pyspark_code_valid, (
        "PySpark code for start_date < end_date not found.")
    EXPECTED_FILTER = (
        'failed_comparison = df.filter(~(col("start_date") < col("end_date")))')
    assert EXPECTED_FILTER in pyspark_code_valid, (
        "PySpark filter for start_date < end_date not found.")
    EXPECTED_MSG2 = "Checking cross-column comparison: price > cost"
    assert EXPECTED_MSG2 in pyspark_code_valid, (
        "PySpark code for price > cost not found.")
    EXPECTED_FILTER2 = (
        'failed_comparison = df.filter(~(col("price") > col("cost")))')
    assert EXPECTED_FILTER2 in pyspark_code_valid, (
        "PySpark filter for price > cost not found.")
    print("PySpark cross-column comparison code assertion PASSED.")

    print("\n--- Testing with error-inducing sample answers ---")
    dsl_errors = generate_dsl(SAMPLE_ANSWERS_WITH_ERRORS)
    print("Generated DSL:")
    print(json.dumps(dsl_errors, indent=4))

    print("\nGenerated PySpark Code (from error-inducing DSL):")
    pyspark_code_errors = generate_pyspark_code(dsl_errors)
    print(pyspark_code_errors)
