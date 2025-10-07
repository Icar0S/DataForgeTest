"""Data processing logic for GOLD Dataset Testing."""

import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np


def strip_accents(text: str) -> str:
    """Remove accents from text."""
    if not isinstance(text, str):
        return text
    nfd = unicodedata.normalize("NFD", text)
    return "".join(char for char in nfd if unicodedata.category(char) != "Mn")


def normalize_column_name(name: str, existing_names: List[str] = None) -> str:
    """Convert column name to normalized format.
    
    Args:
        name: Original column name
        existing_names: List of already normalized names to avoid duplicates
        
    Returns:
        Normalized column name with deduplication
    """
    # Trim
    name = name.strip()
    # Strip accents
    name = strip_accents(name)
    # Replace spaces with underscores
    name = re.sub(r"\s+", "_", name)
    # Convert to lowercase
    name = name.lower()
    # Remove special characters except underscores
    name = re.sub(r"[^\w]", "", name)
    
    # Handle duplicates
    if existing_names is not None and name in existing_names:
        counter = 2
        base_name = name
        while name in existing_names:
            name = f"{base_name}_{counter}"
            counter += 1
    
    return name


def trim_string(value: Any) -> Any:
    """Trim strings and remove invisible characters."""
    if pd.isna(value):
        return value
    if isinstance(value, str):
        # Remove invisible characters (control characters, zero-width spaces, etc.)
        value = re.sub(r'[\x00-\x1f\x7f-\x9f\u200b-\u200f\ufeff]', '', value)
        # Trim whitespace
        value = value.strip()
        return value if value else np.nan
    return value


def coerce_numeric(value: Any) -> Any:
    """Coerce value to numeric, handling various formats."""
    if pd.isna(value):
        return value
    
    if isinstance(value, (int, float)):
        return value
    
    if not isinstance(value, str):
        return value
    
    text = str(value).strip()
    
    # Remove thousands separators and handle comma/period
    # Handle both European (1.234,56) and US (1,234.56) formats
    if "," in text and "." in text:
        # Both present - determine which is decimal separator
        last_comma = text.rfind(",")
        last_period = text.rfind(".")
        if last_comma > last_period:
            # European format: 1.234,56
            text = text.replace(".", "").replace(",", ".")
        else:
            # US format: 1,234.56
            text = text.replace(",", "")
    elif "," in text:
        # Only comma - could be thousands or decimal
        parts = text.split(",")
        if len(parts) == 2 and len(parts[1]) <= 3:
            # Likely decimal: 1,50
            text = text.replace(",", ".")
        else:
            # Likely thousands: 1,234 or 1,234,567
            text = text.replace(",", "")
    
    try:
        return pd.to_numeric(text)
    except (ValueError, TypeError):
        return value


def parse_date(value: Any) -> Any:
    """Parse dates with best-effort, non-fatal approach."""
    if pd.isna(value):
        return value
    
    if isinstance(value, (pd.Timestamp, datetime)):
        return value
    
    if not isinstance(value, str):
        return value
    
    text = str(value).strip()
    
    # Try to parse as datetime
    try:
        return pd.to_datetime(text, format='ISO8601', errors='coerce')
    except Exception:
        # If it fails, try with infer_datetime_format
        try:
            result = pd.to_datetime(text, infer_datetime_format=True, errors='coerce')
            if pd.notna(result):
                return result
        except Exception:
            pass
    
    # If all parsing fails, return original value
    return value


def detect_encoding(file_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """Detect encoding and separator for CSV files.
    
    Returns:
        Tuple of (encoding, separator)
    """
    try:
        import chardet
        
        with open(file_path, "rb") as f:
            raw_data = f.read(100000)  # Read first 100KB
            encoding_result = chardet.detect(raw_data)
            encoding = encoding_result.get("encoding")
            confidence = encoding_result.get("confidence", 0)
            
            if confidence > 0.7 and encoding:
                # Detect separator by trying to read with detected encoding
                for sep in [",", ";", "\t", "|"]:
                    try:
                        df_sample = pd.read_csv(
                            file_path, encoding=encoding, sep=sep, nrows=5
                        )
                        if len(df_sample.columns) > 1:
                            return encoding, sep
                    except Exception:
                        continue
                
                return encoding, ","
    except Exception:
        pass
    
    # Fallback detection
    for encoding in ["utf-8", "utf-8-sig", "latin1", "cp1252"]:
        for sep in [",", ";", "\t"]:
            try:
                df_sample = pd.read_csv(file_path, encoding=encoding, sep=sep, nrows=5)
                if len(df_sample.columns) > 1:
                    return encoding, sep
            except Exception:
                continue
    
    return "utf-8", ","


def read_dataset(file_path: Path, **kwargs) -> pd.DataFrame:
    """Read dataset from file with auto-detection."""
    suffix = file_path.suffix.lower()
    
    if suffix == ".csv":
        encoding = kwargs.get("encoding")
        sep = kwargs.get("sep")
        
        if not encoding or not sep:
            encoding, sep = detect_encoding(file_path)
        
        return pd.read_csv(file_path, encoding=encoding, sep=sep, **{k: v for k, v in kwargs.items() if k not in ['encoding', 'sep']})
    
    elif suffix in [".xlsx", ".xls"]:
        return pd.read_excel(file_path, **kwargs)
    
    elif suffix == ".parquet":
        return pd.read_parquet(file_path, **kwargs)
    
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def clean_dataframe_chunk(
    df_chunk: pd.DataFrame,
    options: Dict[str, Any],
    column_mapping: Dict[str, str] = None,
    is_first_chunk: bool = True,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean a chunk of dataframe according to options.
    
    Args:
        df_chunk: DataFrame chunk to clean
        options: Cleaning options
        column_mapping: Mapping of original to normalized column names
        is_first_chunk: Whether this is the first chunk
        
    Returns:
        Tuple of (cleaned_df, metrics)
    """
    metrics = {
        "trimStrings": 0,
        "coerceNumeric": 0,
        "parseDates": 0,
    }
    
    df = df_chunk.copy()
    
    # Apply column mapping if provided (for subsequent chunks)
    if column_mapping and not is_first_chunk:
        df.columns = [column_mapping.get(col, col) for col in df.columns]
    
    # Trim strings
    if options.get("trimStrings", True):
        for col in df.select_dtypes(include=['object']).columns:
            original = df[col].copy()
            df[col] = df[col].apply(trim_string)
            changed = (original != df[col]).sum()
            metrics["trimStrings"] += changed
    
    # Coerce numeric
    if options.get("coerceNumeric", True):
        for col in df.select_dtypes(include=['object']).columns:
            original = df[col].copy()
            df[col] = df[col].apply(coerce_numeric)
            # Count successful conversions to numeric
            changed = sum(pd.to_numeric(df[col], errors='coerce').notna() & original.notna() & ~pd.to_numeric(original, errors='coerce').notna())
            metrics["coerceNumeric"] += changed
    
    # Parse dates
    if options.get("parseDates", True):
        for col in df.select_dtypes(include=['object']).columns:
            # Check if column might contain dates
            sample = df[col].dropna().head(10)
            if len(sample) > 0:
                parsed_sample = sample.apply(parse_date)
                # If more than 50% parse successfully, apply to whole column
                success_rate = (pd.to_datetime(parsed_sample, errors='coerce').notna()).sum() / len(sample)
                if success_rate > 0.5:
                    original = df[col].copy()
                    df[col] = df[col].apply(parse_date)
                    changed = sum((df[col] != original) & df[col].notna())
                    metrics["parseDates"] += changed
    
    return df, metrics


def get_null_counts(df: pd.DataFrame) -> Dict[str, int]:
    """Get null counts per column."""
    return df.isnull().sum().to_dict()
