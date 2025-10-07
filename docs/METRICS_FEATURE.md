# Dataset Metrics Feature

## Overview

The Dataset Metrics feature provides comprehensive data quality analysis for uploaded datasets. It generates detailed metrics and visualizations to help users understand and improve their data quality.

## Features

### Core Metrics

The system calculates four main categories of data quality metrics:

#### 1. Completeness
- **Overall Completeness**: Percentage of non-null cells across the entire dataset
- **Per-Column Completeness**: Individual completeness rates for each column
- Tracks missing values and filled cells

#### 2. Uniqueness
- **Overall Uniqueness**: Percentage of unique rows in the dataset
- **Per-Column Uniqueness**: Individual uniqueness rates for each column
- Identifies duplicate rows

#### 3. Validity
- **Overall Validity**: Percentage of valid values across the dataset
- **Per-Column Validity**: Individual validity rates for each column
- Detects invalid data types (e.g., infinity in numeric columns, empty strings)

#### 4. Consistency
- **Overall Consistency**: Average consistency score across all columns
- **Per-Column Consistency**: Individual consistency rates based on data type patterns
- Evaluates format uniformity and pattern consistency

### Quality Score

The system generates an **Overall Quality Score** (0-100%) using a weighted average:
- Completeness: 30%
- Uniqueness: 20%
- Validity: 30%
- Consistency: 20%

### Recommendations

Based on the metrics, the system provides actionable recommendations:
- **High severity**: Quality issues requiring immediate attention (e.g., completeness < 90%, validity < 95%)
- **Medium severity**: Quality issues that should be addressed (e.g., duplicates, consistency < 80%)
- **Low severity**: Minor quality improvements

## API Endpoints

### `POST /api/metrics/upload`
Upload a dataset file for analysis.

**Request:**
- Form-data with `file` parameter
- Supported formats: CSV, XLSX, XLS, Parquet
- Max file size: 50MB (configurable)

**Response:**
```json
{
  "sessionId": "uuid",
  "columns": ["col1", "col2", ...],
  "sample": [{ ... }, ...],
  "format": "csv",
  "rows": 100
}
```

### `POST /api/metrics/analyze`
Analyze uploaded dataset and generate quality metrics.

**Request:**
```json
{
  "sessionId": "uuid"
}
```

**Response:**
```json
{
  "overall_quality_score": 95.5,
  "metrics": {
    "completeness": { ... },
    "uniqueness": { ... },
    "validity": { ... },
    "consistency": { ... },
    "dataset_info": { ... }
  },
  "recommendations": [ ... ],
  "generated_at": "2024-01-01T00:00:00"
}
```

### `GET /api/metrics/report?sessionId=...`
Retrieve previously generated quality report.

**Response:**
Same as analyze endpoint

### `GET /api/metrics/health`
Health check endpoint.

**Response:**
```json
{
  "ok": true,
  "service": "metrics",
  "status": "running"
}
```

## Frontend Interface

### Upload Screen
- Drag-and-drop file upload
- File selection via button
- Supported format validation
- File size validation

### Results Dashboard

#### Quality Score Card
- Large display of overall quality score
- Color-coded rating (green: ≥90%, yellow: 70-89%, red: <70%)
- Quality assessment message

#### Metrics Cards
Four cards displaying:
- Completeness percentage and counts
- Uniqueness percentage and duplicate info
- Validity percentage and invalid counts
- Consistency percentage and description

#### Dataset Information
- Total rows
- Total columns
- Memory usage

#### Recommendations Panel
- List of recommendations sorted by severity
- Color-coded severity indicators
- Category tags
- Actionable messages

## Usage Example

### Python (Backend)
```python
import requests

# Upload file
with open('dataset.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/metrics/upload',
        files={'file': f}
    )
    data = response.json()
    session_id = data['sessionId']

# Analyze dataset
response = requests.post(
    'http://localhost:5000/api/metrics/analyze',
    json={'sessionId': session_id}
)
report = response.json()

print(f"Quality Score: {report['overall_quality_score']}%")
print(f"Completeness: {report['metrics']['completeness']['overall_completeness']}%")
```

### Frontend (React)
```javascript
// Upload file
const formData = new FormData();
formData.append('file', file);

const uploadResponse = await fetch('/api/metrics/upload', {
  method: 'POST',
  body: formData,
});
const { sessionId } = await uploadResponse.json();

// Analyze dataset
const analyzeResponse = await fetch('/api/metrics/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ sessionId }),
});
const report = await analyzeResponse.json();
```

## Testing

### Backend Tests
Run the complete test suite:
```bash
pytest tests/test_metrics.py -v
```

**Test Coverage:**
- 11/11 tests passing
- Completeness metrics calculation
- Uniqueness metrics calculation
- Validity metrics calculation
- Consistency metrics calculation
- Quality report generation
- API endpoint functionality
- File upload validation

### Frontend Tests
Run the frontend tests:
```bash
cd frontend/frontend
npm test -- DatasetMetrics.test.js
```

**Test Coverage:**
- 13/13 tests passing
- Component rendering
- File upload functionality
- Error handling
- Results display
- User interactions
- Accessibility features

## Configuration

Environment variables:
- `METRICS_STORAGE_PATH`: Path to store uploaded files (default: `./uploads/metrics`)
- `MAX_UPLOAD_MB`: Maximum file size in MB (default: `50`)
- `METRICS_SAMPLE_SIZE`: Number of rows in preview (default: `10`)

## Data Quality Best Practices

The metrics feature aligns with industry-standard data quality dimensions:

1. **Completeness**: Measures data availability
2. **Uniqueness**: Identifies redundancy
3. **Validity**: Ensures data correctness
4. **Consistency**: Verifies format uniformity

## Screenshots

### Dropdown Menu with Dataset Metrics Option
![Dropdown Menu](https://github.com/user-attachments/assets/67ca675e-ccdb-431e-a38b-2e92817d409a)

### Dataset Metrics Upload Page
![Upload Page](https://github.com/user-attachments/assets/62434d70-fe4d-40ae-a20d-ec174fc56701)

## Future Enhancements

- [ ] Export reports to PDF/Excel
- [ ] Historical quality tracking over time
- [ ] Custom quality rules and thresholds
- [ ] Data profiling (min, max, distributions)
- [ ] Column-level data type recommendations
- [ ] Integration with data catalogs
- [ ] Automated quality alerts
- [ ] Comparative analysis between datasets
