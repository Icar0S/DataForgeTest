# DataForgeTest

> **Advanced Data Quality Testing Platform with AI-Powered Synthetic Data Generation**

DataForgeTest is a comprehensive solution for automating data quality testing in Big Data environments. It combines Large Language Models (LLMs) with advanced data processing capabilities to generate synthetic datasets, validate data accuracy, and create intelligent testing workflows for scalable data systems.

<div align="center">
  <img width="1024" height="1024" alt="DataForgeTest Logo" src="https://github.com/user-attachments/assets/f17fd7ad-e9e9-464a-a55b-5d80af8ec578" />
</div>

## 🚀 Key Features

- **🤖 AI-Powered Synthetic Data Generation** - Create realistic datasets using LLMs with 14+ data types
- **📊 Data Accuracy Validation** - Compare and correct datasets using GOLD reference standards  
- **💬 Intelligent RAG Support System** - Chat with documentation using retrieval-augmented generation
- **⚡ PySpark Code Generation** - Automated generation of data quality validation scripts
- **🌐 Modern Web Interface** - React-based frontend with responsive design and dark theme
- **🔧 RESTful API Architecture** - Modular Flask backend with comprehensive error handling

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Features Overview](#-features-overview)
- [API Reference](#-api-reference)
- [Configuration](#-configuration)
- [Development](#-development)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Contributing](#-contributing)


## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control

### Automated Setup (Windows)

**🎯 First Time Setup**
```bash
setup_start.bat
```
- Installs all dependencies
- Configures environment
- Starts services
- Opens browser automatically

**⚡ Daily Development**
```bash
dev_start.bat
```
- Quick service startup
- No dependency checks
- Optimized for development

### Manual Setup

1. **Clone Repository**
```bash
git clone https://github.com/Icar0S/DataForgeTest.git
cd DataForgeTest
```

2. **Backend Setup**
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment (copy from .env.example)
cp .env.example .env
# Edit .env with your configuration
```

3. **Frontend Setup**
```bash
cd frontend/frontend
npm install
```

4. **Start Services**

Terminal 1 (Backend):
```bash
cd src
python api.py
```

Terminal 2 (Frontend):
```bash
cd frontend/frontend
npm start
```

**🌐 Access Points:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/docs

## 🎯 Features Overview

### 1. 🤖 PySpark Code Generation (QA Checklist)

Interactive chat interface for generating PySpark data quality validation code through natural language conversations.

**Key Features:**
- **Full-screen responsive chat interface** (mobile → desktop)
- **Auto-scrolling message area** with loading indicators
- **Multi-line message input** with keyboard shortcuts
- **Real-time streaming responses** via EventSource
- **Accessible design** with focus management and ARIA labels

**Keyboard Shortcuts:**
- `Enter` - Send message
- `Shift + Enter` - New line in message
- `Tab` - Navigate interactive elements

**API Integration:**
- Uses streaming endpoint: `GET /api/rag/chat?message=<query>`

### 2. 🎲 Synthetic Dataset Generation

LLM-powered synthetic data generation supporting realistic datasets with customizable schemas and multiple output formats.

**Supported Data Types:**
- **Primitives**: string, integer, float, boolean
- **Date/Time**: date, datetime with custom ranges
- **Semantic**: email, phone, address, product_name, price, uuid
- **Advanced**: category (with weights), custom_pattern (regex)

**Output Formats**: CSV, XLSX, JSON, Parquet

**Capabilities:**
- Up to **1,000,000 rows** per dataset
- Up to **50 columns** per schema
- **Preview mode** (50 rows) for quick validation
- **Batch processing** with progress tracking
- **Type validation** and coercion
- **Uniqueness constraints**
- **Null value control** (percentage-based)
- **Locale-aware generation** (default: pt_BR)

**Performance Benchmarks:**
- Small datasets (< 1K rows): 5-15 seconds
- Medium datasets (1K-50K rows): 1-5 minutes  
- Large datasets (50K-1M rows): 10-60 minutes

**Example Schema:**
```json
{
  "schema": {
    "columns": [
      {"name": "product_id", "type": "uuid", "options": {"unique": true}},
      {"name": "name", "type": "product_name", "options": {}},
      {"name": "price", "type": "price", "options": {"min": 10, "max": 9999, "decimals": 2}},
      {"name": "category", "type": "category", "options": {
        "categories": ["Electronics", "Clothing", "Food", "Books"]
      }}
    ]
  },
  "rows": 1000,
  "fileType": "csv"
}
```

### 3. 🎯 Data Accuracy Validation

Compare and correct datasets using GOLD reference standards with automated normalization and intelligent difference detection.

**Key Features:**
- **Multi-format support**: CSV, XLSX, Parquet uploads
- **Smart column mapping**: Define key columns (identifiers) and value columns (data to compare)
- **Automatic normalization**:
  - Column names → snake_case
  - Key normalization (trim, lowercase, accent/punctuation removal)
  - Numeric coercion (comma→decimal, thousands separator removal)
- **Duplicate handling**:
  - GOLD: Error on duplicates
  - TARGET: Configurable policies (keep_last, sum, average)
- **Tolerance-based comparison**: Define numeric comparison tolerance
- **Comprehensive reporting**:
  - Accuracy metrics with precision/recall
  - Paginated difference tables
  - Downloadable reports (CSV, JSON)

**Workflow:**
1. Upload GOLD dataset (trusted reference)
2. Upload TARGET dataset (data to validate)  
3. Map key columns (identifiers) and value columns
4. Configure normalization and tolerance options
5. Execute comparison and download corrected dataset

**Supported Files**: Up to 50MB, 2M rows, CSV/XLSX/Parquet formats

### 4. 💬 Intelligent RAG Support System

AI-powered documentation chat system with retrieval-augmented generation for contextual support and guidance.

**Features:**
- **Smart document search**: Keyword-based retrieval with relevance scoring
- **Contextual responses**: Structured answers based on query type
- **Streaming chat interface**: Real-time response generation
- **Document management**: Upload, index, and manage documentation
- **Multiple implementations**:
  - **Simple RAG**: Keyword-based search (default, no API key required)
  - **Full RAG**: LLM-powered with Claude Sonnet (requires API key)

**Quick Test:**
```bash
# Test RAG system functionality
python tests/test_rag_integration.py
python tests/test_rag_api.py

# Full system diagnostics  
python tests/test_rag_diagnostics.py
```

**Enable Full AI Mode:**
1. Add API key to `.env`: `LLM_API_KEY=your-anthropic-key`
2. Install: `pip install llama-index-llms-anthropic`
3. Restart backend

**Current Status**: ✅ Simple RAG active with 6 documents, structured responses

## 🏗️ Architecture Overview

DataForgeTest follows a modern microservices architecture with clear separation between frontend and backend components.

<div align="center">
  <img width="1918" height="896" alt="System Architecture" src="https://github.com/user-attachments/assets/a5c59bb3-049d-4417-8036-71b9f10e0b25" />
</div>

### Core Components

**🎨 Frontend (React + TypeScript)**
- Modern responsive UI with dark theme
- Real-time streaming chat interfaces
- File upload with progress tracking
- Interactive data visualization
- Accessibility-focused design

**🔧 Backend (Python + Flask)**
- Modular blueprint architecture
- RESTful API with comprehensive error handling
- LLM integration (Anthropic Claude)
- Multi-format file processing
- Automated data validation pipelines

**📁 Project Structure**
```
DataForgeTest/
├── frontend/frontend/          # React application
│   ├── src/components/        # UI components
│   ├── src/pages/            # Application pages
│   └── public/               # Static assets
├── src/                      # Python backend
│   ├── api.py               # Main Flask application
│   ├── chatbot/             # PySpark code generation
│   ├── synthetic/           # Synthetic data generation
│   ├── accuracy/            # Data accuracy validation
│   └── rag/                # RAG support system
├── docs/                    # Comprehensive documentation
├── tests/                   # Test suites
└── storage/                 # Data storage
```

## 📡 API Reference

### Core Endpoints

**Main Application**
- `GET /` - Health check and system status
- `POST /ask` - Process chatbot requests and generate PySpark code

**Synthetic Data Generation**
- `POST /api/synth/preview` - Generate dataset preview (max 100 rows)
- `POST /api/synth/generate` - Generate full synthetic dataset
- `GET /api/synth/download/:session/:file` - Download generated files
- `GET /api/synth/health` - Service health check

**Data Accuracy Validation**  
- `POST /api/accuracy/upload?role=gold|target` - Upload datasets
- `POST /api/accuracy/compare-correct` - Compare and correct datasets
- `GET /api/accuracy/download/:session/:file` - Download results
- `GET /api/accuracy/health` - Service health check

**RAG Support System**
- `POST /api/rag/chat` - Send chat messages
- `GET /api/rag/chat?message=query` - Streaming chat (EventSource)
- `POST /api/rag/search` - Search documentation  
- `POST /api/rag/upload` - Upload documentation
- `GET /api/rag/sources` - List indexed documents
- `DELETE /api/rag/sources/:id` - Remove documents
- `GET /api/rag/health` - RAG system health

## ⚙️ Configuration

### Environment Variables

Create `.env` file (copy from `.env.example`):

```bash
# LLM Configuration (Anthropic Claude)
LLM_API_KEY=your-anthropic-api-key-here
LLM_MODEL=claude-3-haiku-20240307

# RAG System
VECTOR_STORE_PATH=./storage/vectorstore
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=4
MAX_UPLOAD_MB=10

# Synthetic Data Generation
SYNTH_STORAGE_PATH=./storage/synth
SYNTH_MAX_ROWS=1000000
SYNTH_REQUEST_TIMEOUT=300
SYNTH_MAX_MEM_MB=2048

# Data Accuracy
ACCURACY_STORAGE_PATH=./storage/accuracy
ACCURACY_MAX_UPLOAD_MB=50
ACCURACY_MAX_ROWS=2000000
ACCURACY_REQUEST_TIMEOUT=120

# Flask Settings
FLASK_ENV=development
FLASK_DEBUG=True
```

### Supported Data Quality Rules

The PySpark code generator supports comprehensive data quality validation:

**Schema Validation**
- Column name and type verification
- Header presence validation

**Data Integrity**
- `not_null`: Ensure no missing values
- `uniqueness`: Guarantee unique values/combinations

**Value Constraints**
- `format`: Validate data formats (dates, emails, etc.)
- `range`: Check numeric ranges
- `in_set`: Validate against predefined values
- `regex`: Pattern matching validation
- `value_distribution`: Frequency analysis

## 🛠️ Development

### Development Setup

```bash
# Clone and setup
git clone https://github.com/Icar0S/DataForgeTest.git
cd DataForgeTest

# Backend development
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend development  
cd frontend/frontend
npm install
npm start
```

### Code Quality

```bash
# Python linting
pylint src/**/*.py

# Frontend testing
cd frontend/frontend
npm test

# Type checking
npm run type-check
```

### Backend Architecture

**Modular Blueprint Design:**
- `api.py` - Main Flask application with CORS support
- `synthetic/` - LLM-powered synthetic data generation
- `accuracy/` - Dataset comparison and correction
- `rag/` - RAG documentation system (Simple + Full implementations)
- `chatbot/` - PySpark code generation from natural language

**Key Design Patterns:**
- Configuration via environment variables
- Comprehensive error handling with structured responses
- Session-based file management
- Streaming responses for real-time feedback
- Modular validators and processors

## 🧪 Testing

### Automated Test Suites

```bash
# Run all tests
python -m pytest tests/ -v

# Specific test categories
python tests/test_rag_integration.py      # RAG system tests
python tests/test_rag_api.py             # API endpoint tests  
python tests/test_rag_diagnostics.py     # System diagnostics

# Data accuracy tests (31 tests total)
python -m pytest tests/test_accuracy*.py -v                    # All accuracy tests
python tests/test_accuracy_backend.py -v                       # Backend unit tests (9 tests)
python tests/test_accuracy_integration.py -v                   # Basic integration (4 tests)
python tests/test_accuracy_integration_robust.py -v            # Robust integration (18 tests)

# Frontend tests
cd frontend/frontend
npm test
```

### Manual Testing Scripts

```bash
# Test RAG improvements
python test_improved_rag.py

# Test synthetic data generation
python test_csv_download.py

# Test system connectivity
python tests/test_connectivity.py
```

### Test Coverage

**Backend Components:**
- ✅ RAG system (14/14 tests passing, 100% success rate)
- ✅ API endpoints (all endpoints functional)
- ✅ Synthetic data generation (CSV download working)
- ✅ **Data accuracy validation (31/31 tests passing, 100% success rate)**
  - Backend unit tests: 9 tests (normalization, comparison, tolerance)
  - Basic integration: 4 tests (upload/compare/download workflows)
  - Robust integration: 18 tests (multi-format, multi-column, edge cases, security)
- ✅ Error handling and edge cases

**Data Accuracy Test Coverage:**
- File formats: CSV, XLSX, Parquet ✓
- Multi-column keys and values ✓
- Normalization options (accents, punctuation, case) ✓
- Numeric formats (European/US) ✓
- Duplicate policies (keep_last, sum, mean) ✓
- Large datasets (1000+ rows) ✓
- Security (path traversal, access control) ✓
- Edge cases (empty data, special characters, missing columns) ✓

**Frontend Components:**
- ✅ React component rendering
- ✅ Chat interface functionality
- ✅ File upload workflows
- ✅ API integration points
- ✅ Responsive design

## 📚 Documentation

### Comprehensive Guides

**Core Documentation:**
- [`docs/BACKEND_STRUCTURE.md`](docs/BACKEND_STRUCTURE.md) - Backend architecture guide
- [`docs/IMPLEMENTATION_SUMMARY.md`](docs/IMPLEMENTATION_SUMMARY.md) - Complete feature overview
- [`docs/ACCEPTANCE_CHECKLIST.md`](docs/ACCEPTANCE_CHECKLIST.md) - QA validation checklist
- [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) - **Common issues and solutions**

**Feature-Specific:**
- [`docs/SYNTHETIC_DATASET_FEATURE.md`](docs/SYNTHETIC_DATASET_FEATURE.md) - Synthetic data generation
- [`docs/RAG_TROUBLESHOOTING.md`](docs/RAG_TROUBLESHOOTING.md) - RAG system guide
- [`docs/RAG_TEST_RESULTS.md`](docs/RAG_TEST_RESULTS.md) - Test results analysis

**Testing Documentation:**
- [`tests/README_TESTS.md`](tests/README_TESTS.md) - Test suite overview
- [`docs/RAG_QUICK_REFERENCE.md`](docs/RAG_QUICK_REFERENCE.md) - Quick reference guide

### API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:5000/docs (when running)
- **Postman Collection**: Available in `/docs/api/`

## 🎯 Use Cases

**Data Engineering Teams:**
- Generate realistic test datasets for pipeline validation
- Automate data quality rule creation
- Compare production vs. staging datasets
- Create comprehensive PySpark validation scripts

**QA/Testing Teams:**
- Generate edge case datasets for testing
- Validate data accuracy across environments
- Create automated data quality checks
- Document and track data quality metrics

**Data Scientists:**
- Create synthetic datasets for model training
- Validate data preprocessing pipelines
- Compare dataset versions and track changes
- Generate documentation-aware support queries

## 🚀 Deployment

### Production Deployment

```bash
# Backend (using gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.api:app

# Frontend (build and serve)
cd frontend/frontend
npm run build
# Serve build/ directory with your preferred web server
```

### Docker Support (Coming Soon)

```bash
# Will be available in future releases
docker-compose up --build
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Run tests**: `python -m pytest tests/ -v`
4. **Commit changes**: `git commit -m 'Add amazing feature'`
5. **Push to branch**: `git push origin feature/amazing-feature`
6. **Open Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript/React
- Add tests for new features
- Update documentation
- Ensure all tests pass

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Anthropic Claude** for LLM capabilities
- **Apache Spark** for big data processing
- **React Community** for frontend framework
- **Flask Community** for backend framework

---

<div align="center">
  <p><strong>Built with ❤️ for the Data Engineering Community</strong></p>
  <p>
    <a href="https://github.com/Icar0S/DataForgeTest/issues">Report Bug</a>
    ·
    <a href="https://github.com/Icar0S/DataForgeTest/issues">Request Feature</a>
    ·
    <a href="docs/">Documentation</a>
  </p>
</div>
