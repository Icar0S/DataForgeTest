# Data Accuracy Feature - Test Coverage Documentation

This document outlines the comprehensive test coverage for the Data Accuracy (Datasets) feature.

## Test Suite Overview

### Total Test Count: 31 tests
- **Backend Unit Tests**: 9 tests (test_accuracy_backend.py)
- **Integration Tests**: 4 tests (test_accuracy_integration.py)
- **Robust Integration Tests**: 18 tests (test_accuracy_integration_robust.py)

## Test Categories

### 1. Backend Unit Tests (`test_accuracy_backend.py`)

#### Normalization Functions (4 tests)
- `test_normalize_column_name` - Column name conversion to snake_case
- `test_strip_accents` - Accent removal from text (café → cafe)
- `test_normalize_key_value` - Key value normalization with options
- `test_coerce_numeric` - Numeric value coercion from strings

#### Compare and Correct Logic (5 tests)
- `test_simple_comparison` - Basic comparison with one mismatch
- `test_missing_keys` - Handling of missing keys in target
- `test_duplicate_in_gold_error` - Error on duplicates in GOLD dataset
- `test_duplicate_in_target_keep_last` - Duplicate handling with keep_last policy
- `test_tolerance` - Numeric comparison with tolerance

### 2. Basic Integration Tests (`test_accuracy_integration.py`)

- `test_health_check` - Health endpoint verification
- `test_full_workflow` - Complete upload → compare → download workflow
- `test_invalid_file_type` - Invalid file type rejection
- `test_duplicate_in_gold_error` - End-to-end duplicate error handling

### 3. Robust Integration Tests (`test_accuracy_integration_robust.py`)

#### Multi-Column Support (2 tests)
- `test_multiple_key_columns` - Composite key comparison (Region + Product)
- `test_multiple_value_columns` - Multiple value columns comparison

#### File Format Support (3 tests)
- `test_excel_file_format` - XLSX file upload and comparison
- `test_parquet_file_format` - Parquet file upload and comparison
- CSV format is tested in all other tests

#### Normalization & Data Handling (3 tests)
- `test_normalization_options` - Full normalization (lowercase, accents, punctuation)
- `test_numeric_format_european` - European number format (1.234,56)
- `test_special_characters_in_data` - Special characters (João, María, François)

#### Edge Cases (3 tests)
- `test_empty_target_dataset` - Empty target dataset handling
- `test_missing_column_error` - Error for non-existent columns
- `test_extra_keys_in_target` - Extra keys in target not in gold

#### Duplicate Handling Policies (2 tests)
- `test_duplicate_policy_sum` - Sum aggregation for duplicates
- `test_duplicate_policy_mean` - Mean aggregation for duplicates

#### Precision & Tolerance (1 test)
- `test_tolerance_precision` - Tolerance-based comparison with different precision levels

#### Security & Error Handling (2 tests)
- `test_download_security` - Path traversal and file access control
- `test_missing_required_fields` - Required field validation

#### Performance & Metrics (2 tests)
- `test_accuracy_metrics_calculation` - Accuracy calculation verification (70% accuracy)
- `test_large_dataset_handling` - Stress test with 1000 rows, 10% differences

#### Session Management (1 test)
- `test_session_not_found` - Non-existent session error handling

## Feature Coverage Summary

### Supported Features Tested ✓

1. **File Formats**
   - CSV (all tests)
   - XLSX (Excel)
   - Parquet

2. **Key Column Types**
   - Single key column
   - Multiple key columns (composite keys)

3. **Value Column Types**
   - Single value column
   - Multiple value columns

4. **Normalization Options**
   - Column name normalization (snake_case)
   - Key normalization (lowercase, accent stripping, punctuation removal)
   - Numeric coercion (European/US formats)
   - Decimal precision control

5. **Duplicate Handling Policies**
   - Error on duplicates (GOLD)
   - Keep last (TARGET)
   - Sum aggregation (TARGET)
   - Mean aggregation (TARGET)

6. **Comparison Features**
   - Exact matching
   - Tolerance-based comparison
   - Missing keys detection
   - Extra keys detection
   - Accuracy metrics calculation

7. **Output Generation**
   - Corrected CSV
   - Diff CSV
   - JSON report

8. **Error Handling**
   - Invalid file types
   - Missing required fields
   - Non-existent sessions
   - Missing columns
   - Duplicates in GOLD

9. **Security**
   - Path traversal protection
   - Allowed file whitelist

## Test Execution

### Run all accuracy tests:
```bash
python -m pytest tests/test_accuracy*.py -v
```

### Run specific test suites:
```bash
# Backend unit tests only
python -m pytest tests/test_accuracy_backend.py -v

# Integration tests only
python -m pytest tests/test_accuracy_integration.py -v

# Robust integration tests only
python -m pytest tests/test_accuracy_integration_robust.py -v
```

### Run with coverage:
```bash
python -m pytest tests/test_accuracy*.py --cov=src/accuracy --cov-report=html
```

## Test Data Characteristics

The tests use various realistic data scenarios:

- **Brazilian product data**: Café, Açúcar, Arroz (tests accent handling)
- **International names**: João, María, François (tests Unicode support)
- **Numeric formats**: Both European (1.234,56) and US (1,234.56)
- **Dataset sizes**: From empty to 1000 rows
- **Key complexity**: Single and composite keys
- **Value diversity**: Integers, floats, with various precision levels

## Quality Metrics

- **Total Coverage**: 31 comprehensive tests
- **Test Execution Time**: ~1.5 seconds for all tests
- **Pass Rate**: 100% (31/31 passing)
- **Code Coverage**: High coverage of core functionality
- **Edge Cases**: Extensive edge case testing including empty data, special characters, large datasets

## Recommendations for Maintenance

1. **Add tests when adding new features**: Each new option or capability should have corresponding tests
2. **Keep test data realistic**: Use real-world data patterns (Brazilian Portuguese, international names, etc.)
3. **Test performance regularly**: Monitor execution time of large_dataset_handling test
4. **Update documentation**: Keep this document in sync with test additions
5. **Run tests in CI/CD**: Ensure all tests pass before merging changes

## Future Test Enhancements

Potential areas for additional testing:

1. **Concurrency**: Multiple simultaneous sessions
2. **Memory limits**: Very large files (approaching max_upload_mb)
3. **Network failures**: Interrupted uploads
4. **Data types**: Date/datetime columns
5. **Complex schemas**: Nested JSON structures in cells
6. **Performance benchmarks**: Formal performance baselines
