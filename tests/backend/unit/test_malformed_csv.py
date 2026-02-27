"""Teste específico para CSVs mal formatados."""

import tempfile
import pytest
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from src.gold.processor import read_dataset


class TestMalformedCSV:
    """Testes para CSVs mal formatados."""

    def test_csv_with_embedded_newlines(self):
        """Teste CSV com quebras de linha dentro de campos."""
        content = """Nome,Descricao,Valor
"João da Silva","Este é um texto
que tem quebra de linha
no meio do campo",100.50
"Maria Santos","Outro texto normal",200.75"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            df = read_dataset(temp_path)
            assert len(df) >= 2  # Should have at least 2 valid rows
            assert len(df.columns) == 3  # Should have 3 columns
            assert "Nome" in df.columns or "nome" in df.columns
        finally:
            temp_path.unlink()

    def test_csv_with_unbalanced_quotes(self):
        """Teste CSV com aspas não balanceadas."""
        content = """ID,Nome,Status
1,"João Silva,Ativo
2,"Maria" Santos,Inativo
3,Pedro "Costa,Ativo"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            df = read_dataset(temp_path)
            # Should not crash and should get some data
            assert len(df) >= 1
            assert len(df.columns) >= 2
        finally:
            temp_path.unlink()

    def test_csv_with_inconsistent_columns(self):
        """Teste CSV com número inconsistente de colunas."""
        content = """A,B,C
1,2,3
4,5,6,7,8,9
10,11
12,13,14"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            df = read_dataset(temp_path)
            # Should handle inconsistent columns gracefully
            assert len(df) >= 2  # Should get some rows
            assert len(df.columns) >= 3  # Should have at least the expected columns
        finally:
            temp_path.unlink()

    def test_csv_with_special_characters(self):
        """Teste CSV com caracteres especiais e encoding misto."""
        content = """Produto,Preço,Descrição
Café Premium,"R$ 15,50","Café 100% arábica"
Açúcar Cristal,"R$ 3,80",Açúcar refinado
Arroz Integral,"R$ 8,90",Sem agrotóxicos"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            df = read_dataset(temp_path)
            assert len(df) == 3
            assert len(df.columns) == 3
            # Check if special characters are preserved
            product_col = None
            for col in df.columns:
                if "produto" in col.lower():
                    product_col = col
                    break
            if product_col:
                assert "Café" in str(df[product_col].iloc[0]) or "Cafe" in str(
                    df[product_col].iloc[0]
                )
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
