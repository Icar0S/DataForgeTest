"""Tests for dataset inspector API routes with error handling validation."""

import os
import json
import tempfile
import pandas as pd
import pytest
from io import BytesIO
from flask import Flask

# Import the blueprint - using relative import path
import sys
from pathlib import Path

# Add src to path if not already there (for test discovery)
src_path = Path(__file__).parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from dataset_inspector.routes import dataset_inspector_bp


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(dataset_inspector_bp)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestInspectEndpoint:
    """Tests for /api/datasets/inspect endpoint."""
    
    def test_no_file_provided(self, client):
        """Test request without file."""
        response = client.post('/api/datasets/inspect')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'No file provided'
    
    def test_empty_filename(self, client):
        """Test request with empty filename."""
        data = {'file': (BytesIO(b''), '')}
        response = client.post('/api/datasets/inspect', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'No file selected'
    
    def test_invalid_file_extension(self, client):
        """Test request with unsupported file extension."""
        data = {'file': (BytesIO(b'test data'), 'test.txt')}
        response = client.post('/api/datasets/inspect', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'not allowed' in data['error'].lower()
    
    def test_empty_file(self, client):
        """Test request with empty file."""
        data = {'file': (BytesIO(b''), 'test.csv')}
        response = client.post('/api/datasets/inspect', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'empty' in data['error'].lower()
    
    def test_valid_csv_file(self, client):
        """Test request with valid CSV file."""
        csv_content = b'id,name,value\n1,Alice,100\n2,Bob,200\n'
        data = {'file': (BytesIO(csv_content), 'test.csv')}
        response = client.post('/api/datasets/inspect', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        result = response.get_json()
        assert 'format' in result
        assert result['format'] == 'csv'
        assert result['row_count'] == 2
        assert result['column_count'] == 3
        assert 'columns' in result
        assert 'preview' in result
        assert 'filename' in result
        assert result['filename'] == 'test.csv'
    
    def test_valid_csv_with_custom_delimiter(self, client):
        """Test CSV with custom delimiter."""
        csv_content = b'id;name;value\n1;Alice;100\n2;Bob;200\n'
        data = {
            'file': (BytesIO(csv_content), 'test.csv'),
            'delimiter': ';'
        }
        response = client.post('/api/datasets/inspect', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        result = response.get_json()
        assert result['format'] == 'csv'
        assert result['row_count'] == 2
        assert result['detected_options']['delimiter'] == ';'
    
    def test_valid_jsonl_file(self, client):
        """Test request with valid JSON Lines file."""
        jsonl_content = b'{"id": 1, "name": "Alice"}\n{"id": 2, "name": "Bob"}\n'
        data = {'file': (BytesIO(jsonl_content), 'test.jsonl')}
        response = client.post('/api/datasets/inspect', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        result = response.get_json()
        assert result['format'] == 'json'
        assert result['row_count'] == 2
        assert result['column_count'] == 2
    
    def test_valid_json_array_file(self, client):
        """Test request with valid JSON array file."""
        json_content = b'[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]'
        data = {'file': (BytesIO(json_content), 'test.json')}
        response = client.post('/api/datasets/inspect', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        result = response.get_json()
        assert result['format'] == 'json'
        assert result['row_count'] == 2
    
    def test_invalid_json_file(self, client):
        """Test request with invalid JSON file."""
        json_content = b'{"invalid": json without closing brace'
        data = {'file': (BytesIO(json_content), 'test.json')}
        response = client.post('/api/datasets/inspect', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
        assert 'parse' in result['error'].lower() or 'json' in result['error'].lower()
    
    def test_csv_with_no_data_rows(self, client):
        """Test CSV with header but no data rows."""
        csv_content = b'id,name,value\n'
        data = {'file': (BytesIO(csv_content), 'test.csv')}
        response = client.post('/api/datasets/inspect', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
        assert 'no data' in result['error'].lower()
    
    def test_valid_parquet_file(self, client):
        """Test request with valid Parquet file."""
        # Create a parquet file in memory
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'value': [100, 200, 300]
        })
        parquet_bytes = BytesIO()
        df.to_parquet(parquet_bytes, index=False)
        parquet_bytes.seek(0)
        
        data = {'file': (parquet_bytes, 'test.parquet')}
        response = client.post('/api/datasets/inspect', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        result = response.get_json()
        assert result['format'] == 'parquet'
        assert result['row_count'] == 3
        assert result['column_count'] == 3
    
    def test_csv_with_custom_sample_size(self, client):
        """Test CSV with custom sample size."""
        csv_content = b'id,name\n' + b'\n'.join([f'{i},Name{i}'.encode() for i in range(100)])
        data = {
            'file': (BytesIO(csv_content), 'test.csv'),
            'sample_size': '50'
        }
        response = client.post('/api/datasets/inspect', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        result = response.get_json()
        assert result['row_count'] == 100  # 100 rows of data
    
    def test_csv_with_invalid_sample_size(self, client):
        """Test CSV with invalid sample size (should be ignored)."""
        csv_content = b'id,name\n1,Alice\n2,Bob\n'
        data = {
            'file': (BytesIO(csv_content), 'test.csv'),
            'sample_size': 'invalid'
        }
        response = client.post('/api/datasets/inspect', data=data, content_type='multipart/form-data')
        # Should still succeed but ignore the invalid sample_size
        assert response.status_code == 200
        result = response.get_json()
        assert result['row_count'] == 2
    
    def test_csv_with_negative_sample_size(self, client):
        """Test CSV with negative sample size (should be ignored)."""
        csv_content = b'id,name\n1,Alice\n2,Bob\n'
        data = {
            'file': (BytesIO(csv_content), 'test.csv'),
            'sample_size': '-10'
        }
        response = client.post('/api/datasets/inspect', data=data, content_type='multipart/form-data')
        # Should still succeed but ignore the invalid sample_size
        assert response.status_code == 200
        result = response.get_json()
        assert result['row_count'] == 2


class TestGenerateDSLEndpoint:
    """Tests for /api/datasets/generate-dsl endpoint."""
    
    def test_no_data_provided(self, client):
        """Test request with no JSON data."""
        response = client.post('/api/datasets/generate-dsl',
                             data='',
                             content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        # Empty data should be rejected as invalid JSON
        assert 'invalid json' in data['error'].lower() or 'no data' in data['error'].lower()
    
    def test_missing_metadata_field(self, client):
        """Test request without metadata field."""
        response = client.post('/api/datasets/generate-dsl',
                             data=json.dumps({}),
                             content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        # Empty dict should result in missing metadata error
        assert 'metadata' in data['error'].lower() or 'required' in data['error'].lower()
    
    def test_valid_metadata(self, client):
        """Test with valid metadata."""
        metadata = {
            'format': 'csv',
            'row_count': 100,
            'column_count': 3,
            'columns': [
                {'name': 'id', 'type': 'int64', 'null_count': 0},
                {'name': 'name', 'type': 'object', 'null_count': 5},
                {'name': 'value', 'type': 'float64', 'null_count': 10}
            ]
        }
        response = client.post('/api/datasets/generate-dsl',
                             data=json.dumps({'metadata': metadata}),
                             content_type='application/json')
        assert response.status_code == 200
        result = response.get_json()
        assert 'dsl' in result


class TestGeneratePySparkEndpoint:
    """Tests for /api/datasets/generate-pyspark endpoint."""
    
    def test_no_data_provided(self, client):
        """Test request with no JSON data."""
        response = client.post('/api/datasets/generate-pyspark',
                             data='',
                             content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        # Empty data should be rejected as invalid JSON
        assert 'invalid json' in data['error'].lower() or 'no data' in data['error'].lower()
    
    def test_missing_dsl_field(self, client):
        """Test request without dsl field."""
        response = client.post('/api/datasets/generate-pyspark',
                             data=json.dumps({}),
                             content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        # Empty dict should result in missing dsl error
        assert 'dsl' in data['error'].lower() or 'required' in data['error'].lower()
    
    def test_valid_dsl(self, client):
        """Test with valid DSL."""
        dsl = {
            'name': 'test_dataset',
            'dataset': {
                'name': 'test_dataset',
                'format': 'csv',
                'path': 'test.csv'
            },
            'schema': [
                {'name': 'id', 'type': 'long'},
                {'name': 'name', 'type': 'string'}
            ],
            'rules': []
        }
        response = client.post('/api/datasets/generate-pyspark',
                             data=json.dumps({'dsl': dsl}),
                             content_type='application/json')
        assert response.status_code == 200
        result = response.get_json()
        assert 'pyspark_code' in result
        assert 'filename' in result
        assert result['filename'] == 'generated_test_dataset.py'


class TestHealthEndpoint:
    """Tests for /api/datasets/health endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/datasets/health')
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'ok'
