# Generate Synthetic Dataset Feature

## Overview

The Generate Synthetic Dataset feature enables users to create realistic synthetic datasets using AI-powered generation (LLM). This feature supports multiple data types, customizable schemas, and various output formats.

## Features

### Supported Column Types
- **Primitive Types**: string, integer, float, boolean
- **Date/Time**: date, datetime
- **Semantic Types**: email, phone, address, product_name, price, uuid
- **Advanced**: category (with weighted options), custom_pattern

### Output Formats
- CSV (Comma-Separated Values)
- XLSX (Excel)
- JSON (or JSON Lines for large datasets)
- Parquet

### Capabilities
- Generate up to 1,000,000 rows per dataset
- Up to 50 columns per schema
- Preview mode (50 rows) for quick validation
- Batch generation with progress tracking
- Type validation and coercion
- Uniqueness constraints
- Null value percentage control
- Locale-aware generation (default: pt_BR)

## Configuration

### Backend Environment Variables

Add these to your `.env` file:

```bash
# LLM Configuration (shared with RAG)
LLM_API_KEY=your-anthropic-api-key-here
LLM_MODEL=claude-3-haiku-20240307

# Synthetic Dataset Generation Configuration
SYNTH_STORAGE_PATH=./storage/synth
SYNTH_MAX_ROWS=1000000
SYNTH_REQUEST_TIMEOUT=300
SYNTH_MAX_MEM_MB=2048
SYNTH_RATE_LIMIT=60
```

### Required Dependencies

Backend (Python):
```bash
pip install anthropic pandas numpy openpyxl pyarrow xlsxwriter python-dotenv
```

Frontend dependencies are already included in `package.json`.

## API Endpoints

### POST /api/synth/preview
Generate a preview of synthetic data (max 100 rows).

**Request Body:**
```json
{
  "schema": {
    "columns": [
      {
        "name": "id",
        "type": "integer",
        "options": { "min": 1, "max": 1000000, "unique": true }
      },
      {
        "name": "email",
        "type": "email",
        "options": {}
      },
      {
        "name": "created_at",
        "type": "datetime",
        "options": {
          "start": "2020-01-01",
          "end": "2025-12-31"
        }
      }
    ]
  },
  "rows": 50,
  "locale": "pt_BR",
  "seed": 42
}
```

**Response:**
```json
{
  "preview": [
    { "id": 1, "email": "user1@example.com", "created_at": "2024-03-15 10:30:00" },
    { "id": 2, "email": "user2@example.com", "created_at": "2024-06-20 14:45:00" }
  ],
  "columns": ["id", "email", "created_at"],
  "rows_generated": 50,
  "duration_sec": 2.5,
  "logs": ["Generated preview", "Coerced types for 50 records"]
}
```

### POST /api/synth/generate
Generate a full dataset and save to file.

**Request Body:**
```json
{
  "schema": { "columns": [...] },
  "rows": 10000,
  "fileType": "csv",
  "llmMode": "batched",
  "batchSize": 1000,
  "locale": "pt_BR",
  "seed": 42
}
```

**Response:**
```json
{
  "summary": {
    "rows": 10000,
    "cols": 3,
    "fileType": "csv",
    "durationSec": 45.2
  },
  "downloadUrl": "/api/synth/download/abc-123-def/dataset.csv",
  "logs": [
    "Generating 10000 rows in 10 batches of 1000...",
    "Batch 1/10: generating 1000 rows...",
    "Batch 1 complete: 1000/10000 total rows",
    ...
  ]
}
```

### GET /api/synth/download/:session_id/:filename
Download the generated dataset file.

### GET /api/synth/health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "Synthetic Data Generation service is running",
  "model": "claude-3-haiku-20240307",
  "max_rows": 1000000
}
```

## Usage Examples

### Example 1: Simple Product Catalog

```javascript
{
  "schema": {
    "columns": [
      { "name": "product_id", "type": "uuid", "options": { "unique": true } },
      { "name": "name", "type": "product_name", "options": {} },
      { "name": "price", "type": "price", "options": { "min": 10, "max": 9999, "decimals": 2 } },
      { "name": "category", "type": "category", "options": {
          "categories": ["Electronics", "Clothing", "Food", "Books"]
        }
      },
      { "name": "in_stock", "type": "boolean", "options": {} }
    ]
  },
  "rows": 1000,
  "fileType": "csv"
}
```

### Example 2: User Records with Dates

```javascript
{
  "schema": {
    "columns": [
      { "name": "user_id", "type": "integer", "options": { "min": 1, "max": 1000000, "unique": true } },
      { "name": "email", "type": "email", "options": {} },
      { "name": "phone", "type": "phone", "options": {} },
      { "name": "address", "type": "address", "options": {} },
      { "name": "signup_date", "type": "date", "options": {
          "start": "2020-01-01",
          "end": "2024-12-31"
        }
      }
    ]
  },
  "rows": 5000,
  "fileType": "xlsx"
}
```

### Example 3: Custom Pattern

```javascript
{
  "schema": {
    "columns": [
      { "name": "sku", "type": "custom_pattern", "options": {
          "description": "Product SKU in format ABC-1234-XYZ"
        }
      },
      { "name": "quantity", "type": "integer", "options": { "min": 0, "max": 1000 } }
    ]
  },
  "rows": 500,
  "fileType": "json"
}
```

## Performance Considerations

### Generation Time Estimates
- **Small datasets** (< 1,000 rows): 5-15 seconds
- **Medium datasets** (1,000 - 50,000 rows): 1-5 minutes
- **Large datasets** (50,000 - 1,000,000 rows): 10-60 minutes

*Note: Times vary based on LLM response speed, column complexity, and batch size.*

### Memory Usage
- Preview: < 10 MB
- CSV generation: ~50 MB per 100,000 rows
- XLSX generation: ~100 MB per 100,000 rows
- Parquet generation: ~30 MB per 100,000 rows (most efficient)

### Cost Optimization
1. Use smaller batch sizes (500-1000) for more consistent results
2. Use seed values for reproducibility
3. For large datasets (> 100,000 rows), use Parquet or CSV formats
4. Preview before generating large datasets
5. Consider using mock generation (no API key) for testing

## LLM Integration

The feature uses Anthropic's Claude API by default. The generator:
1. Builds a detailed prompt with schema constraints
2. Requests CSV-formatted data from the LLM
3. Parses and validates the response
4. Coerces types and enforces constraints
5. Retries on parse failures (up to 3 attempts)
6. Falls back to mock data if LLM is unavailable

### Fallback Mode (Mock Data)
If no API key is configured, the system generates simple mock data:
- Integers: Random values in specified range
- Floats/Prices: Random decimals in range
- Booleans: Random true/false
- Dates: Random dates in YYYY-MM-DD format
- Strings: Template format "mock_[column_name]_[row_index]"

## Testing

### Backend Tests
```bash
cd /home/runner/work/DataForgeTest/DataForgeTest
python -m pytest tests/test_synthetic_backend.py -v
```

### Frontend Tests
```bash
cd frontend/frontend
npm test -- GenerateDataset.test.js
```

## Limitations

- Maximum 1,000,000 rows per dataset
- Maximum 50 columns per schema
- Preview limited to 100 rows
- Request timeout: 300 seconds (configurable)
- LLM rate limits apply
- Large datasets may take significant time to generate

## Troubleshooting

### "Validation failed" error
- Check that all column names are unique
- Ensure required options are provided for each type
- Verify row count is within limits (1 - 1,000,000)

### "Parse error" or incomplete data
- The LLM may have generated malformed CSV
- The system will retry up to 3 times
- Consider using a smaller batch size
- Check the logs for specific error details

### Slow generation
- Large datasets take time; this is expected
- Use Parquet format for better performance
- Increase batch size for faster generation (but less consistency)
- Monitor the logs to see progress

### Out of memory
- Reduce batch size
- Use streaming formats (CSV, Parquet)
- Avoid XLSX for very large datasets (> 500,000 rows)

## Future Enhancements

- [ ] Support for more LLM providers (OpenAI, local models)
- [ ] Referential integrity (foreign keys between columns)
- [ ] Data quality injection (deliberate anomalies)
- [ ] Template library for common schemas
- [ ] Incremental generation with resume capability
- [ ] Real-time progress streaming
- [ ] Export to database directly
