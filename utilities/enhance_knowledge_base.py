"""Investigate RAG knowledge base and add proper documentation."""

import sys
import os
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


def investigate_knowledge_base():
    """Check what's currently in the RAG knowledge base."""
    print("=" * 70)
    print("RAG KNOWLEDGE BASE INVESTIGATION")
    print("=" * 70)

    try:
        from rag.simple_rag import SimpleRAG
        from rag.config_simple import RAGConfig

        config = RAGConfig.from_env()
        rag = SimpleRAG(config)

        print(f"\n📊 CURRENT STATE:")
        print(f"   Documents: {len(rag.documents)}")
        print(f"   Chunks: {len(rag.document_chunks)}")
        print(f"   Storage path: {config.storage_path}")

        print(f"\n📝 EXISTING DOCUMENTS:")
        for i, (doc_id, doc_data) in enumerate(rag.documents.items()):
            print(f"   {i+1}. ID: {doc_id[:8]}...")
            print(f"      Metadata: {doc_data.get('metadata', {})}")
            print(f"      Content: {doc_data.get('content', '')[:100]}...")
            print()

        print(f"\n🔍 TESTING SEARCH:")
        test_queries = [
            "data quality",
            "testing",
            "validation",
            "pyspark",
            "dataset",
            "quality",
        ]

        for query in test_queries:
            results = rag.search(query, top_k=3)
            print(f"   Query: '{query}' -> {len(results)} results")
            for j, result in enumerate(results[:2]):  # Show top 2
                print(f"     {j+1}. Score: {result.get('score', 0):.3f}")
                print(f"        Text: {result.get('text', '')[:80]}...")

        return rag

    except Exception as e:
        print(f"❌ Error investigating knowledge base: {e}")
        import traceback

        traceback.print_exc()
        return None


def add_data_quality_documentation(rag):
    """Add comprehensive data quality documentation to RAG."""
    print(f"\n📚 ADDING DATA QUALITY DOCUMENTATION:")

    # Data Quality Testing Guide
    data_quality_guide = """
    # Data Quality Testing Guide
    
    Data quality testing is a critical process that ensures the accuracy, completeness, consistency, and reliability of data used in applications and analytics.
    
    ## Key Data Quality Dimensions
    
    1. **Accuracy**: Data correctly represents the real-world values
    2. **Completeness**: All required data is present
    3. **Consistency**: Data is uniform across different sources
    4. **Timeliness**: Data is up-to-date and available when needed
    5. **Validity**: Data conforms to defined formats and business rules
    6. **Uniqueness**: No duplicate records exist where they shouldn't
    
    ## Common Data Quality Issues
    
    - **NULL Values**: Missing data in required fields
    - **Duplicates**: Complete or partial record duplication
    - **Out of Range**: Values outside expected bounds
    - **Invalid Format**: Incorrect format for emails, IDs, dates
    - **Inconsistent Data**: Contradictory field values
    - **Missing Foreign Keys**: Invalid references to other tables
    - **Wrong Data Types**: Incorrect data type assignments
    
    ## Data Quality Testing Process
    
    1. **Define Quality Rules**: Establish what constitutes good data
    2. **Data Profiling**: Analyze existing data to understand patterns
    3. **Validation Testing**: Check data against defined rules
    4. **Anomaly Detection**: Identify outliers and unusual patterns
    5. **Reporting**: Generate quality metrics and reports
    6. **Remediation**: Fix identified data quality issues
    
    ## PySpark for Data Quality
    
    PySpark is excellent for data quality testing due to its distributed computing capabilities:
    
    ```python
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, count, isnan, when
    
    # Check for null values
    df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns]).show()
    
    # Find duplicates
    duplicates = df.groupBy(df.columns).count().filter(col("count") > 1)
    
    # Data validation
    invalid_emails = df.filter(~col("email").rlike(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"))
    ```
    
    ## Best Practices
    
    - Implement data quality checks early in the pipeline
    - Use automated testing and monitoring
    - Establish data quality SLAs
    - Document all quality rules and thresholds
    - Regular data profiling and quality assessment
    """

    doc_id = rag.add_document(
        data_quality_guide,
        {
            "filename": "data_quality_guide.md",
            "title": "Data Quality Testing Guide",
            "type": "documentation",
        },
    )
    print(f"   ✓ Added Data Quality Guide: {doc_id[:8]}...")

    # PySpark Testing Patterns
    pyspark_patterns = """
    # PySpark Data Quality Testing Patterns
    
    ## Setting Up Spark for Data Quality Testing
    
    ```python
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import *
    from pyspark.sql.types import *
    
    spark = SparkSession.builder \
        .appName("DataQualityTesting") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    ```
    
    ## Common Data Quality Checks
    
    ### 1. Null Value Detection
    ```python
    def check_nulls(df, columns=None):
        if columns is None:
            columns = df.columns
        
        null_counts = df.select([
            count(when(col(c).isNull() | (col(c) == ""), c)).alias(f"{c}_nulls")
            for c in columns
        ]).collect()[0]
        
        return {col: count for col, count in null_counts.asDict().items() if count > 0}
    ```
    
    ### 2. Duplicate Detection
    ```python
    def find_duplicates(df, subset=None):
        return df.groupBy(subset if subset else df.columns) \
                 .count() \
                 .filter(col("count") > 1) \
                 .orderBy(desc("count"))
    ```
    
    ### 3. Data Type Validation
    ```python
    def validate_data_types(df, expected_schema):
        actual_types = {field.name: field.dataType for field in df.schema.fields}
        expected_types = {field.name: field.dataType for field in expected_schema.fields}
        
        mismatches = {}
        for column, expected_type in expected_types.items():
            if column in actual_types and actual_types[column] != expected_type:
                mismatches[column] = {
                    'expected': expected_type,
                    'actual': actual_types[column]
                }
        return mismatches
    ```
    
    ### 4. Range Validation
    ```python
    def check_ranges(df, column, min_val=None, max_val=None):
        out_of_range = df.filter(
            (col(column) < min_val if min_val is not None else lit(False)) |
            (col(column) > max_val if max_val is not None else lit(False))
        )
        return out_of_range.count()
    ```
    
    ### 5. Format Validation
    ```python
    def validate_email_format(df, email_column):
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return df.filter(~col(email_column).rlike(email_pattern))
    
    def validate_phone_format(df, phone_column):
        phone_pattern = r"^\+?1?-?\d{3}-?\d{3}-?\d{4}$"
        return df.filter(~col(phone_column).rlike(phone_pattern))
    ```
    
    ## Advanced Quality Metrics
    
    ### Statistical Profiling
    ```python
    def profile_numeric_column(df, column):
        stats = df.select(
            count(column).alias("count"),
            countDistinct(column).alias("distinct_count"),
            min(column).alias("min_value"),
            max(column).alias("max_value"),
            mean(column).alias("mean"),
            stddev(column).alias("stddev"),
            expr(f"percentile_approx({column}, 0.5)").alias("median")
        ).collect()[0]
        
        return stats.asDict()
    ```
    
    ### Custom Quality Rules
    ```python
    def apply_business_rules(df):
        quality_issues = []
        
        # Rule: Age should be between 0 and 120
        invalid_ages = df.filter((col("age") < 0) | (col("age") > 120)).count()
        if invalid_ages > 0:
            quality_issues.append(f"Found {invalid_ages} records with invalid ages")
        
        # Rule: End date should be after start date
        invalid_dates = df.filter(col("end_date") < col("start_date")).count()
        if invalid_dates > 0:
            quality_issues.append(f"Found {invalid_dates} records with invalid date ranges")
        
        return quality_issues
    ```
    """

    doc_id = rag.add_document(
        pyspark_patterns,
        {
            "filename": "pyspark_quality_patterns.md",
            "title": "PySpark Data Quality Testing Patterns",
            "type": "documentation",
        },
    )
    print(f"   ✓ Added PySpark Patterns: {doc_id[:8]}...")

    # DataForgeTest specific documentation
    dataforge_docs = """
    # DataForgeTest System Documentation
    
    DataForgeTest is an advanced data quality testing system that uses Large Language Models (LLMs) and automated PySpark validation to test data-intensive systems.
    
    ## System Architecture
    
    ### 1. LLM 1: Dataset Generation
    - Generates synthetic datasets with deliberate anomalies
    - Creates `SyntheticDataset` with documented `ExpectedProblems`
    - Each problem is catalogued with type, location, and expected detection method
    
    ### 2. LLM 2: Code Generation
    - Analyzes the dataset and generates comprehensive PySpark validation code
    - Creates `GeneratedPySparkCode` with validation functions
    - Includes dependencies and execution instructions
    
    ### 3. Execution & Analytics
    - Executes the generated PySpark code against the synthetic dataset
    - Generates `ValidationLog` with all `DetectedIssues`
    - Captures execution metrics and performance data
    
    ### 4. Evaluation & Metrics
    - Compares `ExpectedProblems` against `DetectedIssues`
    - Generates `ComparisonResult` with precision/recall metrics
    - Provides detailed matching analysis
    
    ## Data Structures
    
    ### SyntheticDataset
    - `dataset_id`: Unique identifier
    - `schema`: Map of field names to data types
    - `data`: List of records in JSON format
    - `row_count`: Total number of generated rows
    - `generation_prompt`: LLM prompt used for generation
    
    ### ExpectedProblems
    - `dataset_id`: Reference to the dataset
    - `problems`: List of injected data quality issues
    - `total_issues`: Count of all problems
    - `issue_distribution`: Breakdown by problem type
    
    ### Problem Types
    - `NULL_VALUE`: Missing values in required fields
    - `DUPLICATE`: Complete or partial record duplication
    - `OUT_OF_RANGE`: Values outside expected bounds
    - `INVALID_FORMAT`: Incorrect format (email, ID, date)
    - `INCONSISTENT`: Contradictory field values
    - `MISSING_FK`: Invalid foreign key references
    - `WRONG_TYPE`: Incorrect data type
    
    ## Usage Examples
    
    ### Starting a Data Quality Test
    1. Click "Start Checklist Testing" on the homepage
    2. Follow the guided questions about your dataset
    3. Provide dataset information and quality requirements
    4. Review generated validation code
    5. Execute tests and review results
    
    ### Using RAG Support
    1. Click "Support RAG" to access AI-powered documentation
    2. Ask questions about data quality testing
    3. Get specific guidance on PySpark implementations
    4. Learn about best practices and common issues
    
    ## Best Practices
    
    - Start with clear data quality requirements
    - Use representative test datasets
    - Validate both expected and unexpected scenarios
    - Monitor performance metrics during testing
    - Document all quality rules and thresholds
    - Regular review and updates of quality standards
    """

    doc_id = rag.add_document(
        dataforge_docs,
        {
            "filename": "dataforge_system_docs.md",
            "title": "DataForgeTest System Documentation",
            "type": "system_documentation",
        },
    )
    print(f"   ✓ Added DataForge Docs: {doc_id[:8]}...")

    print(f"\n📊 UPDATED STATE:")
    print(f"   Documents: {len(rag.documents)}")
    print(f"   Chunks: {len(rag.document_chunks)}")

    return True


def test_improved_responses(rag):
    """Test if the RAG now gives better responses."""
    print(f"\n🧪 TESTING IMPROVED RESPONSES:")

    try:
        from rag.simple_chat import SimpleChatEngine

        chat = SimpleChatEngine(rag)

        test_questions = [
            "What is data quality testing?",
            "How do I check for null values in PySpark?",
            "What are the main data quality dimensions?",
            "How does DataForgeTest work?",
            "What types of data quality problems can be detected?",
        ]

        for question in test_questions:
            print(f"\n❓ Question: {question}")
            response = chat.chat(question)

            if response and "response" in response:
                resp_text = response["response"]
                if "I don't have specific information" in resp_text:
                    print(f"   ❌ Still generic response")
                else:
                    print(f"   ✅ Good response ({len(resp_text)} chars)")
                    print(f"   📝 Preview: {resp_text[:150]}...")

                if "citations" in response and response["citations"]:
                    print(f"   📚 Citations: {len(response['citations'])}")
            else:
                print(f"   ❌ No response generated")

    except Exception as e:
        print(f"❌ Error testing responses: {e}")


if __name__ == "__main__":
    rag = investigate_knowledge_base()

    if rag:
        print(f"\n" + "=" * 70)
        print("ADDING COMPREHENSIVE DOCUMENTATION")
        print("=" * 70)

        if add_data_quality_documentation(rag):
            test_improved_responses(rag)

            print(f"\n" + "=" * 70)
            print("✅ KNOWLEDGE BASE ENHANCED!")
            print("=" * 70)
            print("The RAG system now has comprehensive documentation about:")
            print("• Data quality testing concepts and best practices")
            print("• PySpark implementation patterns and code examples")
            print("• DataForgeTest system architecture and usage")
            print("\nTest the chat interface again - it should now provide")
            print("detailed, relevant responses instead of generic ones!")
            print("=" * 70)
        else:
            print("❌ Failed to add documentation")
    else:
        print("❌ Could not investigate knowledge base")
