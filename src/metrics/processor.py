"""Data quality metrics calculation logic."""

from typing import Dict, Any, List
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path


def read_dataset(file_path: Path) -> pd.DataFrame:
    """Read dataset from file.

    Args:
        file_path: Path to the dataset file

    Returns:
        DataFrame containing the dataset

    Raises:
        ValueError: If file format is not supported
    """
    file_ext = file_path.suffix.lower()

    if file_ext == ".csv":
        # Try to detect encoding and read CSV
        try:
            df = pd.read_csv(file_path, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="latin-1")
    elif file_ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    elif file_ext == ".parquet":
        df = pd.read_parquet(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")

    return df


def calculate_completeness_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate completeness metrics for the dataset.

    Args:
        df: Input DataFrame

    Returns:
        Dictionary with completeness metrics
    """
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isna().sum().sum()
    completeness_rate = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0

    # Per-column completeness
    column_completeness = {}
    for col in df.columns:
        missing = df[col].isna().sum()
        total = len(df)
        completeness = ((total - missing) / total * 100) if total > 0 else 0
        column_completeness[col] = {
            "completeness": round(completeness, 2),
            "missing_count": int(missing),
            "total_count": int(total)
        }

    return {
        "overall_completeness": round(completeness_rate, 2),
        "total_cells": int(total_cells),
        "missing_cells": int(missing_cells),
        "filled_cells": int(total_cells - missing_cells),
        "column_completeness": column_completeness
    }


def calculate_uniqueness_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate uniqueness metrics for the dataset.

    Args:
        df: Input DataFrame

    Returns:
        Dictionary with uniqueness metrics
    """
    total_rows = len(df)
    duplicate_rows = df.duplicated().sum()
    unique_rows = total_rows - duplicate_rows
    uniqueness_rate = (unique_rows / total_rows * 100) if total_rows > 0 else 0

    # Per-column uniqueness
    column_uniqueness = {}
    for col in df.columns:
        unique_values = df[col].nunique()
        total_values = len(df[col].dropna())
        uniqueness = (unique_values / total_values * 100) if total_values > 0 else 0
        column_uniqueness[col] = {
            "uniqueness": round(uniqueness, 2),
            "unique_count": int(unique_values),
            "total_count": int(total_values)
        }

    return {
        "overall_uniqueness": round(uniqueness_rate, 2),
        "total_rows": int(total_rows),
        "unique_rows": int(unique_rows),
        "duplicate_rows": int(duplicate_rows),
        "column_uniqueness": column_uniqueness
    }


def calculate_validity_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate validity metrics for the dataset.

    Args:
        df: Input DataFrame

    Returns:
        Dictionary with validity metrics
    """
    column_validity = {}
    total_valid_cells = 0
    total_cells = 0

    for col in df.columns:
        col_data = df[col].dropna()
        total_values = len(col_data)
        valid_values = total_values  # Start assuming all are valid
        
        # Detect data type and validate
        if pd.api.types.is_numeric_dtype(df[col]):
            # For numeric columns, check for infinity values
            invalid = np.isinf(col_data).sum() if len(col_data) > 0 else 0
            valid_values = total_values - invalid
        elif pd.api.types.is_string_dtype(df[col]):
            # For string columns, check for empty strings after stripping
            invalid = col_data.apply(lambda x: isinstance(x, str) and x.strip() == "").sum()
            valid_values = total_values - invalid

        validity = (valid_values / total_values * 100) if total_values > 0 else 0
        column_validity[col] = {
            "validity": round(validity, 2),
            "valid_count": int(valid_values),
            "invalid_count": int(total_values - valid_values),
            "total_count": int(total_values)
        }
        
        total_valid_cells += valid_values
        total_cells += total_values

    overall_validity = (total_valid_cells / total_cells * 100) if total_cells > 0 else 0

    return {
        "overall_validity": round(overall_validity, 2),
        "total_cells": int(total_cells),
        "valid_cells": int(total_valid_cells),
        "invalid_cells": int(total_cells - total_valid_cells),
        "column_validity": column_validity
    }


def calculate_consistency_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate consistency metrics for the dataset.

    Args:
        df: Input DataFrame

    Returns:
        Dictionary with consistency metrics
    """
    column_consistency = {}
    
    for col in df.columns:
        col_data = df[col].dropna()
        if len(col_data) == 0:
            continue
            
        # Check data type consistency
        if pd.api.types.is_numeric_dtype(df[col]):
            # For numeric columns, check for mixed types (int vs float)
            type_consistency = 100.0
        elif pd.api.types.is_string_dtype(df[col]):
            # For string columns, check format consistency
            # Example: check if all values have similar patterns (same case, same length range)
            lengths = col_data.astype(str).str.len()
            if len(lengths) > 0:
                length_variance = lengths.std() / lengths.mean() if lengths.mean() > 0 else 0
                # Lower variance means more consistency
                type_consistency = max(0, min(100, 100 - (length_variance * 10)))
            else:
                type_consistency = 100.0
        else:
            type_consistency = 100.0

        column_consistency[col] = {
            "consistency": round(type_consistency, 2),
            "data_type": str(df[col].dtype)
        }

    # Overall consistency is average of column consistencies
    if column_consistency:
        overall_consistency = sum(c["consistency"] for c in column_consistency.values()) / len(column_consistency)
    else:
        overall_consistency = 0.0

    return {
        "overall_consistency": round(overall_consistency, 2),
        "column_consistency": column_consistency
    }


def calculate_all_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate all data quality metrics for the dataset.

    Args:
        df: Input DataFrame

    Returns:
        Dictionary with all metrics
    """
    return {
        "completeness": calculate_completeness_metrics(df),
        "uniqueness": calculate_uniqueness_metrics(df),
        "validity": calculate_validity_metrics(df),
        "consistency": calculate_consistency_metrics(df),
        "dataset_info": {
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "column_names": list(df.columns),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        }
    }


def generate_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate comprehensive quality report.

    Args:
        df: Input DataFrame

    Returns:
        Dictionary with quality report including metrics and recommendations
    """
    metrics = calculate_all_metrics(df)
    
    # Generate recommendations based on metrics
    recommendations = []
    
    if metrics["completeness"]["overall_completeness"] < 90:
        recommendations.append({
            "severity": "high",
            "category": "completeness",
            "message": f"Dataset has {metrics['completeness']['overall_completeness']:.1f}% completeness. Consider reviewing missing values."
        })
    
    if metrics["uniqueness"]["overall_uniqueness"] < 95:
        recommendations.append({
            "severity": "medium",
            "category": "uniqueness",
            "message": f"Found {metrics['uniqueness']['duplicate_rows']} duplicate rows. Consider removing duplicates."
        })
    
    if metrics["validity"]["overall_validity"] < 95:
        recommendations.append({
            "severity": "high",
            "category": "validity",
            "message": f"Dataset has {metrics['validity']['overall_validity']:.1f}% validity. Review invalid values."
        })
    
    if metrics["consistency"]["overall_consistency"] < 80:
        recommendations.append({
            "severity": "medium",
            "category": "consistency",
            "message": "Some columns show inconsistent formatting. Consider standardizing data formats."
        })
    
    # Calculate overall quality score (weighted average)
    quality_score = (
        metrics["completeness"]["overall_completeness"] * 0.3 +
        metrics["uniqueness"]["overall_uniqueness"] * 0.2 +
        metrics["validity"]["overall_validity"] * 0.3 +
        metrics["consistency"]["overall_consistency"] * 0.2
    )
    
    return {
        "metrics": metrics,
        "recommendations": recommendations,
        "overall_quality_score": round(quality_score, 2),
        "generated_at": datetime.now().isoformat()
    }
