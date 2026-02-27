"""Unit tests for code quality validation of generated PySpark code."""
import sys
import ast
import unittest
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from src.dsl_parser.generator import generate_dsl
from src.code_generator.pyspark_generator import generate_pyspark_code
from utilities.sample_answers import SAMPLE_ANSWERS


class TestCodeQuality(unittest.TestCase):
    """Test suite for validating the quality of generated PySpark code."""
    def setUp(self):
        """Configura o ambiente de teste gerando o código uma vez para todos os testes."""
        self.dsl = generate_dsl(SAMPLE_ANSWERS)
        self.code = generate_pyspark_code(self.dsl)

    def test_code_is_valid_python(self):
        """Verifica se o código gerado é Python válido que pode ser parseado."""
        # Substitui aspas duplas consecutivas por aspas simples para validação
        code_for_validation = self.code.replace("''", "'")
        try:
            ast.parse(code_for_validation)
        except SyntaxError as e:
            self.fail(f"O código gerado contém erro de sintaxe: {str(e)}")

    def test_code_structure(self):
        """Verifica se o código contém as seções estruturais esperadas."""
        required_sections = [
            "# Data Quality Validation Script",
            "# After installation above",
            "import os",
            "SparkSession.builder",
            "# Helper function",
            "# 2. Upload the data file",
            "# 3. Read data from file",
            "# 4. Applying Data Quality Rules",
            "# 5. Data Quality Summary",
            "# 6. Finalize Spark Session",
        ]

        for section in required_sections:
            self.assertIn(
                section, self.code, f"Seção esperada não encontrada: {section}"
            )

    def test_imports(self):
        """Verifica se todas as importações necessárias estão presentes."""
        required_imports = [
            "import os",
            "import findspark",
            "from pyspark.sql import SparkSession",
            "from pyspark.sql.functions import",
            "from google.colab import files",
        ]

        for imp in required_imports:
            self.assertIn(imp, self.code, f"Importação necessária ausente: {imp}")

    def test_spark_configuration(self):
        """Verifica se a configuração do Spark está correta."""
        spark_config = ["SparkSession.builder", ".appName", ".master", ".getOrCreate()"]

        for config in spark_config:
            self.assertIn(config, self.code, f"Configuração Spark ausente: {config}")

    def test_error_handling(self):
        """Verifica se o código inclui tratamento básico de erros."""
        error_components = ["try:", "except", "exit("]

        for component in error_components:
            self.assertIn(
                component,
                self.code,
                f"Componente de tratamento de erro ausente: {component}",
            )

    def test_helper_functions(self):
        """Verifica se as funções auxiliares necessárias estão presentes."""
        helper_functions = [
            "def run_check",
            "failed_count = failed_df.count()",
            "return all_failed_records_list",
        ]

        for function in helper_functions:
            self.assertIn(
                function,
                self.code,
                f"Função auxiliar ausente ou incompleta: {function}",
            )

    def test_data_validation_rules(self):
        """Verifica se o código inclui validações básicas de dados."""
        validation_components = ["df.filter", "col(", "print(f", "all_failed_records"]

        for component in validation_components:
            self.assertIn(
                component, self.code, f"Componente de validação ausente: {component}"
            )

    def test_spark_cleanup(self):
        """Verifica se o código inclui limpeza adequada dos recursos Spark."""
        cleanup_components = ["spark.stop()", 'print("\\nSpark session finalized.")']

        for component in cleanup_components:
            self.assertIn(
                component, self.code, f"Componente de limpeza ausente: {component}"
            )

    def test_colab_compatibility(self):
        """Verifica se o código é compatível com o ambiente Google Colab."""
        colab_components = [
            "from google.colab import files",
            "files.upload()",
            "findspark.init()",
            "SparkSession.builder",
            '.master("local[*]")',
            'print("Please upload your CSV file")',
            "try:",
            "next(iter(uploaded))",
            "df.printSchema()",
            "show(truncate=False)",
        ]

        for component in colab_components:
            self.assertIn(
                component,
                self.code,
                f"Componente necessário para Colab ausente: {component}",
            )

        # Verifica se não há caminhos absolutos no código (incompatível com Colab)
        code_lines = self.code.split("\\n")
        for line in code_lines:
            if "C:" in line or "D:" in line:  # Procura por caminhos Windows
                self.fail(
                    f"Caminho absoluto Windows detectado (incompatível com Colab): {line}"
                )
            if "/home/" in line:  # Procura por caminhos Linux absolutos
                self.fail(
                    f"Caminho absoluto Linux detectado (incompatível com Colab): {line}"
                )


if __name__ == "__main__":
    unittest.main()
