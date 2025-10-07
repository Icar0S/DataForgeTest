# Test Dataset GOLD Feature

## Overview

The **Test Dataset GOLD** feature provides automated data cleaning and validation for single datasets. It applies industry-standard data quality improvements to transform raw datasets into clean, analysis-ready "GOLD" standard files.

## Features

### Supported File Formats
- **CSV** (.csv) - with automatic encoding and separator detection
- **Excel** (.xlsx, .xls) - full support for both formats
- **Parquet** (.parquet) - optimized columnar format

### Data Cleaning Operations

#### 1. Remove Empty Columns
Automatically removes columns that are 100% null or empty.

#### 2. Normalize Column Names
- Converts to lowercase
- Replaces spaces and hyphens with underscores
- Removes special characters
- Strips accents (e.g., "Año" → "ano")
- Handles duplicate names with suffixes (_2, _3, etc.)

#### 3. Trim Strings
- Removes leading and trailing whitespace
- Removes invisible characters (control chars, zero-width spaces)
- Converts empty strings to null

#### 4. Coerce Numeric Values
- Handles both US (1,234.56) and European (1.234,56) formats
- Removes thousands separators
- Converts string numbers to numeric types
- Best-effort conversion (non-numeric values remain unchanged)

#### 5. Parse Dates
- Attempts ISO 8601 format first
- Falls back to pandas datetime inference
- Non-fatal: returns original value if parsing fails
- Applies to columns where >50% of values parse successfully

#### 6. Remove Duplicate Rows (Optional)
- Disabled by default
- Removes exact duplicate rows when enabled

### Performance Features

#### Chunked Processing
- **CSV/Parquet**: Processes in configurable chunks (default: 200,000 rows)
- **Excel**: Loads entire file, processes in memory chunks
- Real-time progress tracking with phase indicators
- Optimized memory usage for large files

#### Progress Tracking
- Upload phase
- Analysis phase
- Cleaning phase (with chunk progress)
- Finalization phase

## API Endpoints

### `POST /api/gold/upload`
Upload a dataset file.

**Request:**
- Form-data with `file` parameter
- Max file size: 50MB (configurable via `MAX_UPLOAD_MB`)

**Response:**
```json
{
  "sessionId": "uuid",
  "datasetId": "uuid",
  "columns": ["col1", "col2", ...],
  "sample": [{ ... }, ...],
  "format": "csv|xlsx|xls|parquet"
}
```

### `POST /api/gold/clean`
Start cleaning process.

**Request:**
```json
{
  "sessionId": "string",
  "datasetId": "string",
  "options": {
    "dropEmptyColumns": true,
    "normalizeHeaders": true,
    "trimStrings": true,
    "coerceNumeric": true,
    "parseDates": true,
    "dropDuplicates": false,
    "chunksize": 200000
  }
}
```

**Response:**
```json
{
  "status": "completed",
  "progressUrl": "/api/gold/status?sessionId=...",
  "download": {
    "csv": "/api/gold/download/.../gold_clean.csv",
    "sameFormat": "/api/gold/download/.../gold_clean.xlsx"
  }
}
```

### `GET /api/gold/status?sessionId=...`
Get processing status.

**Response:**
```json
{
  "state": "running|completed|failed",
  "progress": {
    "current": 3,
    "total": 12,
    "phase": "cleaning"
  },
  "report": { ... }
}
```

### `GET /api/gold/report?sessionId=...`
Get cleaning report.

**Response:**
```json
{
  "rowsRead": 1000,
  "rowsWritten": 980,
  "columnsBefore": 15,
  "columnsAfter": 12,
  "removedColumns": ["empty_col1", "empty_col2"],
  "changedRows": {
    "trimStrings": 450,
    "coerceNumeric": 120,
    "parseDates": 80
  },
  "nullsPerColumn": {
    "before": { "col1": 10, "col2": 0 },
    "after": { "col1": 5, "col2": 0 }
  },
  "samplePreview": [{ ... }, ...],
  "startedAt": "2024-01-15T10:30:00Z",
  "finishedAt": "2024-01-15T10:30:45Z",
  "durationSec": 45.2
}
```

### `GET /api/gold/download/<session_id>/<filename>`
Download cleaned file.

**Supported files:**
- `gold_clean.csv` - Always available
- `gold_clean.xlsx` - For Excel uploads
- `gold_clean.parquet` - For Parquet uploads

### `GET /api/gold/health`
Health check endpoint.

## Configuration

### Environment Variables

```bash
# Storage path
GOLD_STORAGE_PATH=./storage/gold

# Maximum upload size (MB)
MAX_UPLOAD_MB=50

# Allowed file types (comma-separated)
GOLD_ALLOWED_FILE_TYPES=.csv,.xlsx,.xls,.parquet

# Warning threshold for large datasets (rows)
MAX_ROWS_WARN=500000

# Request timeout (seconds)
GOLD_REQUEST_TIMEOUT=300
```

### Default Configuration

```python
{
    "storage_path": "./storage/gold",
    "max_upload_mb": 50,
    "allowed_file_types": [".csv", ".xlsx", ".xls", ".parquet"],
    "max_rows_warn": 500000,
    "request_timeout": 300
}
```

## Usage Examples

### Frontend (React)

```javascript
// Upload file
const formData = new FormData();
formData.append('file', file);

const uploadRes = await fetch('/api/gold/upload', {
  method: 'POST',
  body: formData
});
const { sessionId } = await uploadRes.json();

// Start cleaning
const cleanRes = await fetch('/api/gold/clean', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sessionId,
    datasetId,
    options: {
      dropEmptyColumns: true,
      normalizeHeaders: true,
      trimStrings: true,
      coerceNumeric: true,
      parseDates: true,
      dropDuplicates: false
    }
  })
});

// Poll for status
const pollStatus = setInterval(async () => {
  const statusRes = await fetch(`/api/gold/status?sessionId=${sessionId}`);
  const status = await statusRes.json();
  
  if (status.state === 'completed') {
    clearInterval(pollStatus);
    // Show report and download buttons
  }
}, 1000);
```

### Backend (Python)

```python
from gold.routes import gold_bp
from api import app

# Register blueprint
app.register_blueprint(gold_bp)
```

## Performance Notes

### Small Files (< 10,000 rows)
- Processing time: 1-5 seconds
- Memory usage: < 100MB

### Medium Files (10,000 - 500,000 rows)
- Processing time: 5-30 seconds
- Memory usage: 100MB - 1GB

### Large Files (500,000+ rows)
- Processing time: 30 seconds - 5 minutes
- Memory usage: 1GB - 4GB
- Recommendation: Use CSV or Parquet for best performance

### Optimization Tips

1. **Use appropriate chunk size**: Larger chunks (500,000) for systems with more RAM
2. **Prefer Parquet** for very large datasets (faster I/O)
3. **Disable unused operations**: Turn off date parsing if not needed
4. **Monitor progress**: Use progress endpoint to track long-running operations

## Security

### Path Traversal Protection
- All file paths are validated
- Prevents `..` and directory traversal attempts
- Files are isolated per session

### File Validation
- Type checking by extension
- Size limits enforced
- Secure filename handling with `secure_filename()`

### Session Isolation
- Each upload gets unique session ID
- Files stored in isolated directories
- No cross-session access

## Troubleshooting

### "File type not allowed"
- Check file extension matches allowed types
- Ensure file is not corrupted

### "File size exceeds maximum"
- Increase `MAX_UPLOAD_MB` in environment
- Or split file into smaller chunks

### "Processing timeout"
- Increase `GOLD_REQUEST_TIMEOUT`
- Reduce chunk size for memory-constrained systems
- Use CSV/Parquet instead of Excel for large files

### Memory Issues
- Reduce `chunksize` option (default: 200,000)
- Close other applications
- Use server with more RAM

## Testing

Run the test suite:

```bash
# All GOLD tests
pytest tests/test_gold.py -v

# Specific test categories
pytest tests/test_gold.py::TestGoldProcessor -v  # Processor tests
pytest tests/test_gold.py::TestGoldAPI -v        # API tests
```

**Test Coverage:**
- 15/15 tests passing
- File upload validation
- Cleaning operations
- Chunked processing
- Report generation
- Download functionality
- Security (path traversal)

## UI Screenshots

### Homepage Dropdown Menu
![Dropdown Menu](https://github.com/user-attachments/assets/9c172c41-18bc-4f21-b1f3-11f8cf61acf0)

### Test Dataset GOLD Page
![GOLD Page](https://github.com/user-attachments/assets/639663b0-4056-4a06-a51a-86eb8e7de04a)

## Architecture

```
┌─────────────────┐
│   Frontend      │
│   React + UI    │
└────────┬────────┘
         │
         │ HTTP/REST
         ↓
┌─────────────────┐
│   Flask API     │
│   /api/gold/*   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐      ┌──────────────┐
│   Processor     │ ───► │   Storage    │
│   Cleaning      │      │   Session    │
│   Logic         │      │   Files      │
└─────────────────┘      └──────────────┘
```

## Future Enhancements

- [ ] Custom cleaning rules (regex-based)
- [ ] Data type inference and conversion
- [ ] Statistical outlier detection
- [ ] Column profiling (min, max, distribution)
- [ ] Export to multiple formats simultaneously
- [ ] Scheduling/batch processing
- [ ] Data quality scoring
- [ ] Integration with data catalogs
