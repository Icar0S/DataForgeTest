"""Flask routes for dataset inspection and advanced PySpark generation."""

import os
import sys
import tempfile
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataset_inspector.inspector import inspect_dataset, MAX_FILE_SIZE_MB
from dataset_inspector.dsl_generator import generate_dsl_from_metadata
from code_generator.pyspark_generator import generate_pyspark_code


# Create blueprint
dataset_inspector_bp = Blueprint("dataset_inspector", __name__, url_prefix="/api/datasets")

# Allowed extensions
ALLOWED_EXTENSIONS = {'csv', 'parquet', 'json', 'jsonl'}
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed.
    
    Args:
        filename: Name of the file
        
    Returns:
        True if extension is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_format(filename: str) -> str:
    """Get file format from filename.
    
    Args:
        filename: Name of the file
        
    Returns:
        File format string
    """
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'jsonl':
        return 'json'
    return ext


@dataset_inspector_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "Dataset inspector service is running"})


@dataset_inspector_bp.route("/inspect", methods=["POST"])
def inspect_uploaded_dataset():
    """Inspect an uploaded dataset file.
    
    Request:
        - file: Dataset file (multipart/form-data)
        - delimiter (optional): CSV delimiter
        - encoding (optional): File encoding
        - header (optional): Whether CSV has header (true/false)
        - sample_size (optional): Number of rows to sample for statistics
        
    Returns:
        JSON with dataset metadata, schema, and statistics
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        file_format = get_file_format(filename)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_format}') as tmp_file:
            temp_path = tmp_file.name
            file.save(temp_path)
            
            # Check file size
            file_size = os.path.getsize(temp_path)
            if file_size > MAX_FILE_SIZE_BYTES:
                os.unlink(temp_path)
                return jsonify({
                    "error": f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
                }), 400
            
            # Get optional parameters
            options = {}
            if request.form.get('delimiter'):
                options['delimiter'] = request.form.get('delimiter')
            if request.form.get('encoding'):
                options['encoding'] = request.form.get('encoding')
            if request.form.get('header'):
                options['header'] = request.form.get('header').lower() == 'true'
            if request.form.get('sample_size'):
                try:
                    options['sample_size'] = int(request.form.get('sample_size'))
                except ValueError:
                    pass
            
            # Inspect the dataset
            try:
                metadata = inspect_dataset(temp_path, file_format, options)
                metadata['filename'] = filename
                metadata['file_size_bytes'] = file_size
                
                return jsonify(metadata), 200
            except Exception as e:
                return jsonify({"error": f"Failed to inspect dataset: {str(e)}"}), 500
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
    
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@dataset_inspector_bp.route("/generate-dsl", methods=["POST"])
def generate_dsl_endpoint():
    """Generate DSL from dataset metadata.
    
    Request JSON:
        - metadata: Dataset metadata from inspection
        - user_edits (optional): User edits to override auto-detected values
        
    Returns:
        JSON with generated DSL
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        metadata = data.get('metadata')
        if not metadata:
            return jsonify({"error": "metadata is required"}), 400
        
        user_edits = data.get('user_edits', {})
        
        # Generate DSL
        dsl = generate_dsl_from_metadata(metadata, user_edits)
        
        return jsonify({"dsl": dsl}), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to generate DSL: {str(e)}"}), 500


@dataset_inspector_bp.route("/generate-pyspark", methods=["POST"])
def generate_pyspark_endpoint():
    """Generate PySpark code from DSL.
    
    Request JSON:
        - dsl: DSL dictionary
        
    Returns:
        JSON with generated PySpark code and suggested filename
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        dsl = data.get('dsl')
        if not dsl:
            return jsonify({"error": "dsl is required"}), 400
        
        # Generate PySpark code
        pyspark_code = generate_pyspark_code(dsl)
        
        # Suggest filename
        dataset_name = dsl.get('name', dsl.get('dataset', {}).get('name', 'dataset'))
        filename = f"generated_{dataset_name}.py"
        
        return jsonify({
            "pyspark_code": pyspark_code,
            "filename": filename
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to generate PySpark code: {str(e)}"}), 500
