import sys
sys.path.append('C:/Users/Icaro/OneDrive/Documents/projetos-google-cli/data-quality-chatbot')

from src.dsl_parser.generator import generate_dsl
from src.code_generator.pyspark_generator import generate_pyspark_code
from tests.sample_answers import SAMPLE_ANSWERS, SAMPLE_ANSWERS_WITH_ERRORS
import json

if __name__ == "__main__":
    print("\n--- Testing with valid sample answers ---")
    dsl_valid = generate_dsl(SAMPLE_ANSWERS)
    print("Generated DSL:")
    print(json.dumps(dsl_valid, indent=4))
    
    print("\nGenerated PySpark Code (from valid DSL):")
    pyspark_code_valid = generate_pyspark_code(dsl_valid)
    print(pyspark_code_valid)

    # Assertions for cross_column_comparison in DSL
    cross_column_rule_found_dsl = False
    for rule in dsl_valid.get("rules", []):
        if rule.get("type") == "cross_column_comparison":
            if rule.get("column1") == "start_date" and rule.get("operator") == "<" and rule.get("column2") == "end_date":
                cross_column_rule_found_dsl = True
            if rule.get("column1") == "price" and rule.get("operator") == ">" and rule.get("column2") == "cost":
                cross_column_rule_found_dsl = True
    assert cross_column_rule_found_dsl, "Cross-column comparison rule not found or incorrect in DSL."
    print("DSL cross-column comparison rule assertion PASSED.")

    # Assertions for cross_column_comparison in PySpark code
    assert "Checking cross-column comparison: start_date < end_date" in pyspark_code_valid, "PySpark code for start_date < end_date not found."
    assert "failed_comparison = df.filter(~(col(\"start_date\") < col(\"end_date\")))" in pyspark_code_valid, "PySpark filter for start_date < end_date not found."
    assert "Checking cross-column comparison: price > cost" in pyspark_code_valid, "PySpark code for price > cost not found."
    assert "failed_comparison = df.filter(~(col(\"price\") > col(\"cost\")))" in pyspark_code_valid, "PySpark filter for price > cost not found."
    print("PySpark cross-column comparison code assertion PASSED.")

    print("\n--- Testing with error-inducing sample answers ---")
    dsl_errors = generate_dsl(SAMPLE_ANSWERS_WITH_ERRORS)
    print("Generated DSL:")
    print(json.dumps(dsl_errors, indent=4))
    
    print("\nGenerated PySpark Code (from error-inducing DSL):")
    pyspark_code_errors = generate_pyspark_code(dsl_errors)
    print(pyspark_code_errors)