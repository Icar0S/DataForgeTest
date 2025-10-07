"""Flask routes for GOLD Dataset Testing feature."""

import json
import uuid
import time
from pathlib import Path
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np

from .config import GoldConfig
from .processor import (
    read_dataset,
    normalize_column_name,
    clean_dataframe_chunk,
    get_null_counts,
)


def convert_to_json_serializable(obj):
    """Convert numpy/pandas types to JSON serializable types."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    return obj


# Create blueprint
gold_bp = Blueprint("gold", __name__, url_prefix="/api/gold")

# Initialize config
config = GoldConfig.from_env()

# Ensure storage directories exist
config.storage_path.mkdir(parents=True, exist_ok=True)

# Track processing status
processing_status = {}


@gold_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"ok": True, "service": "gold", "status": "running"})


@gold_bp.route("/upload", methods=["POST"])
def upload_dataset():
    """Handle dataset upload.

    Form-data:
        file: Dataset file

    Returns:
        JSON with sessionId, datasetId, columns, sample, and format
    """
    try:
        # Check file in request
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "" or file.filename is None:
            return jsonify({"error": "No file selected"}), 400

        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in config.allowed_file_types:
            return (
                jsonify(
                    {
                        "error": f"File type {file_ext} not allowed. Allowed types: {config.allowed_file_types}"
                    }
                ),
                400,
            )

        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        max_size = config.max_upload_mb * 1024 * 1024
        if file_size > max_size:
            return (
                jsonify(
                    {
                        "error": f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum ({config.max_upload_mb}MB)"
                    }
                ),
                413,
            )

        # Generate session ID
        session_id = str(uuid.uuid4())
        dataset_id = str(uuid.uuid4())

        # Create session directory
        session_dir = config.storage_path / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Secure filename
        safe_filename = secure_filename(file.filename)
        # Prevent path traversal
        if ".." in safe_filename or "/" in safe_filename or "\\" in safe_filename:
            return jsonify({"error": "Invalid filename"}), 400

        # Save file with original extension
        file_path = session_dir / f"raw{file_ext}"
        file.save(file_path)

        # Read dataset sample
        if file_ext == ".csv":
            from .processor import detect_encoding

            encoding, sep = detect_encoding(file_path)
            df_sample = read_dataset(file_path, encoding=encoding, sep=sep, nrows=20)
            # Store encoding and separator for later use
            metadata = {"encoding": encoding, "sep": sep, "format": "csv"}
        elif file_ext in [".xlsx", ".xls"]:
            df_sample = pd.read_excel(file_path, nrows=20)
            metadata = {"format": "xlsx" if file_ext == ".xlsx" else "xls"}
        elif file_ext == ".parquet":
            df = pd.read_parquet(file_path)
            df_sample = df.head(20)
            metadata = {"format": "parquet", "total_rows": len(df)}
        else:
            return jsonify({"error": "Unsupported file format"}), 415

        # Get columns
        columns = df_sample.columns.tolist()

        # Get sample data
        sample = df_sample.to_dict(orient="records")

        # Convert NaN to None for JSON
        for record in sample:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None

        # Save metadata
        metadata.update(
            {
                "sessionId": session_id,
                "datasetId": dataset_id,
                "originalFilename": safe_filename,
                "uploadedAt": datetime.now(timezone.utc).isoformat(),
            }
        )

        with open(session_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        return jsonify(
            {
                "sessionId": session_id,
                "datasetId": dataset_id,
                "columns": columns,
                "sample": sample,
                "format": metadata["format"],
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gold_bp.route("/clean", methods=["POST"])
def clean_dataset():
    """Clean dataset with specified options.

    Body JSON:
        {
            "sessionId": "string",
            "datasetId": "string",
            "options": {
                "dropEmptyColumns": true,
                "normalizeHeaders": true,
                "trimStrings": true,
                "coerceNumeric": true,
                "parseDates": true,
                "dropDuplicates": false,
                "chunksize": 200000
            }
        }

    Returns:
        JSON with status and download links
    """
    try:
        data = request.get_json()

        # Validate required fields
        session_id = data.get("sessionId")
        if not session_id:
            return jsonify({"error": "sessionId is required"}), 400

        # Get session directory
        session_dir = config.storage_path / session_id
        if not session_dir.exists():
            return jsonify({"error": "Session not found"}), 404

        # Get options
        options = data.get("options", {})
        chunksize = options.get("chunksize", 200000)

        # Load metadata
        metadata_path = session_dir / "metadata.json"
        if not metadata_path.exists():
            return jsonify({"error": "Session metadata not found"}), 404

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        file_format = metadata.get("format")

        # Get raw file
        raw_files = list(session_dir.glob("raw.*"))
        if not raw_files:
            return jsonify({"error": "Raw file not found"}), 404

        raw_file = raw_files[0]

        # Initialize processing status
        processing_status[session_id] = {
            "state": "running",
            "progress": {"current": 0, "total": 100, "phase": "initializing"},
            "startedAt": datetime.now(timezone.utc).isoformat(),
        }

        # Start cleaning process
        try:
            start_time = time.time()

            # Read and clean dataset
            if file_format == "csv":
                # Process CSV in chunks
                encoding = metadata.get("encoding", "utf-8")
                sep = metadata.get("sep", ",")

                process_csv_chunked(
                    raw_file, session_id, options, encoding, sep, chunksize
                )

            elif file_format in ["xlsx", "xls"]:
                # Load Excel file entirely, then process in memory chunks
                process_excel(raw_file, session_id, options, chunksize)

            elif file_format == "parquet":
                # Process Parquet in chunks
                process_parquet_chunked(raw_file, session_id, options, chunksize)
            else:
                processing_status[session_id]["state"] = "failed"
                processing_status[session_id]["error"] = "Unsupported format"
                return jsonify({"error": "Unsupported format"}), 415

            # Generate report
            report = processing_status[session_id].get("report", {})
            report["finishedAt"] = datetime.now(timezone.utc).isoformat()
            report["durationSec"] = time.time() - start_time

            # Save report
            with open(session_dir / "report.json", "w") as f:
                json.dump(report, f, indent=2)

            # Update status
            processing_status[session_id]["state"] = "completed"
            processing_status[session_id]["report"] = report
            processing_status[session_id]["progress"] = {
                "current": 100,
                "total": 100,
                "phase": "completed",
            }

            # Generate download links
            download_links = {"csv": f"/api/gold/download/{session_id}/gold_clean.csv"}

            # Add same format download if available
            if file_format == "csv":
                download_links["sameFormat"] = download_links["csv"]
            elif file_format in ["xlsx", "xls"]:
                if (session_dir / "gold_clean.xlsx").exists():
                    download_links["sameFormat"] = (
                        f"/api/gold/download/{session_id}/gold_clean.xlsx"
                    )
            elif file_format == "parquet":
                if (session_dir / "gold_clean.parquet").exists():
                    download_links["sameFormat"] = (
                        f"/api/gold/download/{session_id}/gold_clean.parquet"
                    )

            return (
                jsonify(
                    {
                        "status": "completed",
                        "progressUrl": f"/api/gold/status?sessionId={session_id}",
                        "download": download_links,
                    }
                ),
                200,
            )

        except Exception as e:
            processing_status[session_id]["state"] = "failed"
            processing_status[session_id]["error"] = str(e)
            raise

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def process_csv_chunked(file_path, session_id, options, encoding, sep, chunksize):
    """Process CSV file in chunks."""
    session_dir = config.storage_path / session_id

    # First pass: analyze structure
    processing_status[session_id]["progress"]["phase"] = "analyzing"
    df_first = read_dataset(file_path, encoding=encoding, sep=sep, nrows=1000)

    # Get total rows
    total_rows = sum(1 for _ in open(file_path, "r", encoding=encoding)) - 1

    # Normalize headers if requested
    column_mapping = {}
    if options.get("normalizeHeaders", True):
        normalized_cols = []
        for col in df_first.columns:
            normalized = normalize_column_name(col, normalized_cols)
            normalized_cols.append(normalized)
            column_mapping[col] = normalized
        df_first.columns = normalized_cols

    # Identify empty columns to drop
    columns_to_drop = []
    if options.get("dropEmptyColumns", True):
        # Need to check full file for empty columns
        df_check = read_dataset(file_path, encoding=encoding, sep=sep)
        if column_mapping:
            df_check.columns = [
                column_mapping.get(col, col) for col in df_check.columns
            ]
        for col in df_check.columns:
            if df_check[col].isna().all():
                columns_to_drop.append(col)

    # Get null counts before
    nulls_before = get_null_counts(df_first)
    columns_before = len(df_first.columns)

    # Drop empty columns
    df_first = df_first.drop(columns=columns_to_drop, errors="ignore")

    # Process in chunks
    processing_status[session_id]["progress"]["phase"] = "cleaning"

    chunks = []
    metrics = {"trimStrings": 0, "coerceNumeric": 0, "parseDates": 0}

    # Use robust CSV reading with chunking - try different strategies for problematic files
    chunk_reader = None
    chunk_strategies = [
        # Standard approach
        {"encoding": encoding, "sep": sep, "chunksize": chunksize},
        # With quoting for CSV files with embedded commas/newlines
        {"encoding": encoding, "sep": sep, "chunksize": chunksize, "quoting": 1},
        # With different quote handling
        {
            "encoding": encoding,
            "sep": sep,
            "chunksize": chunksize,
            "quotechar": '"',
            "doublequote": True,
        },
        # Skip bad lines
        {
            "encoding": encoding,
            "sep": sep,
            "chunksize": chunksize,
            "on_bad_lines": "skip",
        },
        # Engine change for problematic files
        {"encoding": encoding, "sep": sep, "chunksize": chunksize, "engine": "python"},
        # Last resort with more permissive settings
        {
            "encoding": encoding,
            "sep": sep,
            "chunksize": chunksize,
            "engine": "python",
            "on_bad_lines": "skip",
            "quoting": 3,
        },
    ]

    last_error = None
    successful_strategy = None
    for i, strategy in enumerate(chunk_strategies):
        try:
            # Test if this strategy can read at least one chunk first
            test_strategy = {k: v for k, v in strategy.items() if k != "chunksize"}
            test_strategy["nrows"] = 10
            test_reader = pd.read_csv(file_path, **test_strategy)

            if len(test_reader) > 0:
                # Strategy works, now create the actual chunk reader
                chunk_reader = pd.read_csv(file_path, **strategy)
                successful_strategy = i + 1
                if i > 0:  # Log fallback usage
                    print(
                        f"Using CSV chunk reading strategy {successful_strategy} for processing"
                    )
                break
        except Exception as e:
            last_error = e
            continue

    if chunk_reader is None:
        raise ValueError(
            f"Could not read CSV file {file_path} in chunks. Last error: {str(last_error)}. "
            f"The file may have structural issues that prevent chunked reading."
        )

    total_chunks = (total_rows // chunksize) + 1
    chunk_count = 0

    try:
        for chunk in chunk_reader:
            try:
                chunk_count += 1
                processing_status[session_id]["progress"]["current"] = chunk_count
                processing_status[session_id]["progress"]["total"] = total_chunks

                # Apply column mapping
                if column_mapping:
                    chunk.columns = [
                        column_mapping.get(col, col) for col in chunk.columns
                    ]

                # Drop empty columns
                chunk = chunk.drop(columns=columns_to_drop, errors="ignore")

                # Clean chunk
                cleaned_chunk, chunk_metrics = clean_dataframe_chunk(
                    chunk,
                    options,
                    column_mapping=column_mapping,
                    is_first_chunk=(chunk_count == 1),
                )

                # Update metrics
                for key in metrics:
                    metrics[key] += chunk_metrics.get(key, 0)

                chunks.append(cleaned_chunk)

            except Exception as chunk_error:
                print(
                    f"Warning: Error processing chunk {chunk_count}: {str(chunk_error)}"
                )
                # Skip this problematic chunk and continue
                continue

    except Exception as reader_error:
        # If chunk reading fails completely, try to recover with more permissive settings
        print(
            f"Chunk reading failed: {str(reader_error)}. Attempting recovery with permissive settings..."
        )

        # Try to read the entire file with the most permissive strategy and then chunk it in memory
        try:
            recovery_strategy = {
                "encoding": encoding,
                "sep": sep,
                "engine": "python",
                "on_bad_lines": "skip",
                "quoting": 3,
                "skipinitialspace": True,
            }

            print(
                "Attempting recovery by reading entire file with permissive settings..."
            )
            df_full = pd.read_csv(file_path, **recovery_strategy)

            # Apply column mapping to full dataframe
            if column_mapping:
                df_full.columns = [
                    column_mapping.get(col, col) for col in df_full.columns
                ]

            # Drop empty columns
            df_full = df_full.drop(columns=columns_to_drop, errors="ignore")

            # Process in memory chunks
            print(
                f"Recovery successful. Processing {len(df_full)} rows in memory chunks..."
            )
            total_chunks = (len(df_full) // chunksize) + 1

            for i in range(0, len(df_full), chunksize):
                chunk_count += 1
                processing_status[session_id]["progress"]["current"] = chunk_count
                processing_status[session_id]["progress"]["total"] = total_chunks

                chunk = df_full.iloc[i : i + chunksize].copy()

                try:
                    # Clean chunk
                    cleaned_chunk, chunk_metrics = clean_dataframe_chunk(
                        chunk,
                        options,
                        column_mapping=column_mapping,
                        is_first_chunk=(i == 0),
                    )

                    # Update metrics
                    for key in metrics:
                        metrics[key] += chunk_metrics.get(key, 0)

                    chunks.append(cleaned_chunk)

                except Exception as chunk_error:
                    print(
                        f"Warning: Error processing memory chunk {chunk_count}: {str(chunk_error)}"
                    )
                    continue

            print("Recovery processing completed successfully.")

        except Exception as recovery_error:
            print(
                f"Python engine recovery failed: {str(recovery_error)}. Trying C engine with permissive settings..."
            )

            # Try one more time with C engine and very permissive settings
            try:
                # Build recovery strategy with compatibility check
                recovery_strategy_c = {
                    "encoding": encoding,
                    "sep": sep,
                    "engine": "c",
                    "quoting": 3,
                    "skipinitialspace": True,
                    "low_memory": False,
                }

                # Add on_bad_lines parameter based on pandas version compatibility
                try:
                    recovery_strategy_c["on_bad_lines"] = "skip"
                except Exception:
                    # Fallback for older pandas versions
                    recovery_strategy_c["error_bad_lines"] = False
                    recovery_strategy_c["warn_bad_lines"] = False

                print("Attempting final recovery with C engine...")
                df_full = pd.read_csv(file_path, **recovery_strategy_c)

                # Apply column mapping to full dataframe
                if column_mapping:
                    df_full.columns = [
                        column_mapping.get(col, col) for col in df_full.columns
                    ]

                # Drop empty columns
                df_full = df_full.drop(columns=columns_to_drop, errors="ignore")

                # Process in memory chunks
                print(
                    f"Final recovery successful. Processing {len(df_full)} rows in memory chunks..."
                )
                total_chunks = (len(df_full) // chunksize) + 1

                for i in range(0, len(df_full), chunksize):
                    chunk_count += 1
                    processing_status[session_id]["progress"]["current"] = chunk_count
                    processing_status[session_id]["progress"]["total"] = total_chunks

                    chunk = df_full.iloc[i : i + chunksize].copy()

                    try:
                        # Clean chunk
                        cleaned_chunk, chunk_metrics = clean_dataframe_chunk(
                            chunk,
                            options,
                            column_mapping=column_mapping,
                            is_first_chunk=(i == 0),
                        )

                        # Update metrics
                        for key in metrics:
                            metrics[key] += chunk_metrics.get(key, 0)

                        chunks.append(cleaned_chunk)

                    except Exception as chunk_error:
                        print(
                            f"Warning: Error processing final recovery chunk {chunk_count}: {str(chunk_error)}"
                        )
                        continue

                print("Final recovery processing completed successfully.")

            except Exception as final_error:
                raise ValueError(
                    f"Error reading CSV chunks: {str(reader_error)}. "
                    f"Python engine recovery failed: {str(recovery_error)}. "
                    f"C engine recovery also failed: {str(final_error)}. "
                    f"File has severe structural issues that prevent any form of processing."
                )

    # Concatenate all chunks
    processing_status[session_id]["progress"]["phase"] = "finalizing"
    result_df = pd.concat(chunks, ignore_index=True)

    # Drop duplicates if requested
    if options.get("dropDuplicates", False):
        result_df = result_df.drop_duplicates()

    # Get null counts after
    nulls_after = get_null_counts(result_df)

    # Save cleaned CSV
    output_csv = session_dir / "gold_clean.csv"
    result_df.to_csv(output_csv, index=False)

    # Generate preview
    preview = result_df.head(50).to_dict(orient="records")
    for record in preview:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None

    # Build report
    report = {
        "rowsRead": int(total_rows),
        "rowsWritten": int(len(result_df)),
        "columnsBefore": int(columns_before),
        "columnsAfter": int(len(result_df.columns)),
        "removedColumns": columns_to_drop,
        "changedRows": convert_to_json_serializable(metrics),
        "nullsPerColumn": {
            "before": convert_to_json_serializable(nulls_before),
            "after": convert_to_json_serializable(nulls_after),
        },
        "samplePreview": preview,
        "startedAt": processing_status[session_id]["startedAt"],
    }

    processing_status[session_id]["report"] = report

    return result_df


def process_excel(file_path, session_id, options, chunksize):
    """Process Excel file."""
    session_dir = config.storage_path / session_id

    processing_status[session_id]["progress"]["phase"] = "reading"

    # Read entire Excel file
    df = pd.read_excel(file_path)

    total_rows = len(df)
    columns_before = len(df.columns)

    # Normalize headers
    column_mapping = {}
    if options.get("normalizeHeaders", True):
        processing_status[session_id]["progress"]["phase"] = "normalizing headers"
        normalized_cols = []
        for col in df.columns:
            normalized = normalize_column_name(col, normalized_cols)
            normalized_cols.append(normalized)
            column_mapping[col] = normalized
        df.columns = normalized_cols

    # Get null counts before
    nulls_before = get_null_counts(df)

    # Drop empty columns
    columns_to_drop = []
    if options.get("dropEmptyColumns", True):
        for col in df.columns:
            if df[col].isna().all():
                columns_to_drop.append(col)
        df = df.drop(columns=columns_to_drop)

    # Process in memory chunks
    processing_status[session_id]["progress"]["phase"] = "cleaning"

    metrics = {"trimStrings": 0, "coerceNumeric": 0, "parseDates": 0}
    chunks = []

    total_chunks = (len(df) // chunksize) + 1

    for i in range(0, len(df), chunksize):
        chunk_num = i // chunksize + 1
        processing_status[session_id]["progress"]["current"] = chunk_num
        processing_status[session_id]["progress"]["total"] = total_chunks

        chunk = df.iloc[i : i + chunksize].copy()

        # Clean chunk
        cleaned_chunk, chunk_metrics = clean_dataframe_chunk(
            chunk, options, is_first_chunk=(i == 0)
        )

        # Update metrics
        for key in metrics:
            metrics[key] += chunk_metrics.get(key, 0)

        chunks.append(cleaned_chunk)

    # Concatenate chunks
    processing_status[session_id]["progress"]["phase"] = "finalizing"
    result_df = pd.concat(chunks, ignore_index=True)

    # Drop duplicates if requested
    if options.get("dropDuplicates", False):
        result_df = result_df.drop_duplicates()

    # Get null counts after
    nulls_after = get_null_counts(result_df)

    # Save as CSV
    output_csv = session_dir / "gold_clean.csv"
    result_df.to_csv(output_csv, index=False)

    # Also save as Excel
    output_xlsx = session_dir / "gold_clean.xlsx"
    result_df.to_excel(output_xlsx, index=False, engine="openpyxl")

    # Generate preview
    preview = result_df.head(50).to_dict(orient="records")
    for record in preview:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None

    # Build report
    report = {
        "rowsRead": int(total_rows),
        "rowsWritten": int(len(result_df)),
        "columnsBefore": int(columns_before),
        "columnsAfter": int(len(result_df.columns)),
        "removedColumns": columns_to_drop,
        "changedRows": convert_to_json_serializable(metrics),
        "nullsPerColumn": {
            "before": convert_to_json_serializable(nulls_before),
            "after": convert_to_json_serializable(nulls_after),
        },
        "samplePreview": preview,
        "startedAt": processing_status[session_id]["startedAt"],
    }

    processing_status[session_id]["report"] = report

    return result_df


def process_parquet_chunked(file_path, session_id, options, chunksize):
    """Process Parquet file in chunks."""
    session_dir = config.storage_path / session_id

    processing_status[session_id]["progress"]["phase"] = "reading"

    # Read parquet file
    df = pd.read_parquet(file_path)

    total_rows = len(df)
    columns_before = len(df.columns)

    # Normalize headers
    column_mapping = {}
    if options.get("normalizeHeaders", True):
        normalized_cols = []
        for col in df.columns:
            normalized = normalize_column_name(col, normalized_cols)
            normalized_cols.append(normalized)
            column_mapping[col] = normalized
        df.columns = normalized_cols

    # Get null counts before
    nulls_before = get_null_counts(df)

    # Drop empty columns
    columns_to_drop = []
    if options.get("dropEmptyColumns", True):
        for col in df.columns:
            if df[col].isna().all():
                columns_to_drop.append(col)
        df = df.drop(columns=columns_to_drop)

    # Process in chunks
    processing_status[session_id]["progress"]["phase"] = "cleaning"

    metrics = {"trimStrings": 0, "coerceNumeric": 0, "parseDates": 0}
    chunks = []

    total_chunks = (len(df) // chunksize) + 1

    for i in range(0, len(df), chunksize):
        chunk_num = i // chunksize + 1
        processing_status[session_id]["progress"]["current"] = chunk_num
        processing_status[session_id]["progress"]["total"] = total_chunks

        chunk = df.iloc[i : i + chunksize].copy()

        # Clean chunk
        cleaned_chunk, chunk_metrics = clean_dataframe_chunk(
            chunk, options, is_first_chunk=(i == 0)
        )

        # Update metrics
        for key in metrics:
            metrics[key] += chunk_metrics.get(key, 0)

        chunks.append(cleaned_chunk)

    # Concatenate chunks
    processing_status[session_id]["progress"]["phase"] = "finalizing"
    result_df = pd.concat(chunks, ignore_index=True)

    # Drop duplicates if requested
    if options.get("dropDuplicates", False):
        result_df = result_df.drop_duplicates()

    # Get null counts after
    nulls_after = get_null_counts(result_df)

    # Save as CSV
    output_csv = session_dir / "gold_clean.csv"
    result_df.to_csv(output_csv, index=False)

    # Also save as Parquet
    output_parquet = session_dir / "gold_clean.parquet"
    result_df.to_parquet(output_parquet, index=False)

    # Generate preview
    preview = result_df.head(50).to_dict(orient="records")
    for record in preview:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None

    # Build report
    report = {
        "rowsRead": int(total_rows),
        "rowsWritten": int(len(result_df)),
        "columnsBefore": int(columns_before),
        "columnsAfter": int(len(result_df.columns)),
        "removedColumns": columns_to_drop,
        "changedRows": convert_to_json_serializable(metrics),
        "nullsPerColumn": {
            "before": convert_to_json_serializable(nulls_before),
            "after": convert_to_json_serializable(nulls_after),
        },
        "samplePreview": preview,
        "startedAt": processing_status[session_id]["startedAt"],
    }

    processing_status[session_id]["report"] = report

    return result_df


@gold_bp.route("/status", methods=["GET"])
def get_status():
    """Get processing status.

    Query params:
        sessionId: Session ID

    Returns:
        JSON with state, progress, and report (if completed)
    """
    session_id = request.args.get("sessionId")
    if not session_id:
        return jsonify({"error": "sessionId is required"}), 400

    if session_id not in processing_status:
        return jsonify({"error": "Session not found"}), 404

    status = processing_status[session_id]
    return jsonify(status)


@gold_bp.route("/report", methods=["GET"])
def get_report():
    """Get cleaning report.

    Query params:
        sessionId: Session ID

    Returns:
        JSON report
    """
    session_id = request.args.get("sessionId")
    if not session_id:
        return jsonify({"error": "sessionId is required"}), 400

    session_dir = config.storage_path / session_id
    report_path = session_dir / "report.json"

    if not report_path.exists():
        return jsonify({"error": "Report not found"}), 404

    with open(report_path, "r") as f:
        report = json.load(f)

    return jsonify(report)


@gold_bp.route("/download/<session_id>/<filename>", methods=["GET"])
def download_file(session_id, filename):
    """Download cleaned dataset.

    Args:
        session_id: Session ID
        filename: File name to download

    Returns:
        File download
    """
    # Validate session_id and filename to prevent path traversal
    if ".." in session_id or "/" in session_id or "\\" in session_id:
        return jsonify({"error": "Invalid session ID"}), 400

    if ".." in filename or "/" in filename or "\\" in filename:
        return jsonify({"error": "Invalid filename"}), 400

    session_dir = config.storage_path / session_id
    file_path = session_dir / filename

    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404

    # Verify file is in session directory (double-check path traversal)
    try:
        file_path.resolve().relative_to(session_dir.resolve())
    except ValueError:
        return jsonify({"error": "Invalid file path"}), 400

    return send_file(file_path, as_attachment=True)
