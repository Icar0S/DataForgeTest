"""Robust integration tests for Data Accuracy feature.

This test suite provides comprehensive coverage of the Data Accuracy feature
including edge cases, different file formats, large datasets, and various
normalization options.
"""

import io
import pytest
import tempfile
import shutil
from pathlib import Path
import pandas as pd
import numpy as np
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.api import app


class TestDataAccuracyRobust:
    """Robust integration tests for Data Accuracy feature."""
    
    def setup_method(self):
        """Setup test client and data."""
        self.client = app.test_client()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup test data."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_multiple_key_columns(self):
        """Test comparison with composite key (multiple key columns)."""
        # GOLD dataset with composite key
        gold_csv = Path(self.temp_dir) / "gold_multi_key.csv"
        gold_df = pd.DataFrame({
            "Região": ["Norte", "Norte", "Sul", "Sul"],
            "Produto": ["Café", "Açúcar", "Café", "Açúcar"],
            "Preço": [10.0, 5.0, 12.0, 6.0]
        })
        gold_df.to_csv(gold_csv, index=False)
        
        # TARGET dataset with one difference
        target_csv = Path(self.temp_dir) / "target_multi_key.csv"
        target_df = pd.DataFrame({
            "Região": ["Norte", "Norte", "Sul", "Sul"],
            "Produto": ["Café", "Açúcar", "Café", "Açúcar"],
            "Preço": [10.0, 5.5, 12.0, 6.0]  # Norte-Açúcar is different
        })
        target_df.to_csv(target_csv, index=False)
        
        # Upload GOLD
        with open(gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        assert response.status_code == 200
        session_id = response.get_json()['sessionId']
        
        # Upload TARGET
        with open(target_csv, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.csv')},
                content_type='multipart/form-data'
            )
        assert response.status_code == 200
        
        # Compare with multiple key columns
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["regiao", "produto"],
            "valueColumns": ["preco"],
            "options": {
                "normalizeKeys": True,
                "lowercase": True,
                "stripAccents": True
            }
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        
        # Verify only one mismatch (Norte-Açúcar)
        assert result['summary']['mismatches_total'] == 1
        assert result['summary']['common_keys'] == 4
        assert len(result['diffSample']) == 1
    
    def test_multiple_value_columns(self):
        """Test comparison with multiple value columns."""
        # GOLD dataset
        gold_csv = Path(self.temp_dir) / "gold_multi_val.csv"
        gold_df = pd.DataFrame({
            "ID": ["A", "B", "C"],
            "Quantidade": [100, 200, 300],
            "Preço": [10.0, 20.0, 30.0],
            "Desconto": [0.1, 0.2, 0.15]
        })
        gold_df.to_csv(gold_csv, index=False)
        
        # TARGET dataset with differences in multiple columns
        target_csv = Path(self.temp_dir) / "target_multi_val.csv"
        target_df = pd.DataFrame({
            "ID": ["A", "B", "C"],
            "Quantidade": [100, 250, 300],  # B is different
            "Preço": [10.0, 20.0, 35.0],    # C is different
            "Desconto": [0.1, 0.2, 0.15]
        })
        target_df.to_csv(target_csv, index=False)
        
        # Upload and compare
        with open(gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        session_id = response.get_json()['sessionId']
        
        with open(target_csv, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.csv')},
                content_type='multipart/form-data'
            )
        
        # Compare all value columns
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["id"],
            "valueColumns": ["quantidade", "preco", "desconto"],
            "options": {}
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        
        # Should have 2 mismatches (B-quantidade and C-preco)
        assert result['summary']['mismatches_total'] == 2
        
        # Download corrected file
        corrected_url = result['download']['correctedCsv']
        response = self.client.get(corrected_url)
        assert response.status_code == 200
        
        corrected_df = pd.read_csv(io.BytesIO(response.data))
        # Verify corrections
        assert corrected_df[corrected_df['id'] == 'B']['quantidade'].values[0] == 200
        assert corrected_df[corrected_df['id'] == 'C']['preco'].values[0] == 30.0
    
    def test_excel_file_format(self):
        """Test upload and comparison with XLSX format."""
        # Create XLSX files
        gold_xlsx = Path(self.temp_dir) / "gold.xlsx"
        gold_df = pd.DataFrame({
            "Produto": ["A", "B", "C"],
            "Valor": [10.0, 20.0, 30.0]
        })
        gold_df.to_excel(gold_xlsx, index=False)
        
        target_xlsx = Path(self.temp_dir) / "target.xlsx"
        target_df = pd.DataFrame({
            "Produto": ["A", "B", "C"],
            "Valor": [10.0, 25.0, 30.0]
        })
        target_df.to_excel(target_xlsx, index=False)
        
        # Upload XLSX files
        with open(gold_xlsx, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.xlsx')},
                content_type='multipart/form-data'
            )
        assert response.status_code == 200
        session_id = response.get_json()['sessionId']
        
        with open(target_xlsx, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.xlsx')},
                content_type='multipart/form-data'
            )
        assert response.status_code == 200
        
        # Compare
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["produto"],
            "valueColumns": ["valor"],
            "options": {}
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['summary']['mismatches_total'] == 1
    
    def test_parquet_file_format(self):
        """Test upload and comparison with Parquet format."""
        # Create Parquet files
        gold_parquet = Path(self.temp_dir) / "gold.parquet"
        gold_df = pd.DataFrame({
            "ID": ["X", "Y", "Z"],
            "Amount": [100, 200, 300]
        })
        gold_df.to_parquet(gold_parquet, index=False)
        
        target_parquet = Path(self.temp_dir) / "target.parquet"
        target_df = pd.DataFrame({
            "ID": ["X", "Y", "Z"],
            "Amount": [100, 250, 300]
        })
        target_df.to_parquet(target_parquet, index=False)
        
        # Upload Parquet files
        with open(gold_parquet, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.parquet')},
                content_type='multipart/form-data'
            )
        assert response.status_code == 200
        session_id = response.get_json()['sessionId']
        
        with open(target_parquet, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.parquet')},
                content_type='multipart/form-data'
            )
        assert response.status_code == 200
        
        # Compare
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["id"],
            "valueColumns": ["amount"],
            "options": {}
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['summary']['mismatches_total'] == 1
    
    def test_normalization_options(self):
        """Test different normalization options."""
        # GOLD dataset with special characters
        gold_csv = Path(self.temp_dir) / "gold_norm.csv"
        gold_df = pd.DataFrame({
            "Produto": ["Café Premium", "Açúcar Refinado", "Arroz TIPO 1"],
            "Preço": [10.0, 5.0, 8.0]
        })
        gold_df.to_csv(gold_csv, index=False)
        
        # TARGET dataset with same data but different formatting (case and accents differ)
        target_csv = Path(self.temp_dir) / "target_norm.csv"
        target_df = pd.DataFrame({
            "Produto": ["CAFE PREMIUM", "acucar refinado", "arroz tipo 1"],
            "Preço": [10.0, 5.0, 8.0]
        })
        target_df.to_csv(target_csv, index=False)
        
        # Upload
        with open(gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        session_id = response.get_json()['sessionId']
        
        with open(target_csv, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.csv')},
                content_type='multipart/form-data'
            )
        
        # Compare with full normalization
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["produto"],
            "valueColumns": ["preco"],
            "options": {
                "normalizeKeys": True,
                "lowercase": True,
                "stripAccents": True,
                "stripPunctuation": True
            }
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        # With normalization, all keys should match
        assert result['summary']['common_keys'] == 3
        assert result['summary']['mismatches_total'] == 0
    
    def test_numeric_format_european(self):
        """Test European numeric format (1.234,56)."""
        # GOLD dataset with US format
        gold_csv = Path(self.temp_dir) / "gold_num.csv"
        gold_df = pd.DataFrame({
            "Produto": ["A", "B", "C"],
            "Preço": [1234.56, 5678.90, 100.00]
        })
        gold_df.to_csv(gold_csv, index=False)
        
        # TARGET dataset with European format (as strings)
        target_csv = Path(self.temp_dir) / "target_num.csv"
        target_df = pd.DataFrame({
            "Produto": ["A", "B", "C"],
            "Preço": ["1.234,56", "5.678,90", "100,00"]
        })
        target_df.to_csv(target_csv, index=False)
        
        # Upload
        with open(gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        session_id = response.get_json()['sessionId']
        
        with open(target_csv, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.csv')},
                content_type='multipart/form-data'
            )
        
        # Compare with numeric coercion
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["produto"],
            "valueColumns": ["preco"],
            "options": {
                "coerceNumeric": True,
                "decimalPlaces": 2
            }
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        # All values should match after coercion
        assert result['summary']['mismatches_total'] == 0
    
    def test_empty_target_dataset(self):
        """Test with empty target dataset."""
        # GOLD dataset
        gold_csv = Path(self.temp_dir) / "gold_empty.csv"
        gold_df = pd.DataFrame({
            "ID": ["A", "B"],
            "Value": [10, 20]
        })
        gold_df.to_csv(gold_csv, index=False)
        
        # Empty TARGET dataset
        target_csv = Path(self.temp_dir) / "target_empty.csv"
        target_df = pd.DataFrame({
            "ID": [],
            "Value": []
        })
        target_df.to_csv(target_csv, index=False)
        
        # Upload
        with open(gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        session_id = response.get_json()['sessionId']
        
        with open(target_csv, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.csv')},
                content_type='multipart/form-data'
            )
        
        # Compare
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["id"],
            "valueColumns": ["value"],
            "options": {}
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['summary']['rows_target'] == 0
        assert result['summary']['missing_in_target'] == 2
        assert result['summary']['common_keys'] == 0
    
    def test_missing_column_error(self):
        """Test error handling when specified column doesn't exist."""
        # Create datasets
        gold_csv = Path(self.temp_dir) / "gold_missing_col.csv"
        gold_df = pd.DataFrame({
            "ID": ["A", "B"],
            "Value": [10, 20]
        })
        gold_df.to_csv(gold_csv, index=False)
        
        target_csv = Path(self.temp_dir) / "target_missing_col.csv"
        target_df = pd.DataFrame({
            "ID": ["A", "B"],
            "Value": [10, 20]
        })
        target_df.to_csv(target_csv, index=False)
        
        # Upload
        with open(gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        session_id = response.get_json()['sessionId']
        
        with open(target_csv, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.csv')},
                content_type='multipart/form-data'
            )
        
        # Try to compare with non-existent column
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["id"],
            "valueColumns": ["nonexistent_column"],
            "options": {}
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 422
        error = response.get_json()
        assert 'error' in error
        assert 'not found' in error['error'].lower()
    
    def test_duplicate_policy_sum(self):
        """Test duplicate handling with sum policy."""
        # GOLD dataset
        gold_csv = Path(self.temp_dir) / "gold_dup_sum.csv"
        gold_df = pd.DataFrame({
            "Product": ["A", "B"],
            "Amount": [100, 200]
        })
        gold_df.to_csv(gold_csv, index=False)
        
        # TARGET dataset with duplicates
        target_csv = Path(self.temp_dir) / "target_dup_sum.csv"
        target_df = pd.DataFrame({
            "Product": ["A", "A", "B"],
            "Amount": [50, 50, 200]  # Two A's should sum to 100
        })
        target_df.to_csv(target_csv, index=False)
        
        # Upload
        with open(gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        session_id = response.get_json()['sessionId']
        
        with open(target_csv, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.csv')},
                content_type='multipart/form-data'
            )
        
        # Compare with sum policy
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["product"],
            "valueColumns": ["amount"],
            "options": {
                "targetDuplicatePolicy": "sum"
            }
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        # After summing duplicates, should have no mismatches
        assert result['summary']['mismatches_total'] == 0
    
    def test_duplicate_policy_mean(self):
        """Test duplicate handling with mean policy."""
        # GOLD dataset
        gold_csv = Path(self.temp_dir) / "gold_dup_mean.csv"
        gold_df = pd.DataFrame({
            "Product": ["A", "B"],
            "Price": [50.0, 100.0]
        })
        gold_df.to_csv(gold_csv, index=False)
        
        # TARGET dataset with duplicates
        target_csv = Path(self.temp_dir) / "target_dup_mean.csv"
        target_df = pd.DataFrame({
            "Product": ["A", "A", "B"],
            "Price": [40.0, 60.0, 100.0]  # Average of A should be 50.0
        })
        target_df.to_csv(target_csv, index=False)
        
        # Upload
        with open(gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        session_id = response.get_json()['sessionId']
        
        with open(target_csv, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.csv')},
                content_type='multipart/form-data'
            )
        
        # Compare with mean policy
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["product"],
            "valueColumns": ["price"],
            "options": {
                "targetDuplicatePolicy": "mean"
            }
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        # After averaging duplicates, should have no mismatches
        assert result['summary']['mismatches_total'] == 0
    
    def test_tolerance_precision(self):
        """Test tolerance with different precision levels."""
        # GOLD dataset
        gold_csv = Path(self.temp_dir) / "gold_tol.csv"
        gold_df = pd.DataFrame({
            "ID": ["A", "B", "C"],
            "Value": [100.00, 200.00, 300.00]
        })
        gold_df.to_csv(gold_csv, index=False)
        
        # TARGET dataset with small differences
        target_csv = Path(self.temp_dir) / "target_tol.csv"
        target_df = pd.DataFrame({
            "ID": ["A", "B", "C"],
            "Value": [100.01, 200.05, 300.15]  # Various differences
        })
        target_df.to_csv(target_csv, index=False)
        
        # Upload
        with open(gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        session_id = response.get_json()['sessionId']
        
        with open(target_csv, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.csv')},
                content_type='multipart/form-data'
            )
        
        # Test with tolerance 0.1 (should accept A and B, reject C)
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["id"],
            "valueColumns": ["value"],
            "options": {
                "tolerance": 0.1
            }
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['summary']['mismatches_total'] == 1  # Only C exceeds tolerance
    
    def test_download_security(self):
        """Test that only allowed files can be downloaded."""
        # Create a session
        gold_csv = Path(self.temp_dir) / "gold_sec.csv"
        gold_df = pd.DataFrame({"ID": [1], "Val": [10]})
        gold_df.to_csv(gold_csv, index=False)
        
        with open(gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        session_id = response.get_json()['sessionId']
        
        # Try to download non-allowed file (path traversal)
        # secure_filename strips the path, so this will look for a sanitized filename
        response = self.client.get(
            f'/api/accuracy/download/{session_id}/../../etc/passwd'
        )
        # Should either be 403 (forbidden) or 404 (not found after sanitization)
        assert response.status_code in [403, 404]
        
        # Try to download a file with invalid name (not in allowed list)
        response = self.client.get(
            f'/api/accuracy/download/{session_id}/malicious.exe'
        )
        assert response.status_code == 403
        
        # Try to download non-existent allowed file
        response = self.client.get(
            f'/api/accuracy/download/{session_id}/target_corrected.csv'
        )
        assert response.status_code == 404
    
    def test_accuracy_metrics_calculation(self):
        """Test that accuracy metrics are calculated correctly."""
        # GOLD dataset with 10 items
        gold_csv = Path(self.temp_dir) / "gold_acc.csv"
        gold_df = pd.DataFrame({
            "ID": list(range(1, 11)),
            "Value": [100] * 10
        })
        gold_df.to_csv(gold_csv, index=False)
        
        # TARGET dataset with 7 correct, 3 incorrect
        target_csv = Path(self.temp_dir) / "target_acc.csv"
        target_df = pd.DataFrame({
            "ID": list(range(1, 11)),
            "Value": [100, 100, 100, 100, 100, 100, 100, 110, 110, 110]
        })
        target_df.to_csv(target_csv, index=False)
        
        # Upload
        with open(gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        session_id = response.get_json()['sessionId']
        
        with open(target_csv, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.csv')},
                content_type='multipart/form-data'
            )
        
        # Compare
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["id"],
            "valueColumns": ["value"],
            "options": {}
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        
        # Verify accuracy calculation: 7 correct out of 10 = 0.7
        assert result['summary']['accuracy'] == 0.7
        assert result['summary']['mismatches_total'] == 3
    
    def test_large_dataset_handling(self):
        """Test handling of larger datasets (stress test)."""
        # Create a moderately large dataset (1000 rows)
        gold_csv = Path(self.temp_dir) / "gold_large.csv"
        gold_df = pd.DataFrame({
            "ID": list(range(1, 1001)),
            "Value": [i * 10 for i in range(1, 1001)]
        })
        gold_df.to_csv(gold_csv, index=False)
        
        # TARGET with 10% differences
        target_csv = Path(self.temp_dir) / "target_large.csv"
        target_df = gold_df.copy()
        # Introduce differences in every 10th row
        for i in range(0, 1000, 10):
            target_df.at[i, 'Value'] = target_df.at[i, 'Value'] + 1
        target_df.to_csv(target_csv, index=False)
        
        # Upload
        with open(gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        assert response.status_code == 200
        session_id = response.get_json()['sessionId']
        
        with open(target_csv, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.csv')},
                content_type='multipart/form-data'
            )
        assert response.status_code == 200
        
        # Compare
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["id"],
            "valueColumns": ["value"],
            "options": {}
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        
        # Should have 100 mismatches (every 10th row)
        assert result['summary']['mismatches_total'] == 100
        assert result['summary']['rows_gold'] == 1000
        assert result['summary']['rows_target'] == 1000
        # Accuracy should be 90%
        assert result['summary']['accuracy'] == 0.9
        
        # Verify diff sample is limited
        assert len(result['diffSample']) <= 50  # Limited to 50 in response
    
    def test_extra_keys_in_target(self):
        """Test handling of extra keys in target that don't exist in gold."""
        # GOLD dataset
        gold_csv = Path(self.temp_dir) / "gold_extra.csv"
        gold_df = pd.DataFrame({
            "ID": ["A", "B"],
            "Value": [10, 20]
        })
        gold_df.to_csv(gold_csv, index=False)
        
        # TARGET dataset with extra keys
        target_csv = Path(self.temp_dir) / "target_extra.csv"
        target_df = pd.DataFrame({
            "ID": ["A", "B", "C", "D"],
            "Value": [10, 20, 30, 40]
        })
        target_df.to_csv(target_csv, index=False)
        
        # Upload
        with open(gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        session_id = response.get_json()['sessionId']
        
        with open(target_csv, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.csv')},
                content_type='multipart/form-data'
            )
        
        # Compare
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["id"],
            "valueColumns": ["value"],
            "options": {}
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        
        # Should report extra keys in target
        assert result['summary']['extra_in_target'] == 2
        assert result['summary']['common_keys'] == 2
    
    def test_special_characters_in_data(self):
        """Test handling of special characters in data values."""
        # GOLD dataset with special characters
        gold_csv = Path(self.temp_dir) / "gold_special.csv"
        gold_df = pd.DataFrame({
            "Nome": ["João da Silva", "María José", "François Müller"],
            "Valor": [10.0, 20.0, 30.0]
        })
        gold_df.to_csv(gold_csv, index=False, encoding='utf-8')
        
        # TARGET dataset
        target_csv = Path(self.temp_dir) / "target_special.csv"
        target_df = pd.DataFrame({
            "Nome": ["Joao da Silva", "Maria Jose", "Francois Muller"],
            "Valor": [10.0, 20.0, 30.0]
        })
        target_df.to_csv(target_csv, index=False, encoding='utf-8')
        
        # Upload
        with open(gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        session_id = response.get_json()['sessionId']
        
        with open(target_csv, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.csv')},
                content_type='multipart/form-data'
            )
        
        # Compare with accent stripping
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["nome"],
            "valueColumns": ["valor"],
            "options": {
                "normalizeKeys": True,
                "stripAccents": True,
                "lowercase": True
            }
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        
        # All keys should match after normalization
        assert result['summary']['common_keys'] == 3
        assert result['summary']['mismatches_total'] == 0
    
    def test_missing_required_fields(self):
        """Test error handling for missing required fields in compare request."""
        # Create and upload files first
        gold_csv = Path(self.temp_dir) / "gold_req.csv"
        gold_df = pd.DataFrame({"ID": [1], "Val": [10]})
        gold_df.to_csv(gold_csv, index=False)
        
        with open(gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        session_id = response.get_json()['sessionId']
        
        # Try to compare without keyColumns
        compare_payload = {
            "sessionId": session_id,
            "valueColumns": ["val"]
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        error = response.get_json()
        assert 'error' in error
        assert 'keyColumns' in error['error']
    
    def test_session_not_found(self):
        """Test error handling for non-existent session."""
        compare_payload = {
            "sessionId": "non-existent-session-id",
            "keyColumns": ["id"],
            "valueColumns": ["value"]
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 404
        error = response.get_json()
        assert 'error' in error
        assert 'not found' in error['error'].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
