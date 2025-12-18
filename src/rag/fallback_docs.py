"""Fallback documents for RAG when documents.json is missing."""

FALLBACK_DOCUMENTS = {
    "spark_best_practices": {
        "content": """Apache Spark Best Practices for Data Quality

Introduction: Apache Spark is a powerful distributed computing framework that excels at processing large datasets. Following best practices ensures data quality and optimal performance.

Key Best Practices:

1. Data Partitioning
- Partition data appropriately based on data size and cluster resources
- Use repartition() or coalesce() to optimize partition count
- Avoid skewed partitions which can cause performance bottlenecks

2. Caching and Persistence
- Cache DataFrames that are reused multiple times
- Choose appropriate storage levels (MEMORY_ONLY, MEMORY_AND_DISK, etc.)
- Unpersist data when no longer needed to free memory

3. Data Quality Checks
- Validate data schemas before processing
- Check for null values and handle them appropriately  
- Implement data quality metrics and monitoring
- Use DataFrame assertions to catch issues early

4. Performance Optimization
- Avoid wide transformations when possible
- Use broadcast joins for small lookup tables
- Filter data as early as possible in the pipeline
- Minimize shuffles by using proper partitioning

5. Testing Strategies
- Write unit tests for transformations
- Implement integration tests with sample datasets
- Use schema validation to catch data issues
- Monitor data quality metrics in production

6. Error Handling
- Implement proper exception handling
- Log errors with context for debugging
- Use try-catch blocks for fault tolerance
- Implement retry logic for transient failures
""",
        "metadata": {"filename": "spark_best_practices.txt", "source": "internal_docs"},
    },
    "data_validation": {
        "content": """Data Validation Strategies for Big Data

Overview: Data validation is crucial for maintaining data quality in big data systems. Effective validation catches issues early and prevents downstream problems.

Validation Approaches:

1. Schema Validation
- Enforce data types and formats
- Validate column names and structure
- Check for required fields
- Ensure consistency across datasets

2. Data Quality Dimensions
- Accuracy: Data correctly represents real-world values
- Completeness: All required data is present
- Consistency: Data is uniform across systems
- Timeliness: Data is up-to-date and available when needed
- Validity: Data conforms to defined formats and ranges

3. Validation Techniques
- Range checks: Ensure values fall within expected bounds
- Format validation: Verify data matches expected patterns
- Reference data validation: Check against known valid values
- Cross-field validation: Ensure related fields are consistent
- Duplicate detection: Identify and handle duplicate records

4. Big Data Specific Challenges
- Scale: Validating billions of records efficiently
- Velocity: Validating streaming data in real-time
- Variety: Handling different data formats and sources
- Veracity: Dealing with uncertain or imprecise data

5. Implementation Best Practices
- Validate data as early as possible in the pipeline
- Use sampling for preliminary checks on large datasets
- Implement both automated and manual validation
- Document validation rules and their business rationale
- Monitor validation metrics over time

6. Tools and Frameworks
- Apache Spark for distributed validation
- Great Expectations for validation rules
- Apache Nifi for data flow validation
- Custom validation frameworks
""",
        "metadata": {
            "filename": "data_validation_strategies.md",
            "source": "internal_docs",
        },
    },
    "testing_strategies": {
        "content": """Big Data Testing Strategies

Introduction: Testing big data applications requires specialized approaches due to scale, complexity, and distributed nature of systems.

Testing Levels:

1. Unit Testing
- Test individual functions and transformations
- Use small, representative datasets
- Mock external dependencies
- Validate business logic in isolation

2. Integration Testing
- Test interactions between components
- Validate data flow through pipelines
- Test with realistic data volumes
- Verify system integrations

3. Performance Testing
- Measure throughput and latency
- Test scalability with increasing data volumes
- Identify performance bottlenecks
- Validate SLAs and performance requirements

4. Data Quality Testing
- Validate data accuracy and completeness
- Check for data anomalies and outliers
- Verify data transformations
- Test error handling and recovery

Testing Approaches:

1. Sampling
- Use representative data samples for quick tests
- Implement stratified sampling for diverse data
- Balance test speed with coverage

2. Production-like Environments
- Test with production-scale data when possible
- Use realistic hardware configurations
- Simulate production load patterns

3. Automated Testing
- Implement CI/CD pipelines for data applications
- Automate regression testing
- Use data quality monitoring tools
- Implement automated alerting

Best Practices:
- Start testing early in development
- Maintain test data that represents edge cases
- Document test scenarios and expected results
- Monitor and track data quality metrics
- Implement continuous testing in production
""",
        "metadata": {"filename": "performance_testing.md", "source": "internal_docs"},
    },
}
