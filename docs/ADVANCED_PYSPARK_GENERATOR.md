# Advanced PySpark Code Generator

## Overview

The Advanced PySpark Code Generator is a new feature that allows users to automatically generate PySpark validation code by uploading a dataset. The system automatically inspects the dataset, infers the schema and statistics, generates a Data Specification Language (DSL), and produces ready-to-use PySpark code.

## Features

### 1. Automatic Dataset Inspection
- **Supported Formats**: CSV, JSON, JSONL, Parquet
- **File Size Limit**: 100MB
- **Automatic Detection**:
  - CSV delimiter (comma, semicolon, tab, pipe)
  - File encoding (UTF-8, Latin-1, Windows-1252)
  - Header presence
  - Schema and data types

### 2. Intelligent Schema Inference
For each column, the system automatically detects:
- Data type (integer, float, string, boolean, timestamp)
- Null ratio and null count
- Unique value ratio
- For numeric columns: min, max, mean, median, standard deviation
- For string columns: average length, max length, sample values

### 3. DSL Generation
The system generates a comprehensive Data Specification Language (DSL) that includes:
- Dataset metadata
- Schema definition with PySpark types
- Auto-generated validation rules:
  - Not-null constraints (for columns with <5% nulls)
  - Uniqueness constraints (for columns with >95% unique values)
  - Range validations (for numeric columns)
  - Custom validations (user-defined)

### 4. PySpark Code Generation
Generates production-ready PySpark code optimized for Google Colab with:
- Data loading with format-specific options
- Schema validation
- Data quality checks
- Summary reporting
- Copy to clipboard functionality
- Download as .py file

## Usage Guide

### Step 1: Access the Feature

From the homepage, click on the **"Generate PySpark Code"** dropdown and select **"Generate Advanced PySpark Code"**.

![Homepage with Dropdown](https://github.com/user-attachments/assets/518d4e1f-ff3a-431f-b56e-b52c2c6c096d)

### Step 2: Upload Dataset

1. Click "Choose File" to select your dataset
2. For CSV files, optionally configure:
   - Delimiter
   - Encoding
   - Header presence
3. Click "Inspect Dataset"

![Step 1 - Upload](https://github.com/user-attachments/assets/58384374-92cb-461a-871e-4dfe64de257d)

### Step 3: Review Metadata

Review the automatically detected:
- Dataset statistics (rows, columns, format)
- Data preview
- Column-level statistics
- Edit column properties:
  - Mark as required (not null)
  - Mark as unique
  - Set custom validations

### Step 4: Review and Edit DSL

Review the generated DSL in JSON format. You can:
- View the complete data specification
- Edit the DSL directly if needed
- Validate the JSON structure

### Step 5: Generate and Download Code

- View the generated PySpark code with syntax highlighting
- Copy code to clipboard
- Download as .py file
- Code is ready to use in Google Colab or any PySpark environment

## API Endpoints

### Dataset Inspection
```http
POST /api/datasets/inspect
Content-Type: multipart/form-data

Parameters:
- file: Dataset file (required)
- delimiter: CSV delimiter (optional)
- encoding: File encoding (optional)
- header: Has header (true/false, optional)
- sample_size: Sample size for statistics (optional, default: 10000)
```

### DSL Generation
```http
POST /api/datasets/generate-dsl
Content-Type: application/json

Body:
{
  "metadata": {...},
  "user_edits": {...}
}
```

### PySpark Code Generation
```http
POST /api/datasets/generate-pyspark
Content-Type: application/json

Body:
{
  "dsl": {...}
}
```

## Technical Details

### Backend Components

1. **Dataset Inspector** (`src/dataset_inspector/inspector.py`)
   - Handles CSV, Parquet, and JSON files
   - Performs automatic schema inference
   - Calculates column-level statistics
   - Detects encoding and delimiters

2. **DSL Generator** (`src/dataset_inspector/dsl_generator.py`)
   - Converts metadata to DSL format
   - Auto-generates validation rules
   - Supports user customizations

3. **Routes** (`src/dataset_inspector/routes.py`)
   - REST API endpoints
   - File upload handling
   - Security validations

### Frontend Components

1. **PySparkDropdown** (`frontend/src/components/PySparkDropdown.js`)
   - Dropdown menu component
   - Follows Data Accuracy dropdown pattern
   - Accessible and keyboard-navigable

2. **AdvancedPySparkGenerator** (`frontend/src/pages/AdvancedPySparkGenerator.js`)
   - Multi-step wizard interface
   - File upload with validation
   - Interactive metadata editing
   - Code viewer with syntax highlighting

## Security Considerations

- Maximum file size: 100MB
- Allowed file extensions: .csv, .json, .jsonl, .parquet
- Secure filename handling (prevents path traversal)
- Temporary file cleanup
- No persistent storage of uploaded data

## Testing

Run the test suite:

```bash
# Backend tests
python -m pytest tests/test_dataset_inspector.py tests/test_dsl_generator.py

# Frontend tests
cd frontend
npm test -- PySparkDropdown.test.js
```

## Examples

### Example 1: CSV with Customer Data

Input: `customers.csv`
```csv
id,name,age,email,score
1,Alice,25,alice@example.com,85.5
2,Bob,30,bob@example.com,90.0
```

Generated DSL includes:
- `id`: long type, not null, unique
- `name`: string type
- `age`: long type with range [25, 30]
- `email`: string type
- `score`: double type with range [85.5, 90.0]

### Example 2: Parquet with Transaction Data

Input: `transactions.parquet`

The system automatically:
1. Detects Parquet format
2. Reads schema from Parquet metadata
3. Analyzes data statistics
4. Generates appropriate PySpark code

## Future Enhancements

- Support for Delta Lake format
- Advanced transformations (e.g., column derivations)
- Custom validation rules builder
- Integration with data quality metrics dashboard
- Support for incremental data validation
- Export DSL in YAML format

## Contributing

When contributing to this feature:
1. Maintain backward compatibility with existing DSL format
2. Add tests for new functionality
3. Update this documentation
4. Follow the existing code style and patterns

## License

This feature is part of DataForgeTest and follows the project's license.
