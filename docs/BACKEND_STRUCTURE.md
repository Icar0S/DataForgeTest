# Backend Structure Documentation

This document describes the organization of the backend Python code.

## Directory Structure

```
/
├── src/                    # Main backend source code
│   ├── api.py             # Flask API entry point
│   ├── accuracy/          # Data accuracy validation
│   │   ├── config.py
│   │   ├── processor.py
│   │   └── routes.py
│   ├── chatbot/           # Interactive chatbot for data quality rules
│   │   ├── main.py
│   │   ├── questions.py
│   │   └── answers.py
│   ├── code_generator/    # PySpark code generation
│   │   └── pyspark_generator.py
│   ├── dsl_parser/        # DSL (Domain Specific Language) parsing
│   │   └── generator.py
│   ├── gold/              # GOLD dataset testing
│   │   ├── config.py
│   │   ├── processor.py
│   │   ├── routes.py
│   │   └── services/      # ✨ Business logic layer
│   │       ├── file_processor.py
│   │       └── serialization_utils.py
│   ├── metrics/           # Data quality metrics
│   │   ├── config.py
│   │   ├── processor.py
│   │   ├── routes.py
│   │   └── services/      # ✨ Metric calculation layer
│   │       ├── completeness.py
│   │       ├── consistency.py
│   │       ├── file_reader.py
│   │       ├── uniqueness.py
│   │       └── validity.py
│   ├── rag/               # RAG (Retrieval-Augmented Generation) system
│   │   ├── (Simple & Full implementations)
│   │   └── README.md
│   └── synthetic/         # Synthetic data generation
│       ├── config.py
│       ├── generator.py
│       ├── routes.py
│       └── validators.py
│
├── tests/                 # Automated test suite
│   ├── test_accuracy_*.py          # Accuracy module tests
│   ├── test_code_quality.py        # Code quality validation tests
│   ├── test_connectivity.py        # Frontend-backend connectivity tests
│   ├── test_generator.py           # DSL generation tests
│   ├── test_gold.py                # GOLD module tests
│   ├── test_improved_chat.py       # Chat functionality tests
│   ├── test_metrics.py             # Metrics module tests
│   ├── test_pyspark_generator.py   # PySpark code generation tests
│   ├── test_rag_*.py               # RAG system tests
│   └── test_synthetic_backend.py   # Synthetic data tests
│
└── utilities/             # Development and maintenance utilities
    ├── clean_knowledge_base.py
    ├── debug_config.py
    ├── debug_flask_vs_direct.py
    ├── debug_rag.py
    ├── enhance_knowledge_base.py
    ├── fix_rag_chunks.py
    └── sample_answers.py
```

## Module Descriptions

### src/api.py
Main Flask application entry point. Registers all blueprints and handles CORS.

### src/gold/
GOLD dataset testing feature for data cleaning and validation.
- `routes.py` - Flask blueprint with API endpoints
- `processor.py` - Data processing utilities
- `config.py` - Configuration management
- `services/` - **Business logic layer**
  - `file_processor.py` - CSV/Excel/Parquet file processing
  - `serialization_utils.py` - JSON serialization helpers

### src/metrics/
Data quality metrics calculation.
- `routes.py` - Flask blueprint with API endpoints
- `processor.py` - Metric orchestration
- `config.py` - Configuration management
- `services/` - **Metric calculation layer**
  - `file_reader.py` - Robust file reading utilities
  - `completeness.py` - Completeness metric calculations
  - `uniqueness.py` - Uniqueness metric calculations
  - `validity.py` - Validity metric calculations
  - `consistency.py` - Consistency metric calculations

### src/accuracy/
Data accuracy validation and correction.
- `routes.py` - Flask blueprint with API endpoints
- `processor.py` - Data comparison and normalization logic
- `config.py` - Configuration management

### src/synthetic/
Synthetic data generation using LLM.
- `routes.py` - Flask blueprint with API endpoints
- `generator.py` - Data generation logic
- `validators.py` - Validation utilities
- `config.py` - Configuration management

### src/chatbot/
Interactive chatbot that guides users through defining data quality rules.
- `main.py` - Main chatbot logic
- `questions.py` - Question templates
- `answers.py` - Answer validation

### src/code_generator/
Generates executable PySpark code from DSL definitions.
- `pyspark_generator.py` - Main code generation logic

### src/dsl_parser/
Parses user answers and generates DSL (Domain Specific Language) for data quality rules.
- `generator.py` - DSL generation logic

### src/rag/
RAG (Retrieval-Augmented Generation) system for intelligent documentation access.
See [src/rag/README.md](src/rag/README.md) for detailed documentation.

## Running the Backend

### Development Mode

```bash
cd src
python api.py
```

The API will be available at `http://localhost:5000`

### Production Mode

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=production

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.api:app
```

## API Endpoints

### Main Chatbot API
- `GET /` - Health check
- `POST /ask` - Process user answers and generate DSL/PySpark code

### GOLD Dataset API
- `GET /api/gold/health` - Health check
- `POST /api/gold/upload` - Upload dataset file
- `POST /api/gold/clean` - Clean dataset with options
- `GET /api/gold/status` - Get processing status
- `GET /api/gold/report` - Get cleaning report
- `GET /api/gold/download/<session_id>/<filename>` - Download cleaned file

### Metrics API
- `GET /api/metrics/health` - Health check
- `POST /api/metrics/upload` - Upload dataset file
- `POST /api/metrics/analyze` - Analyze dataset and generate metrics
- `GET /api/metrics/report?sessionId=<id>` - Retrieve report

### Accuracy API
- `GET /api/accuracy/health` - Health check
- `POST /api/accuracy/upload/gold` - Upload GOLD dataset
- `POST /api/accuracy/upload/target` - Upload target dataset
- `POST /api/accuracy/compare` - Compare and generate corrections
- `GET /api/accuracy/report/<session_id>` - Get comparison report
- `GET /api/accuracy/download/<session_id>/<filename>` - Download results

### Synthetic Data API
- `GET /api/synthetic/health` - Health check
- `POST /api/synthetic/generate` - Generate synthetic data

### RAG System API
- `POST /api/rag/chat` - Chat with AI assistant
- `GET /api/rag/chat` - Stream chat response
- `POST /api/rag/upload` - Upload documentation
- `GET /api/rag/sources` - List documents
- `DELETE /api/rag/sources/<id>` - Delete document
- `GET /api/rag/health` - RAG health check

## Testing

Run all tests:
```bash
python -m pytest tests/ -v
```

Run specific test file:
```bash
python -m pytest tests/test_rag_integration.py -v
```

## Code Quality

Check code quality with pylint:
```bash
pylint src/**/*.py
```

## Environment Variables

Create a `.env` file in the project root:

```env
# RAG Configuration
VECTOR_STORE_PATH=./storage/vectorstore
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=4
MAX_UPLOAD_MB=10

# For Full RAG with LLM (optional)
LLM_API_KEY=your-api-key
LLM_MODEL=claude-3-haiku-20240307
EMBED_MODEL=text-embedding-3-small
```

## Development Guidelines

1. **Code Style**: Follow PEP 8
2. **Type Hints**: Use type hints where applicable
3. **Docstrings**: Document all public functions and classes
4. **Error Handling**: Use try-except blocks appropriately
5. **Testing**: Write tests for new features
6. **Git**: Create feature branches, not direct commits to main

## Utilities

Development utilities are in the `utilities/` folder. These are helper scripts for debugging and maintenance, not part of the automated test suite.

See [utilities/README.md](utilities/README.md) for details.

## Common Tasks

### Add a new data quality rule type
1. Update `src/dsl_parser/generator.py`
2. Update `src/code_generator/pyspark_generator.py`
3. Add tests in `tests/test_generator.py`

### Add new RAG functionality
1. Update appropriate files in `src/rag/`
2. Add tests in `tests/test_rag_*.py`
3. Update `src/rag/README.md`

### Debug RAG issues
1. Use `utilities/debug_rag.py` to check system state
2. Use `utilities/debug_config.py` to verify paths
3. Use `utilities/fix_rag_chunks.py` to rebuild chunks

## Frontend Integration

The frontend (React) is in the `frontend//` directory and communicates with this backend via REST API.

Frontend makes requests to:
- `/ask` - For chatbot interactions
- `/api/rag/*` - For RAG system interactions

CORS is enabled for development.
