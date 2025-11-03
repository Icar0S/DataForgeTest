"""Dataset inspection module for automatic schema and statistics inference."""

import pandas as pd
import pyarrow.parquet as pq
import json
import chardet
from typing import Dict, Any, List, Optional, Tuple


# Constants
MAX_FILE_SIZE_MB = 100
SAMPLE_SIZE = 10000
PREVIEW_ROWS = 10


def detect_encoding(file_path: str) -> str:
    """Detect file encoding using chardet.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Detected encoding string (e.g., 'utf-8', 'latin-1')
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)  # Read first 10KB for detection
        result = chardet.detect(raw_data)
        return result['encoding'] or 'utf-8'


def detect_csv_delimiter(file_path: str, encoding: str) -> str:
    """Detect CSV delimiter by trying common delimiters.
    
    Args:
        file_path: Path to the CSV file
        encoding: File encoding
        
    Returns:
        Detected delimiter character
    """
    delimiters = [',', ';', '\t', '|']
    max_columns = 0
    best_delimiter = ','
    
    for delimiter in delimiters:
        try:
            df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter, nrows=5)
            num_columns = len(df.columns)
            if num_columns > max_columns:
                max_columns = num_columns
                best_delimiter = delimiter
        except Exception:
            continue
    
    return best_delimiter


def infer_column_statistics(df: pd.DataFrame, column: str, sample_size: int = SAMPLE_SIZE) -> Dict[str, Any]:
    """Infer statistics for a single column.
    
    Args:
        df: DataFrame containing the column
        column: Column name
        sample_size: Number of rows to sample for statistics
        
    Returns:
        Dictionary with column statistics
    """
    # Sample the data if it's too large
    if len(df) > sample_size:
        sample_df = df.sample(n=sample_size, random_state=42)
    else:
        sample_df = df
    
    col_data = sample_df[column]
    total_rows = len(df)
    
    stats = {
        'name': column,
        'type': str(col_data.dtype),
        'null_count': int(col_data.isna().sum()),
        'null_ratio': float(col_data.isna().sum() / len(col_data)) if len(col_data) > 0 else 0.0,
        'unique_count': int(col_data.nunique()),
        'unique_ratio': float(col_data.nunique() / len(col_data)) if len(col_data) > 0 else 0.0,
    }
    
    # Add type-specific statistics
    if pd.api.types.is_numeric_dtype(col_data):
        non_null = col_data.dropna()
        if len(non_null) > 0:
            stats['min'] = float(non_null.min())
            stats['max'] = float(non_null.max())
            stats['mean'] = float(non_null.mean())
            stats['median'] = float(non_null.median())
            stats['std'] = float(non_null.std()) if len(non_null) > 1 else 0.0
    elif pd.api.types.is_string_dtype(col_data) or pd.api.types.is_object_dtype(col_data):
        non_null = col_data.dropna()
        if len(non_null) > 0:
            stats['avg_length'] = float(non_null.astype(str).str.len().mean())
            stats['max_length'] = int(non_null.astype(str).str.len().max())
            # Get sample values (up to 5 most common)
            value_counts = non_null.value_counts().head(5)
            stats['sample_values'] = [str(v) for v in value_counts.index.tolist()]
    
    return stats


def inspect_csv(file_path: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Inspect a CSV file and extract metadata.
    
    Args:
        file_path: Path to the CSV file
        options: Optional dict with delimiter, encoding, header, sample_size
        
    Returns:
        Dictionary with file metadata, schema, and statistics
    """
    options = options or {}
    
    # Auto-detect or use provided options
    encoding = options.get('encoding') or detect_encoding(file_path)
    delimiter = options.get('delimiter') or detect_csv_delimiter(file_path, encoding)
    header = options.get('header', True)
    sample_size = options.get('sample_size', SAMPLE_SIZE)
    
    # Read the file
    if header:
        df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter)
    else:
        df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter, header=None)
    
    # Generate metadata
    metadata = {
        'format': 'csv',
        'row_count': len(df),
        'column_count': len(df.columns),
        'detected_options': {
            'encoding': encoding,
            'delimiter': delimiter,
            'header': header,
        },
        'columns': [],
        'preview': df.head(PREVIEW_ROWS).to_dict(orient='records'),
    }
    
    # Infer statistics for each column
    for column in df.columns:
        col_stats = infer_column_statistics(df, column, sample_size)
        metadata['columns'].append(col_stats)
    
    return metadata


def inspect_parquet(file_path: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Inspect a Parquet file and extract metadata.
    
    Args:
        file_path: Path to the Parquet file
        options: Optional dict with sample_size
        
    Returns:
        Dictionary with file metadata, schema, and statistics
    """
    options = options or {}
    sample_size = options.get('sample_size', SAMPLE_SIZE)
    
    # Read the file
    df = pd.read_parquet(file_path)
    
    # Generate metadata
    metadata = {
        'format': 'parquet',
        'row_count': len(df),
        'column_count': len(df.columns),
        'detected_options': {},
        'columns': [],
        'preview': df.head(PREVIEW_ROWS).to_dict(orient='records'),
    }
    
    # Infer statistics for each column
    for column in df.columns:
        col_stats = infer_column_statistics(df, column, sample_size)
        metadata['columns'].append(col_stats)
    
    return metadata


def inspect_json(file_path: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Inspect a JSON file and extract metadata.
    
    Args:
        file_path: Path to the JSON file
        options: Optional dict with sample_size
        
    Returns:
        Dictionary with file metadata, schema, and statistics
    """
    options = options or {}
    sample_size = options.get('sample_size', SAMPLE_SIZE)
    
    # Try to read as JSON lines first, then as regular JSON
    try:
        df = pd.read_json(file_path, lines=True)
        json_type = 'jsonl'
    except ValueError:
        df = pd.read_json(file_path)
        json_type = 'json'
    
    # Generate metadata
    metadata = {
        'format': 'json',
        'row_count': len(df),
        'column_count': len(df.columns),
        'detected_options': {
            'json_type': json_type,
        },
        'columns': [],
        'preview': df.head(PREVIEW_ROWS).to_dict(orient='records'),
    }
    
    # Infer statistics for each column
    for column in df.columns:
        col_stats = infer_column_statistics(df, column, sample_size)
        metadata['columns'].append(col_stats)
    
    return metadata


def inspect_dataset(file_path: str, file_format: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Inspect a dataset file and extract metadata.
    
    Args:
        file_path: Path to the dataset file
        file_format: Format of the file ('csv', 'parquet', 'json')
        options: Optional dict with format-specific options
        
    Returns:
        Dictionary with file metadata, schema, and statistics
        
    Raises:
        ValueError: If format is not supported
    """
    file_format = file_format.lower()
    
    if file_format == 'csv':
        return inspect_csv(file_path, options)
    elif file_format == 'parquet':
        return inspect_parquet(file_path, options)
    elif file_format == 'json':
        return inspect_json(file_path, options)
    else:
        raise ValueError(f"Unsupported file format: {file_format}")


def map_pandas_type_to_spark(pandas_type: str) -> str:
    """Map pandas dtype to PySpark type.
    
    Args:
        pandas_type: Pandas dtype string
        
    Returns:
        PySpark type string
    """
    type_mapping = {
        'int64': 'long',
        'int32': 'integer',
        'float64': 'double',
        'float32': 'float',
        'object': 'string',
        'string': 'string',
        'bool': 'boolean',
        'datetime64[ns]': 'timestamp',
    }
    
    return type_mapping.get(pandas_type, 'string')
