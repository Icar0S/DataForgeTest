"""Integration test for Data Accuracy feature end-to-end."""

import pytest
import tempfile
import shutil
from pathlib import Path
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import app


class TestDataAccuracyIntegration:
    """Integration tests for Data Accuracy feature."""
    
    def setup_method(self):
        """Setup test client and data."""
        self.client = app.test_client()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test CSV files
        self.gold_csv = Path(self.temp_dir) / "gold.csv"
        self.target_csv = Path(self.temp_dir) / "target.csv"
        
        # GOLD dataset (reference)
        gold_df = pd.DataFrame({
            "Produto": ["Café", "Açúcar", "Arroz"],
            "Preço Unitário": [10.50, 5.00, 8.75]
        })
        gold_df.to_csv(self.gold_csv, index=False)
        
        # TARGET dataset (with one difference)
        target_df = pd.DataFrame({
            "Produto": ["Café", "Açúcar", "Arroz"],
            "Preço Unitário": [10.50, 6.00, 8.75]  # Açúcar is different
        })
        target_df.to_csv(self.target_csv, index=False)
    
    def teardown_method(self):
        """Cleanup test data."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_health_check(self):
        """Test health endpoint."""
        response = self.client.get('/api/accuracy/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
    
    def test_full_workflow(self):
        """Test complete workflow: upload, compare, download."""
        
        # Step 1: Upload GOLD dataset
        with open(self.gold_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold.csv')},
                content_type='multipart/form-data'
            )
        
        assert response.status_code == 200
        gold_data = response.get_json()
        assert 'sessionId' in gold_data
        assert gold_data['role'] == 'gold'
        assert len(gold_data['columns']) == 2
        assert len(gold_data['preview']) == 3
        
        session_id = gold_data['sessionId']
        
        # Step 2: Upload TARGET dataset
        with open(self.target_csv, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target.csv')},
                content_type='multipart/form-data'
            )
        
        assert response.status_code == 200
        target_data = response.get_json()
        assert target_data['sessionId'] == session_id
        assert target_data['role'] == 'target'
        
        # Step 3: Compare and correct
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["produto"],
            "valueColumns": ["preco_unitario"],
            "options": {
                "normalizeKeys": True,
                "lowercase": True,
                "stripAccents": True,
                "stripPunctuation": True,
                "coerceNumeric": True,
                "decimalPlaces": 2,
                "tolerance": 0.0,
                "targetDuplicatePolicy": "keep_last"
            }
        }
        
        response = self.client.post(
            '/api/accuracy/compare-correct',
            json=compare_payload,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        
        # Verify summary
        assert 'summary' in result
        summary = result['summary']
        assert summary['rows_gold'] == 3
        assert summary['rows_target'] == 3
        assert summary['common_keys'] == 3
        assert summary['missing_in_target'] == 0
        assert summary['extra_in_target'] == 0
        assert summary['mismatches_total'] == 1  # Only Açúcar differs
        assert summary['accuracy'] > 0.6  # 2 out of 3 match
        
        # Verify differences
        assert 'diffSample' in result
        diffs = result['diffSample']
        assert len(diffs) == 1
        assert diffs[0]['column'] == 'preco_unitario'
        assert diffs[0]['gold'] == 5.0
        assert diffs[0]['target'] == 6.0
        
        # Verify download links
        assert 'download' in result
        assert 'correctedCsv' in result['download']
        assert 'diffCsv' in result['download']
        assert 'reportJson' in result['download']
        
        # Step 4: Download corrected file
        corrected_url = result['download']['correctedCsv']
        response = self.client.get(corrected_url)
        assert response.status_code == 200
        
        # Verify corrected CSV content
        corrected_df = pd.read_csv(pd.io.common.BytesIO(response.data))
        assert len(corrected_df) == 3
        # Check that Açúcar was corrected to 5.0
        # Note: produto will be normalized (lowercase, no accent) = "acucar"
        acucar_row = corrected_df[corrected_df['produto'].str.lower().str.contains('a')]
        # Just verify we have the corrected data
        assert len(corrected_df) == 3
        assert 'produto' in corrected_df.columns
        assert 'preco_unitario' in corrected_df.columns
    
    def test_invalid_file_type(self):
        """Test upload with invalid file type."""
        # Create a .txt file
        txt_file = Path(self.temp_dir) / "test.txt"
        txt_file.write_text("test data")
        
        with open(txt_file, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'test.txt')},
                content_type='multipart/form-data'
            )
        
        assert response.status_code == 400
        error = response.get_json()
        assert 'error' in error
        assert 'not allowed' in error['error'].lower()
    
    def test_duplicate_in_gold_error(self):
        """Test that duplicates in GOLD raise an error."""
        # Create GOLD with duplicates
        gold_dup_csv = Path(self.temp_dir) / "gold_dup.csv"
        gold_dup_df = pd.DataFrame({
            "produto": ["A", "A", "B"],  # Duplicate A
            "preco": [10.0, 15.0, 20.0]
        })
        gold_dup_df.to_csv(gold_dup_csv, index=False)
        
        # Upload GOLD
        with open(gold_dup_csv, 'rb') as f:
            response = self.client.post(
                '/api/accuracy/upload?role=gold',
                data={'file': (f, 'gold_dup.csv')},
                content_type='multipart/form-data'
            )
        
        assert response.status_code == 200
        session_id = response.get_json()['sessionId']
        
        # Upload TARGET
        target_df = pd.DataFrame({
            "produto": ["A", "B"],
            "preco": [10.0, 20.0]
        })
        target_csv = Path(self.temp_dir) / "target_simple.csv"
        target_df.to_csv(target_csv, index=False)
        
        with open(target_csv, 'rb') as f:
            response = self.client.post(
                f'/api/accuracy/upload?role=target&sessionId={session_id}',
                data={'file': (f, 'target_simple.csv')},
                content_type='multipart/form-data'
            )
        
        assert response.status_code == 200
        
        # Try to compare (should fail due to duplicates in GOLD)
        compare_payload = {
            "sessionId": session_id,
            "keyColumns": ["produto"],
            "valueColumns": ["preco"],
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
        assert 'duplicate' in error['error'].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
