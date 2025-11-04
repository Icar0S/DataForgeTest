"""Tests for dataset inspector module."""

import os
import json
import tempfile
import pandas as pd
import pytest
from src.dataset_inspector.inspector import (
    inspect_csv,
    inspect_parquet,
    inspect_json,
    detect_csv_delimiter,
    detect_encoding,
    infer_column_statistics,
    map_pandas_type_to_spark
)


@pytest.fixture
def sample_csv_file():
    """Create a sample CSV file for testing."""
    data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'age': [25, 30, 35, None, 45],
        'score': [85.5, 90.0, 75.5, 88.0, 92.5]
    }
    df = pd.DataFrame(data)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        df.to_csv(f.name, index=False)
        yield f.name
    
    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def sample_parquet_file():
    """Create a sample Parquet file for testing."""
    data = {
        'id': [1, 2, 3, 4, 5],
        'product': ['A', 'B', 'C', 'D', 'E'],
        'price': [10.5, 20.0, 15.5, 30.0, 25.5],
        'quantity': [5, 10, 15, None, 25]
    }
    df = pd.DataFrame(data)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.parquet') as f:
        df.to_parquet(f.name, index=False)
        yield f.name
    
    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def sample_json_file():
    """Create a sample JSON file for testing."""
    data = [
        {'id': 1, 'name': 'Alice', 'active': True},
        {'id': 2, 'name': 'Bob', 'active': False},
        {'id': 3, 'name': 'Charlie', 'active': True},
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(data, f)
        f.flush()  # Ensure data is written
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_detect_csv_delimiter():
    """Test CSV delimiter detection."""
    # Create CSV with semicolon delimiter
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write('id;name;value\n')
        f.write('1;Alice;100\n')
        f.write('2;Bob;200\n')
        temp_file = f.name
    
    try:
        delimiter = detect_csv_delimiter(temp_file, 'utf-8')
        assert delimiter == ';'
    finally:
        os.unlink(temp_file)


def test_infer_column_statistics():
    """Test column statistics inference."""
    df = pd.DataFrame({
        'numeric': [1, 2, 3, 4, 5],
        'string': ['a', 'b', 'c', 'd', 'e'],
        'with_nulls': [1, 2, None, 4, None]
    })
    
    # Test numeric column
    stats = infer_column_statistics(df, 'numeric')
    assert stats['name'] == 'numeric'
    assert stats['null_count'] == 0
    assert stats['null_ratio'] == 0.0
    assert stats['unique_count'] == 5
    assert 'min' in stats
    assert 'max' in stats
    assert stats['min'] == 1
    assert stats['max'] == 5
    
    # Test string column
    stats = infer_column_statistics(df, 'string')
    assert stats['name'] == 'string'
    assert 'avg_length' in stats
    assert 'sample_values' in stats
    
    # Test column with nulls
    stats = infer_column_statistics(df, 'with_nulls')
    assert stats['null_count'] == 2
    assert stats['null_ratio'] == 0.4


def test_inspect_csv(sample_csv_file):
    """Test CSV file inspection."""
    metadata = inspect_csv(sample_csv_file)
    
    assert metadata['format'] == 'csv'
    assert metadata['row_count'] == 5
    assert metadata['column_count'] == 4
    assert len(metadata['columns']) == 4
    assert len(metadata['preview']) <= 10
    
    # Check column names
    column_names = [col['name'] for col in metadata['columns']]
    assert 'id' in column_names
    assert 'name' in column_names
    assert 'age' in column_names
    assert 'score' in column_names
    
    # Check detected options
    assert 'encoding' in metadata['detected_options']
    assert 'delimiter' in metadata['detected_options']
    assert 'header' in metadata['detected_options']


def test_inspect_parquet(sample_parquet_file):
    """Test Parquet file inspection."""
    metadata = inspect_parquet(sample_parquet_file)
    
    assert metadata['format'] == 'parquet'
    assert metadata['row_count'] == 5
    assert metadata['column_count'] == 4
    assert len(metadata['columns']) == 4
    assert len(metadata['preview']) <= 10
    
    # Check column names
    column_names = [col['name'] for col in metadata['columns']]
    assert 'id' in column_names
    assert 'product' in column_names
    assert 'price' in column_names
    assert 'quantity' in column_names


def test_inspect_json(sample_json_file):
    """Test JSON file inspection."""
    metadata = inspect_json(sample_json_file)
    
    assert metadata['format'] == 'json'
    assert metadata['row_count'] == 3
    assert metadata['column_count'] == 3
    assert len(metadata['columns']) == 3
    
    # Check column names
    column_names = [col['name'] for col in metadata['columns']]
    assert 'id' in column_names
    assert 'name' in column_names
    assert 'active' in column_names


def test_map_pandas_type_to_spark():
    """Test pandas to Spark type mapping."""
    assert map_pandas_type_to_spark('int64') == 'long'
    assert map_pandas_type_to_spark('int32') == 'integer'
    assert map_pandas_type_to_spark('float64') == 'double'
    assert map_pandas_type_to_spark('object') == 'string'
    assert map_pandas_type_to_spark('bool') == 'boolean'
    assert map_pandas_type_to_spark('unknown') == 'string'  # Default
