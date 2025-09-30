# Data Quality Chatbot

Um chatbot interativo para definir regras de qualidade de dados e gerar scripts PySpark correspondentes.

# How to Run
abra dois terminais:
rodar api: 
```(.venv) (base) PS C:\Users\Icaro\OneDrive\Documents\projetos-google-cli\data-quality-chatbot\src> python api.py```

rodar frontend:
```(base) PS C:\Users\Icaro\OneDrive\Documents\projetos-google-cli\data-quality-chatbot\frontend\frontend> npm start```

## Visão Geral

Este projeto oferece uma solução para automatizar a criação de regras de qualidade de dados e a geração de código PySpark para aplicá-las. Através de uma interface de linha de comando, o usuário pode responder a perguntas sobre seus dados e as regras desejadas. O chatbot então traduz essas respostas em uma DSL (Domain Specific Language) estruturada e, posteriormente, em um script PySpark funcional.

## Funcionalidades

*   **Coleta de Requisitos**: Interage com o usuário via CLI para coletar informações sobre o dataset e as regras de qualidade de dados desejadas.
*   **Geração de DSL**: Converte as respostas do usuário em um formato DSL (JSON) que representa as regras de qualidade de dados de forma estruturada e legível por máquina.
*   **Geração de Código PySpark**: A partir da DSL gerada, o chatbot cria scripts PySpark prontos para serem executados em ambientes Spark, aplicando as regras de qualidade de dados definidas.
*   **Suporte a Diversas Regras**:
    *   **Validação de Esquema**: Verifica nomes e tipos de colunas, e se o dataset possui cabeçalho.
    *   **Integridade de Dados**:
        *   `not_null`: Garante que colunas não contenham valores ausentes.
        *   `uniqueness`: Assegura que colunas ou combinações de colunas tenham valores únicos.
    *   **Restrições de Valor**:
        *   `format`: Valida o formato de valores em colunas (e.g., datas, e-mails).
        *   `range`: Verifica se valores numéricos estão dentro de um intervalo especificado.
        *   `in_set`: Confere se valores pertencem a um conjunto predefinido de opções.
        *   `regex`: Valida valores contra um padrão de expressão regular.
        *   `value_distribution`: Permite verificar a frequência de ocorrência de valores específicos.

## Estrutura do Projeto

```
data-quality-chatbot/
├── data/                     # Diretório para dados de exemplo ou datasets de entrada.
├── dsl/                      # Armazena os arquivos DSL (JSON) gerados pelo chatbot.
├── output/                   # Armazena os scripts PySpark (.py) gerados.
├── notebooks/                # Notebooks Jupyter para experimentação ou demonstração.
├── src/
│   ├── chatbot/              # Lógica principal do chatbot e interação com o usuário.
│   │   ├── main.py           # Ponto de entrada do chatbot.
│   │   ├── questions.py      # Definição das perguntas feitas ao usuário.
│   │   └── answers.py        # Gerenciamento das respostas do usuário.
│   ├── code_generator/       # Módulos para gerar código PySpark a partir da DSL.
│   │   └── pyspark_generator.py # Lógica de geração de código PySpark.
│   ├── dsl_parser/           # Módulos para parsing e geração da DSL.
│   │   └── generator.py      # Lógica para converter respostas em DSL.
│   └── __init__.py
├── tests/                    # Testes unitários para as diferentes partes do projeto.
│   ├── test_generator.py
│   ├── test_pyspark_generator.py
│   └── sample_answers.py
└── .gitignore                # Arquivo para ignorar arquivos e diretórios no controle de versão.
└── README.md                 # Este arquivo.
```

## Como Usar

### Pré-requisitos

*   Python 3.x
*   pip (gerenciador de pacotes do Python)

### Instalação

1.  Clone o repositório:
    ```bash
    git clone https://github.com/seu-usuario/data-quality-chatbot.git
    cd data-quality-chatbot
    ```
    (Nota: Substitua `https://github.com/seu-usuario/data-quality-chatbot.git` pelo link real do seu repositório, se aplicável.)

2.  Crie e ative um ambiente virtual (recomendado):
    ```bash
    python -m venv .venv
    # No Windows:
    .venv\\Scripts\\activate
    # No macOS/Linux:
    source .venv/bin/activate
    ```

3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
    (Nota: Se o arquivo `requirements.txt` não existir, você precisará criá-lo com as dependências do projeto, como `pyspark` e outras que possam ser necessárias.)

### Executando o Chatbot

Para iniciar o chatbot, execute o seguinte comando no terminal:

```bash
python -m src.chatbot.main
```

O chatbot fará uma série de perguntas sobre o seu dataset e as regras de qualidade de dados que você deseja aplicar. Ao final, ele exibirá a DSL gerada e o código PySpark correspondente, com a opção de salvá-los em arquivos.

### Exemplo de Interação

```
Welcome to the Data Quality Chatbot!

--- Dataset Information ---
What is the name of the dataset you want to validate? my_sales_data
What is the source of the data (e.g., a file path, a database table)? /data/sales.csv
What is the format of the data (e.g., CSV, JSON, Parquet)? CSV

--- Schema Validation ---
Does the data have a header? yes
What are the expected column names, in order? product_id, sale_date, amount, region
What is the expected data type for each column (e.g., string, integer, float, date)? string, date, float, string

--- Data Integrity ---
Which columns should not contain any missing values (i.e., are mandatory)? product_id, sale_date
Which columns should contain unique values (i.e., are primary keys)? product_id

--- Value Constraints ---
Are there any columns that should have a specific format (e.g., a date format like YYYY-MM-DD)? sale_date:YYYY-MM-DD
Are there any columns that should have a minimum or maximum value? amount:0:1000
Are there any columns that should only contain values from a specific set (e.g., a list of categories)? region:[North,South,East,West]
Are there any columns that should match a specific regular expression pattern? product_id:^[A-Z]{3}\\d{4}$
Are there any columns for which you want to check the value distribution (e.g., to ensure certain values appear with a specific frequency)? region:North:0.2:0.4

--- Generated DSL ---
{
    "dataset": {
        "name": "my_sales_data",
        "source": "/data/sales.csv",
        "format": "CSV",
        "has_header": true,
        "schema": {
            "product_id": "string",
            "sale_date": "date",
            "amount": "float",
            "region": "string"
        }
    },
    "rules": [
        {
            "type": "not_null",
            "column": "product_id"
        },
        {
            "type": "not_null",
            "column": "sale_date"
        },
        {
            "type": "uniqueness",
            "columns": [
                "product_id"
            ]
        },
        {
            "type": "format",
            "column": "sale_date",
            "format": "YYYY-MM-DD"
        },
        {
            "type": "range",
            "column": "amount",
            "min": 0.0,
            "max": 1000.0
        },
        {
            "type": "in_set",
            "column": "region",
            "values": [
                "North",
                "South",
                "East",
                "West"
            ]
        },
        {
            "type": "regex",
            "column": "product_id",
            "pattern": "^[A-Z]{3}\\d{4}$"
        },
        {
            "type": "value_distribution",
            "column": "region",
            "value": "North",
            "min_freq": 0.2,
            "max_freq": 0.4
        }
    ]
}

Would you like to save the generated DSL to a file? (yes/no): yes
Please enter a filename for the DSL (e.g., my_rules.json): sales_rules.json
DSL saved successfully to dsl\\sales_rules.json

--- Generating PySpark Code ---
# PySpark code generated by Data Quality Chatbot
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, isnull, countDistinct, regexp_extract, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, DateType

spark = SparkSession.builder.appName("DataQualityChecks").getOrCreate()

# Define schema
schema = StructType([
    StructField("product_id", StringType(), True),
    StructField("sale_date", DateType(), True),
    StructField("amount", FloatType(), True),
    StructField("region", StringType(), True)
])

# Load data
df = spark.read.csv("/data/sales.csv", header=True, schema=schema)

print("Running Data Quality Checks...")

# Rule: not_null for product_id
null_product_id_count = df.filter(isnull(col("product_id"))).count()
if null_product_id_count > 0:
    print(f"FAIL: Column 'product_id' has {null_product_id_count} null values.")
else:
    print("PASS: Column 'product_id' has no null values.")

# Rule: not_null for sale_date
null_sale_date_count = df.filter(isnull(col("sale_date"))).count()
if null_sale_date_count > 0:
    print(f"FAIL: Column 'sale_date' has {null_sale_date_count} null values.")
else:
    print("PASS: Column 'sale_date' has no null values.")

# Rule: uniqueness for product_id
total_rows = df.count()
distinct_product_id_count = df.select(countDistinct(col("product_id"))).collect()[0][0]
if total_rows != distinct_product_id_count:
    print(f"FAIL: Column 'product_id' has duplicate values. Total rows: {total_rows}, Distinct product_ids: {distinct_product_id_count}.")
else:
    print("PASS: Column 'product_id' has unique values.")

# Rule: format for sale_date (YYYY-MM-DD)
invalid_sale_date_format_count = df.filter(~col("sale_date").cast(StringType()).rlike("^\\d{4}-\\d{2}-\\d{2}$")).count()
if invalid_sale_date_format_count > 0:
    print(f"FAIL: Column 'sale_date' has {invalid_sale_date_format_count} values with invalid format (expected YYYY-MM-DD).")
else:
    print("PASS: Column 'sale_date' has valid format.")

# Rule: range for amount (min: 0.0, max: 1000.0)
out_of_range_amount_count = df.filter((col("amount") < 0.0) | (col("amount") > 1000.0)).count()
if out_of_range_amount_count > 0:
    print(f"FAIL: Column 'amount' has {out_of_range_amount_count} values out of expected range [0.0, 1000.0].")
else:
    print("PASS: Column 'amount' values are within range.")

# Rule: in_set for region (values: ['North', 'South', 'East', 'West'])
invalid_region_count = df.filter(~col("region").isin(['North', 'South', 'East', 'West'])).count()
if invalid_region_count > 0:
    print(f"FAIL: Column 'region' has {invalid_region_count} values not in the allowed set.")
else:
    print("PASS: Column 'region' values are in the allowed set.")

# Rule: regex for product_id (pattern: ^[A-Z]{3}\d{4}$)
invalid_product_id_regex_count = df.filter(~col("product_id").rlike("^[A-Z]{3}\\d{4}$")).count()
if invalid_product_id_regex_count > 0:
    print(f"FAIL: Column 'product_id' has {invalid_product_id_regex_count} values not matching the regex pattern '^[A-Z]{3}\\d{4}$'.")
else:
    print("PASS: Column 'product_id' values match the regex pattern.")

# Rule: value_distribution for region (value: North, min_freq: 0.2, max_freq: 0.4)
north_region_count = df.filter(col("region") == "North").count()
total_rows = df.count()
north_region_frequency = north_region_count / total_rows if total_rows > 0 else 0

if north_region_frequency >= 0.2 and north_region_frequency <= 0.4:
    print(f"PASS: Value 'North' in column 'region' has frequency {north_region_frequency:.2f}, which is within [0.2, 0.4].")
else:
    print(f"FAIL: Value 'North' in column 'region' has frequency {north_region_frequency:.2f}, which is outside [0.2, 0.4].")

spark.stop()

Would you like to save the generated PySpark code to a file? (yes/no): yes
Please enter a filename for the PySpark code (e.g., data_quality_script.py): sales_data_quality_checks.py
PySpark code saved successfully to output\\sales_data_quality_checks.py