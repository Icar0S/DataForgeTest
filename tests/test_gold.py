"""Tests for GOLD Dataset Testing feature."""

import pytest
import json
import tempfile
from pathlib import Path
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from gold.config import GoldConfig
from gold.processor import (
    normalize_column_name,
    trim_string,
    coerce_numeric,
    parse_date,
    clean_dataframe_chunk,
    get_null_counts,
)


class TestGoldProcessor:
    """Test GOLD data processing functions."""

    def test_normalize_column_name(self):
        """Test column name normalization."""
        assert normalize_column_name("First Name") == "first_name"
        assert normalize_column_name("  Spaced  ") == "spaced"
        assert normalize_column_name("Año") == "ano"
        assert normalize_column_name("Column-With-Dashes") == "column_with_dashes"
        
        # Test deduplication
        existing = ["name"]
        assert normalize_column_name("Name", existing) == "name_2"
        existing.append("name_2")
        assert normalize_column_name("Name", existing) == "name_3"

    def test_trim_string(self):
        """Test string trimming."""
        assert trim_string("  hello  ") == "hello"
        assert trim_string("test\x00string") == "teststring"
        assert pd.isna(trim_string("   "))
        assert trim_string(123) == 123
        assert pd.isna(trim_string(None))

    def test_coerce_numeric(self):
        """Test numeric coercion."""
        # US format
        assert coerce_numeric("1,234.56") == 1234.56
        # European format
        assert coerce_numeric("1.234,56") == 1234.56
        # Simple decimal
        assert coerce_numeric("1.50") == 1.50
        # Already numeric
        assert coerce_numeric(100) == 100
        # Not numeric
        assert coerce_numeric("abc") == "abc"

    def test_parse_date(self):
        """Test date parsing."""
        # ISO format
        result = parse_date("2024-01-15")
        assert pd.notna(result)
        
        # Common format
        result = parse_date("01/15/2024")
        assert pd.notna(result)
        
        # Not a date
        result = parse_date("not a date")
        assert result == "not a date"

    def test_clean_dataframe_chunk(self):
        """Test dataframe cleaning."""
        df = pd.DataFrame({
            "col1": ["  value1  ", "value2", None],
            "col2": ["1,234.56", "2.50", "3"],
            "col3": ["2024-01-01", "2024-01-02", "2024-01-03"],
        })

        options = {
            "trimStrings": True,
            "coerceNumeric": True,
            "parseDates": True,
        }

        cleaned_df, metrics = clean_dataframe_chunk(df, options)

        # Check trimming worked
        assert cleaned_df.loc[0, "col1"] == "value1"
        
        # Check metrics
        assert metrics["trimStrings"] > 0

    def test_get_null_counts(self):
        """Test null counting."""
        df = pd.DataFrame({
            "col1": [1, 2, None, 4],
            "col2": [None, None, None, None],
            "col3": ["a", "b", "c", "d"],
        })

        nulls = get_null_counts(df)
        assert nulls["col1"] == 1
        assert nulls["col2"] == 4
        assert nulls["col3"] == 0


class TestGoldAPI:
    """Test GOLD API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from api import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def sample_csv(self):
        """Create sample CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write("Name,Age,City,Empty Column\n")
            f.write("John Doe,30,New York,\n")
            f.write("Jane Smith,25,Los Angeles,\n")
            f.write("  Bob  ,28,  Chicago  ,\n")
            f.flush()
            fname = f.name
        yield fname
        Path(fname).unlink(missing_ok=True)

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/gold/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['ok'] is True

    def test_upload_no_file(self, client):
        """Test upload without file."""
        response = client.post('/api/gold/upload')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_upload_invalid_type(self, client):
        """Test upload with invalid file type."""
        with tempfile.NamedTemporaryFile(suffix='.txt') as f:
            f.write(b"test content")
            f.seek(0)
            response = client.post(
                '/api/gold/upload',
                data={'file': (f, 'test.txt')},
                content_type='multipart/form-data'
            )
        assert response.status_code == 400

    def test_upload_csv(self, client, sample_csv):
        """Test successful CSV upload."""
        with open(sample_csv, 'rb') as f:
            response = client.post(
                '/api/gold/upload',
                data={'file': (f, 'test.csv')},
                content_type='multipart/form-data'
            )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'sessionId' in data
        assert 'datasetId' in data
        assert 'columns' in data
        assert 'sample' in data
        assert data['format'] == 'csv'
        
        # Should detect 4 columns
        assert len(data['columns']) == 4

    def test_upload_and_clean(self, client, sample_csv):
        """Test upload and cleaning workflow."""
        # Upload
        with open(sample_csv, 'rb') as f:
            upload_response = client.post(
                '/api/gold/upload',
                data={'file': (f, 'test.csv')},
                content_type='multipart/form-data'
            )
        
        upload_data = json.loads(upload_response.data)
        session_id = upload_data['sessionId']
        
        # Clean
        clean_response = client.post(
            '/api/gold/clean',
            data=json.dumps({
                'sessionId': session_id,
                'datasetId': upload_data['datasetId'],
                'options': {
                    'dropEmptyColumns': True,
                    'normalizeHeaders': True,
                    'trimStrings': True,
                    'coerceNumeric': True,
                    'parseDates': False,
                    'dropDuplicates': False,
                }
            }),
            content_type='application/json'
        )
        
        assert clean_response.status_code == 200
        clean_data = json.loads(clean_response.data)
        assert clean_data['status'] == 'completed'
        assert 'download' in clean_data

    def test_status_endpoint(self, client, sample_csv):
        """Test status endpoint."""
        # Upload and start processing
        with open(sample_csv, 'rb') as f:
            upload_response = client.post(
                '/api/gold/upload',
                data={'file': (f, 'test.csv')},
                content_type='multipart/form-data'
            )
        
        upload_data = json.loads(upload_response.data)
        session_id = upload_data['sessionId']
        
        # Start cleaning
        client.post(
            '/api/gold/clean',
            data=json.dumps({
                'sessionId': session_id,
                'datasetId': upload_data['datasetId'],
                'options': {}
            }),
            content_type='application/json'
        )
        
        # Check status
        status_response = client.get(f'/api/gold/status?sessionId={session_id}')
        assert status_response.status_code == 200
        status_data = json.loads(status_response.data)
        assert 'state' in status_data

    def test_report_endpoint(self, client, sample_csv):
        """Test report endpoint."""
        # Upload
        with open(sample_csv, 'rb') as f:
            upload_response = client.post(
                '/api/gold/upload',
                data={'file': (f, 'test.csv')},
                content_type='multipart/form-data'
            )
        
        upload_data = json.loads(upload_response.data)
        session_id = upload_data['sessionId']
        
        # Clean
        client.post(
            '/api/gold/clean',
            data=json.dumps({
                'sessionId': session_id,
                'datasetId': upload_data['datasetId'],
                'options': {}
            }),
            content_type='application/json'
        )
        
        # Get report
        report_response = client.get(f'/api/gold/report?sessionId={session_id}')
        assert report_response.status_code == 200
        report_data = json.loads(report_response.data)
        assert 'rowsRead' in report_data
        assert 'rowsWritten' in report_data
        assert 'columnsBefore' in report_data
        assert 'columnsAfter' in report_data

    def test_download_endpoint(self, client, sample_csv):
        """Test download endpoint."""
        # Upload
        with open(sample_csv, 'rb') as f:
            upload_response = client.post(
                '/api/gold/upload',
                data={'file': (f, 'test.csv')},
                content_type='multipart/form-data'
            )
        
        upload_data = json.loads(upload_response.data)
        session_id = upload_data['sessionId']
        
        # Clean
        client.post(
            '/api/gold/clean',
            data=json.dumps({
                'sessionId': session_id,
                'datasetId': upload_data['datasetId'],
                'options': {}
            }),
            content_type='application/json'
        )
        
        # Download
        download_response = client.get(f'/api/gold/download/{session_id}/gold_clean.csv')
        assert download_response.status_code == 200

    def test_path_traversal_protection(self, client):
        """Test path traversal attack prevention."""
        # Try to access with path traversal in session ID
        response = client.get('/api/gold/download/../etc/gold_clean.csv')
        # Can be 404 (Flask routing rejects) or 400 (our validation)
        assert response.status_code in [400, 404]
        
        # Try with dots in filename
        response = client.get('/api/gold/download/valid-session/../../../etc/passwd')
        assert response.status_code in [400, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
