# RAG System Test Suite

This directory contains comprehensive tests for the RAG (Retrieval-Augmented Generation) system to help diagnose and prevent connection issues.

## Test Files

### 1. `test_rag_integration.py`
**Purpose:** Test core RAG functionality and components

**Tests:**
- Configuration loading and validation
- RAG system initialization
- Document operations (add, search, retrieve)
- Chat engine operations
- Response format compatibility with frontend
- Storage and persistence

**Run:**
```bash
python tests/test_rag_integration.py
```

**Expected Output:**
```
✓ Config loaded: storage=storage/vectorstore, chunk_size=512
✓ RAG system initialized successfully
✓ Chat engine initialized successfully
...
Tests run: 16
Success rate: 100.0%
```

### 2. `test_rag_api.py`
**Purpose:** Test Flask API endpoints for RAG functionality

**Tests:**
- Health check endpoint
- Chat endpoints (POST and GET/EventSource)
- Request validation
- Error handling
- CORS configuration
- Response formats
- Frontend-backend integration

**Run:**
```bash
python tests/test_rag_api.py
```

**Expected Output:**
```
✓ Health endpoint working
✓ Chat POST endpoint working
✓ Chat GET endpoint configured for EventSource
...
Tests run: 14
Success rate: 100.0%
```

### 3. `test_rag_diagnostics.py`
**Purpose:** Comprehensive system diagnostics and troubleshooting

**Checks:**
1. Environment configuration (.env file)
2. Python dependencies
3. RAG module imports
4. System initialization
5. API routes configuration
6. Frontend configuration
7. Storage setup
8. Known issues detection

**Run:**
```bash
python tests/test_rag_diagnostics.py
```

**Expected Output:**
```
======================================================================
RAG SYSTEM COMPREHENSIVE DIAGNOSTICS
======================================================================

1. ENVIRONMENT CONFIGURATION
✓ .env file found
✓ LLM_API_KEY is configured
...

DIAGNOSTIC REPORT
Successes: 22
Warnings: 2
Critical Issues: 0
```

## Quick Start

### Run All Tests

```bash
# Navigate to project root
cd /home/runner/work/DataForgeTest/DataForgeTest

# Run integration tests
python tests/test_rag_integration.py

# Run API tests
python tests/test_rag_api.py

# Run diagnostics
python tests/test_rag_diagnostics.py
```

### Run with Python unittest

```bash
python -m unittest tests.test_rag_integration
python -m unittest tests.test_rag_api
```

### Run Specific Test Class

```bash
python -m unittest tests.test_rag_integration.TestRAGConfiguration
python -m unittest tests.test_rag_api.TestRAGAPIEndpoints
```

## Understanding Test Results

### ✓ Success Indicators
- Green checkmarks (✓)
- "OK" status
- 100% success rate
- All tests passed

### ⚠ Warnings
- Yellow warnings (⚠)
- Optional features not configured
- Non-critical issues
- Recommendations for improvement

### ✗ Critical Issues
- Red X marks (✗)
- Failed tests
- Missing required dependencies
- System cannot function properly

## Common Test Scenarios

### Scenario 1: Fresh Installation

**Run diagnostics first:**
```bash
python tests/test_rag_diagnostics.py
```

**Expected Issues:**
- `.env file not found` - Normal for first run
- `LLM packages not installed` - OK if using Simple RAG
- `PySpark not installed` - Install with requirements.txt

**Fix:**
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys if needed
```

### Scenario 2: Chat Not Responding

**Run API tests:**
```bash
python tests/test_rag_api.py
```

**Look for:**
- ✗ `Chat endpoint` failures → Backend not running
- ✗ `CORS` issues → Flask-CORS not installed
- ✓ All tests pass → Problem is in frontend or LLM config

### Scenario 3: LLM Integration Issues

**Run diagnostics:**
```bash
python tests/test_rag_diagnostics.py
```

**Look for:**
- "Using Simple RAG" warning → Not using Claude LLM
- "LLM API key not set" → Need to configure .env
- Missing llama-index packages → Install LLM dependencies

**Fix:**
```bash
pip install llama-index-llms-anthropic llama-index-embeddings-openai
# Configure .env with LLM_API_KEY
# Switch routes_simple to routes in api.py
```

## Test Coverage

### Backend Components Tested
- ✅ RAG Configuration (RAGConfig)
- ✅ Simple RAG System (SimpleRAG)
- ✅ Simple Chat Engine (SimpleChatEngine)
- ✅ Document operations (add, search, delete)
- ✅ Chat functionality
- ✅ Response formatting
- ✅ Storage and persistence

### API Endpoints Tested
- ✅ `GET /api/rag/health` - Health check
- ✅ `POST /api/rag/chat` - Non-streaming chat
- ✅ `GET /api/rag/chat?message=...` - EventSource streaming
- ✅ `GET /api/rag/sources` - List documents
- ✅ `POST /api/rag/upload` - Upload documents
- ✅ CORS configuration
- ✅ Error handling

### Integration Points Tested
- ✅ Frontend EventSource connection
- ✅ Response format compatibility
- ✅ Streaming format (SSE)
- ✅ Citation format
- ✅ Error messages
- ✅ URL encoding

## Continuous Testing

### Before Making Changes
```bash
# Baseline - ensure all tests pass
python tests/test_rag_integration.py
python tests/test_rag_api.py
```

### After Making Changes
```bash
# Verify changes didn't break anything
python tests/test_rag_integration.py
python tests/test_rag_api.py

# Run diagnostics to check configuration
python tests/test_rag_diagnostics.py
```

### Before Committing
```bash
# Full test suite
python tests/test_rag_integration.py && \
python tests/test_rag_api.py && \
python tests/test_rag_diagnostics.py
```

## Troubleshooting Test Failures

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Fix:**
```bash
pip install -r requirements.txt
```

### Path Issues

**Error:** `ModuleNotFoundError: No module named 'src'`

**Fix:**
```bash
# Run from project root
cd /home/runner/work/DataForgeTest/DataForgeTest
python tests/test_rag_integration.py
```

### Storage Permission Issues

**Error:** `PermissionError: [Errno 13] Permission denied: 'storage/vectorstore'`

**Fix:**
```bash
# Check and fix permissions
chmod 755 storage/
chmod 755 storage/vectorstore/
```

### API Test Failures

**Error:** Tests fail with "Flask not available"

**Fix:**
```bash
pip install flask flask-cors
```

## Adding New Tests

### Template for Integration Test

```python
class TestNewFeature(unittest.TestCase):
    """Test new feature."""

    def setUp(self):
        """Set up test environment."""
        self.config = RAGConfig.from_env()
        self.rag_system = SimpleRAG(self.config)

    def test_new_functionality(self):
        """Test that new feature works."""
        # Arrange
        test_data = "test"
        
        # Act
        result = self.rag_system.new_method(test_data)
        
        # Assert
        self.assertIsNotNone(result)
        print("✓ New feature works")
```

### Template for API Test

```python
class TestNewEndpoint(unittest.TestCase):
    """Test new API endpoint."""

    @classmethod
    def setUpClass(cls):
        """Set up test Flask app."""
        cls.app = Flask(__name__)
        cls.app.register_blueprint(rag_bp)
        cls.client = cls.app.test_client()

    def test_new_endpoint(self):
        """Test new endpoint responds correctly."""
        response = self.client.get('/api/rag/new-endpoint')
        self.assertEqual(response.status_code, 200)
        print("✓ New endpoint works")
```

## Test Data

Tests use temporary data that is cleaned up automatically:
- Test documents are created in memory or temp storage
- Storage tests use the configured storage path
- No permanent data is created during tests

## Performance

Typical test execution times:
- Integration tests: ~0.015s (16 tests)
- API tests: ~0.018s (14 tests)
- Diagnostics: ~2-3s (comprehensive checks)

Total: ~3-4 seconds for full suite

## CI/CD Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run RAG Tests
  run: |
    python tests/test_rag_integration.py
    python tests/test_rag_api.py
    python tests/test_rag_diagnostics.py
```

## Documentation

For more information, see:
- `docs/RAG_TROUBLESHOOTING.md` - Troubleshooting guide
- `.env.example` - Environment configuration
- `src/rag/` - RAG implementation code
- Project README.md - General setup

## Support

If tests fail unexpectedly:
1. Check test output for specific error messages
2. Run diagnostics: `python tests/test_rag_diagnostics.py`
3. Review `docs/RAG_TROUBLESHOOTING.md`
4. Check backend logs
5. Verify all dependencies are installed
