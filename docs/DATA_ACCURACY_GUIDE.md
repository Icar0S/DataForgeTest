# Data Accuracy Feature - Usage Guide

## Overview

The Data Accuracy feature allows you to compare and correct datasets using a GOLD (reference) dataset as the source of truth. This is particularly useful for:

- Data quality validation
- Correcting price lists or product catalogs
- Reconciling financial data
- Verifying ETL/data migration processes

## Quick Start

### 1. Access the Feature

From the homepage at http://localhost:3000, click the **"Acurácia de Dados (Datasets)"** button.

### 2. Upload Your Datasets

**GOLD Dataset (Reference):**
- This is your trusted, correct dataset
- Must not contain duplicate keys
- Drag & drop or click to select file
- Supported formats: CSV, XLSX, Parquet

**TARGET Dataset (To Validate):**
- This is the dataset you want to check and correct
- Can contain duplicates (handled according to policy)
- Same format support as GOLD

### 3. Map Your Columns

After uploading both files, you'll see the column mapping interface:

**Key Columns:**
- Select the columns that identify unique records
- Examples: product_id, customer_id, order_number
- Can select multiple columns for composite keys
- These will be used to match records between datasets

**Value Columns:**
- Select the columns whose values should be compared
- Examples: price, quantity, status
- Can select multiple columns
- Differences will be detected and corrected

### 4. Configure Options

**Numeric Options:**
- **Tolerance:** Allow small differences (e.g., 0.01 for rounding)
- **Decimal Places:** Number of decimals in corrected values (default: 2)

**Key Normalization:**
- **Lowercase:** Convert keys to lowercase before matching
- **Remove Accents:** Strip accents (café → cafe)
- **Remove Punctuation:** Remove special characters
- **Numeric Coercion:** Convert numbers (handles comma/period variations)

**Duplicate Policy (TARGET only):**
- **Keep Last:** Keep the last occurrence of duplicate keys
- **Sum:** Sum numeric values for duplicates
- **Mean:** Average numeric values for duplicates

### 5. Compare & Correct

Click the **"Comparar & Corrigir"** button to:
- Compare the datasets
- Identify differences
- Generate corrected dataset
- Create detailed reports

### 6. Review Results

**Summary Metrics:**
- Total rows in each dataset
- Common keys found
- Keys missing in TARGET
- Extra keys in TARGET
- Total mismatches detected
- Overall accuracy percentage

**Differences Table:**
- Paginated view of all detected differences
- Shows GOLD value, TARGET original, corrected value, and delta
- Filterable and searchable

### 7. Download Results

Three files are available for download:

1. **Dataset Corrigido (.csv):** The corrected TARGET dataset with GOLD values
2. **Diferenças (.csv):** Detailed list of all corrections made
3. **Relatório (.json):** Complete report with metrics and parameters used

## Example Workflow

### Scenario: Price List Validation

**GOLD Dataset (reference_prices.csv):**
```csv
Produto,Preço Unitário
Café Especial,10.50
Açúcar Cristal,5.00
Arroz Integral,8.75
```

**TARGET Dataset (current_prices.csv):**
```csv
Produto,Preço Unitário
Café Especial,10.50
Açúcar Cristal,6.00
Arroz Integral,8.75
```

**Steps:**
1. Upload both files
2. Select "produto" as Key Column
3. Select "preco_unitario" as Value Column
4. Enable normalization options (to handle "Açúcar" vs "acucar")
5. Set tolerance to 0.0 (exact match required)
6. Click "Comparar & Corrigir"

**Results:**
- Accuracy: 66.67% (2 out of 3 match)
- 1 mismatch detected: "Açúcar Cristal" price differs
- Corrected file will have price 5.00 for "Açúcar Cristal"

## API Usage

For automated workflows, you can use the REST API directly:

```python
import requests

# 1. Upload GOLD
with open('gold.csv', 'rb') as f:
    resp = requests.post(
        'http://localhost:5000/api/accuracy/upload?role=gold',
        files={'file': f}
    )
    session_id = resp.json()['sessionId']

# 2. Upload TARGET
with open('target.csv', 'rb') as f:
    requests.post(
        f'http://localhost:5000/api/accuracy/upload?role=target&sessionId={session_id}',
        files={'file': f}
    )

# 3. Compare and Correct
result = requests.post(
    'http://localhost:5000/api/accuracy/compare-correct',
    json={
        'sessionId': session_id,
        'keyColumns': ['produto'],
        'valueColumns': ['preco_unitario'],
        'options': {
            'tolerance': 0.0,
            'decimalPlaces': 2,
            'targetDuplicatePolicy': 'keep_last'
        }
    }
).json()

# 4. Download corrected file
corrected_csv = requests.get(
    f"http://localhost:5000{result['download']['correctedCsv']}"
)
with open('corrected.csv', 'wb') as f:
    f.write(corrected_csv.content)
```

## Tips and Best Practices

1. **Clean Your GOLD Dataset First:** Ensure your reference dataset is truly accurate and has no duplicates

2. **Choose Key Columns Carefully:** Select columns that uniquely identify records. Use composite keys if needed.

3. **Use Normalization:** Enable normalization options to handle variations in text (case, accents, punctuation)

4. **Set Appropriate Tolerance:** For numeric comparisons, consider setting a small tolerance (e.g., 0.01) to handle rounding differences

5. **Review Differences:** Always review the differences table before using the corrected dataset

6. **Handle Duplicates Wisely:** Choose the duplicate policy based on your use case:
   - Financial data: usually "keep_last" or "sum"
   - Measurements: usually "mean"
   - Status/text fields: "keep_last"

7. **Large Datasets:** For datasets over 100K rows, the process may take a few minutes. Be patient!

## Troubleshooting

**Error: "Duplicate keys found in GOLD dataset"**
- Solution: Clean your GOLD dataset to ensure unique keys
- Use pandas: `df.drop_duplicates(subset=['key_column'], keep='first')`

**Error: "Column not found"**
- Solution: Ensure column names match (case-insensitive after normalization)
- Check for extra spaces in column names

**Low Accuracy Score**
- Check if normalization options are appropriate for your data
- Verify that key columns are correctly selected
- Review a sample of differences to understand the issues

**Download Not Working**
- Ensure the comparison completed successfully
- Check browser console for errors
- Try downloading again or refresh the page

## Configuration

Environment variables (in `.env` file):

```bash
# Maximum file size for uploads
MAX_UPLOAD_MB=50

# Allowed file types
ACCURACY_ALLOWED_FILE_TYPES=.csv,.xlsx,.parquet

# Maximum number of rows to process
ACCURACY_MAX_ROWS=2000000

# Request timeout in seconds
ACCURACY_REQUEST_TIMEOUT=120

# Storage path for uploads and results
ACCURACY_STORAGE_PATH=./storage
```

## Support

For issues or questions:
1. Check this guide
2. Review the test files for examples
3. Check the main README.md
4. Open an issue on GitHub
