# Data Accuracy Integration Tests - Quick Start Guide

## 🎯 Overview

This directory contains comprehensive integration tests for the **Data Accuracy (Datasets)** feature. The test suite validates end-to-end functionality including file uploads, data comparison, correction, and download workflows.

## 📊 Test Statistics

- **Total Tests**: 31
- **Test Files**: 3
- **Pass Rate**: 100%
- **Execution Time**: ~1.5 seconds
- **Coverage**: Backend logic, API endpoints, file handling, normalization, security

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov
```

### Run All Accuracy Tests

```bash
# From project root
python -m pytest tests/test_accuracy*.py -v
```

### Run Specific Test Suites

```bash
# Backend unit tests (normalization, comparison logic)
python -m pytest tests/test_accuracy_backend.py -v

# Basic integration tests (health check, full workflow)
python -m pytest tests/test_accuracy_integration.py -v

# Robust integration tests (18 comprehensive scenarios)
python -m pytest tests/test_accuracy_integration_robust.py -v
```

## 📋 Test Suite Breakdown

### 1. Backend Unit Tests (`test_accuracy_backend.py`) - 9 tests

**Focus**: Core processing logic

- Column name normalization (snake_case conversion)
- Accent stripping (café → cafe)
- Key value normalization
- Numeric coercion (handles "1.234,56" and "1,234.56")
- Basic comparison and correction
- Duplicate handling
- Tolerance-based comparison

### 2. Basic Integration Tests (`test_accuracy_integration.py`) - 4 tests

**Focus**: Essential end-to-end workflows

- Health check endpoint
- Complete upload → compare → download workflow
- Invalid file type handling
- Duplicate error handling

### 3. Robust Integration Tests (`test_accuracy_integration_robust.py`) - 18 tests

**Focus**: Comprehensive real-world scenarios

#### File Format Support
- ✅ CSV format
- ✅ XLSX (Excel) format
- ✅ Parquet format

#### Multi-Column Scenarios
- ✅ Composite keys (multiple key columns)
- ✅ Multiple value columns comparison

#### Data Normalization
- ✅ Case-insensitive comparison
- ✅ Accent stripping (João → Joao)
- ✅ Punctuation removal
- ✅ European number format (1.234,56)
- ✅ Special characters (María, François)

#### Edge Cases
- ✅ Empty target datasets
- ✅ Missing columns error handling
- ✅ Extra keys in target
- ✅ Large datasets (1000+ rows)

#### Duplicate Policies
- ✅ Keep last (default)
- ✅ Sum aggregation
- ✅ Mean aggregation

#### Quality & Security
- ✅ Tolerance precision testing
- ✅ Accuracy metrics validation
- ✅ Download security (path traversal protection)
- ✅ Session management
- ✅ Required field validation

## 🎓 Test Examples

### Example 1: Multi-Column Key Comparison

```python
# Test: test_multiple_key_columns
# Tests composite key matching with Region + Product

GOLD Dataset:
  Região   | Produto | Preço
  Norte    | Café    | 10.0
  Norte    | Açúcar  | 5.0
  Sul      | Café    | 12.0

TARGET Dataset:
  Região   | Produto | Preço
  Norte    | Café    | 10.0
  Norte    | Açúcar  | 5.5  ← Difference detected
  Sul      | Café    | 12.0

Result: 1 mismatch on composite key (Norte, Açúcar)
```

### Example 2: European Number Format

```python
# Test: test_numeric_format_european
# Tests automatic conversion of European number format

GOLD Dataset (US format):
  Produto | Preço
  A       | 1234.56
  B       | 5678.90

TARGET Dataset (European format):
  Produto | Preço
  A       | "1.234,56"  ← Automatically converted
  B       | "5.678,90"  ← Automatically converted

Result: 0 mismatches (after numeric coercion)
```

### Example 3: Duplicate Handling with Sum

```python
# Test: test_duplicate_policy_sum
# Tests sum aggregation for duplicate keys

GOLD Dataset:
  Product | Amount
  A       | 100
  B       | 200

TARGET Dataset (with duplicates):
  Product | Amount
  A       | 50  ← Duplicates
  A       | 50  ← will be summed
  B       | 200

After deduplication with 'sum' policy:
  Product | Amount
  A       | 100  ← Sum of duplicates
  B       | 200

Result: 0 mismatches
```

## 🔬 Running Tests with Coverage

```bash
# Generate HTML coverage report
python -m pytest tests/test_accuracy*.py --cov=src/accuracy --cov-report=html

# View report
open htmlcov/index.html  # or your browser
```

## 📈 Test Data Patterns

The tests use realistic data patterns:

- **Brazilian Portuguese**: Café, Açúcar, Arroz (tests accent handling)
- **International Names**: João da Silva, María José, François Müller
- **Number Formats**: Both European (1.234,56) and US (1,234.56)
- **Datasets**: From empty to 1000 rows
- **Keys**: Simple and composite keys
- **Values**: Integers, floats, various precision

## 🐛 Debugging Failed Tests

```bash
# Run with verbose output and stop at first failure
python -m pytest tests/test_accuracy_integration_robust.py -v -x

# Run specific test with detailed output
python -m pytest tests/test_accuracy_integration_robust.py::TestDataAccuracyRobust::test_large_dataset_handling -v -s

# Run with pdb debugger on failure
python -m pytest tests/test_accuracy_integration_robust.py --pdb
```

## 📝 Adding New Tests

When adding new test cases:

1. **Choose the right file**:
   - Backend logic → `test_accuracy_backend.py`
   - Simple integration → `test_accuracy_integration.py`
   - Complex scenarios → `test_accuracy_integration_robust.py`

2. **Follow naming convention**:
   - Use descriptive names: `test_<feature>_<scenario>`
   - Example: `test_duplicate_policy_sum`

3. **Use realistic data**:
   - Real-world patterns (Brazilian names, European formats)
   - Edge cases (empty, special chars, large datasets)

4. **Assert comprehensively**:
   - Verify status codes
   - Check response structure
   - Validate business logic
   - Test error messages

5. **Clean up**:
   - Use `setup_method` and `teardown_method`
   - Clean up temporary files

## 📚 Additional Documentation

- **Detailed Coverage**: See `TEST_COVERAGE_ACCURACY.md`
- **API Reference**: See `/src/accuracy/routes.py` docstrings
- **Feature Overview**: See main `README.md`

## 🎯 Test Objectives Met

✅ **Robustness**: Tests handle edge cases, errors, and invalid input
✅ **Coverage**: All major features and options tested
✅ **Performance**: Large dataset handling validated (1000 rows)
✅ **Security**: Path traversal and access control tested
✅ **Real-world**: Tests use realistic data patterns
✅ **Maintainability**: Well-documented, organized, and easy to extend

## 💡 Tips

- Run tests before committing code changes
- Use `-v` flag for detailed test names
- Use `-k` to run tests matching a pattern: `pytest -k "test_duplicate"`
- Tests are designed to be independent and can run in any order
- All tests clean up their temporary files automatically

## 🚦 CI/CD Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Data Accuracy Tests
  run: |
    pip install -r requirements.txt
    pip install pytest pytest-cov
    pytest tests/test_accuracy*.py -v --cov=src/accuracy
```

---

**Questions or Issues?** Check the main project README or open an issue on GitHub.
