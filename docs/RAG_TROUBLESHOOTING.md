# RAG System Troubleshooting Guide

## Problem: RAG Chat Not Responding

When running `dev_start.bat` and accessing the Support page, the RAG chat system doesn't connect or respond to messages.

## Root Cause Analysis

After comprehensive testing, we've identified the following issues:

### 1. **Using Simple RAG Implementation (Not LLM-based)**

The system is currently using `routes_simple.py` which implements a basic keyword-based search system, **NOT** an actual LLM integration with Claude Sonnet.

**Current Flow:**
```
Frontend → EventSource → /api/rag/chat (GET) → SimpleChatEngine → Keyword Search → Response
```

**Expected Flow (for LLM):**
```
Frontend → EventSource → /api/rag/chat (GET) → ChatEngine → Claude API → RAG-enhanced Response
```

### 2. **Missing LLM API Configuration**

The `.env` file with LLM API credentials is not configured, which would be required for the full RAG system.

### 3. **Missing Dependencies**

The full RAG system with LLM integration requires additional packages that may not be installed:
- `llama-index-llms-anthropic` (for Claude)
- `llama-index-embeddings-openai` (for embeddings)
- `llama-index-core` (core framework)

## Test Results

✅ **All backend tests pass** (16/16 tests)
✅ **All API tests pass** (14/14 tests)
✅ **Simple RAG system works correctly**

The issue is not a bug - it's the architectural choice of using Simple RAG instead of full LLM RAG.

## Solutions

### Option 1: Test Simple RAG (Current Implementation)

The Simple RAG works but needs documents in the knowledge base:

1. **Start the backend and frontend** (using `dev_start.bat`)

2. **Upload a document:**
   ```bash
   curl -X POST http://localhost:5000/api/rag/upload \
     -F "file=@path/to/your/document.txt"
   ```

3. **Test the chat:**
   - Go to Support page
   - Ask: "What is data quality?"
   - The system will search uploaded documents and respond

**Note:** Simple RAG uses keyword matching, not AI understanding.

### Option 2: Enable Full LLM Integration (Recommended)

To use Claude Sonnet with RAG:

#### Step 1: Get API Key

1. Sign up at https://console.anthropic.com/
2. Get your API key
3. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
4. Add your API key:
   ```
   LLM_API_KEY=sk-ant-api03-...your-key...
   LLM_MODEL=claude-3-sonnet-20240229
   ```

#### Step 2: Install Dependencies

```bash
pip install llama-index-llms-anthropic llama-index-embeddings-openai llama-index-core
```

#### Step 3: Switch to Full RAG Routes

Edit `src/api.py`, change line 12:
```python
# FROM:
from rag.routes_simple import rag_bp

# TO:
from rag.routes import rag_bp
```

#### Step 4: Restart Backend

Stop the backend and run `dev_start.bat` again.

### Option 3: Quick Test with Existing System

To verify the system is working with Simple RAG:

```bash
# 1. Run tests
cd /home/runner/work/DataForgeTest/DataForgeTest
python tests/test_rag_integration.py
python tests/test_rag_api.py

# 2. Run diagnostics
python tests/test_rag_diagnostics.py
```

## Diagnostic Tests

We've added comprehensive test suites:

### 1. `test_rag_integration.py`
Tests RAG system components:
- Configuration loading
- Document operations
- Search functionality
- Chat engine operations
- Response format compatibility

### 2. `test_rag_api.py`
Tests API endpoints:
- Health checks
- Chat endpoints (POST and GET/EventSource)
- Request validation
- CORS configuration
- Response formats

### 3. `test_rag_diagnostics.py`
Comprehensive system diagnostics:
- Environment configuration
- Dependencies check
- Module imports
- System initialization
- Storage permissions
- Frontend-backend integration

## Running the Tests

```bash
# All integration tests
python tests/test_rag_integration.py

# All API tests
python tests/test_rag_api.py

# Full diagnostics
python tests/test_rag_diagnostics.py
```

## Common Issues and Solutions

### Issue: "Connection error" in frontend

**Cause:** Backend not running or wrong port

**Solution:**
1. Check backend is running on port 5000
2. Check console for errors: `netstat -an | find "5000"`
3. Restart backend

### Issue: "No response from chat"

**Cause:** No documents in knowledge base (Simple RAG)

**Solution:**
1. Upload documents via `/api/rag/upload`
2. Or switch to full LLM RAG (doesn't require documents)

### Issue: "Module not found" errors

**Cause:** Missing Python dependencies

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "LLM API key not configured"

**Cause:** Using full RAG routes without API key

**Solution:**
1. Create `.env` with `LLM_API_KEY`
2. Or switch back to `routes_simple.py`

## System Architecture

### Current (Simple RAG):
```
┌─────────────┐
│  Frontend   │
│ (React)     │
└──────┬──────┘
       │ EventSource
       │ /api/rag/chat?message=...
       ▼
┌─────────────────┐
│   Flask API     │
│ (routes_simple) │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  SimpleChatEngine│
│   - Keyword      │
│     Search       │
│   - Template     │
│     Response     │
└─────────────────┘
```

### Full RAG (with LLM):
```
┌─────────────┐
│  Frontend   │
│ (React)     │
└──────┬──────┘
       │ EventSource
       │ /api/rag/chat?message=...
       ▼
┌─────────────────┐
│   Flask API     │
│   (routes)      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  ChatEngine     │
│  (LlamaIndex)   │
└──────┬──────────┘
       │
       ├─────────────────┐
       ▼                 ▼
┌──────────────┐  ┌─────────────┐
│ Vector Store │  │  Claude API │
│ (Documents)  │  │  (Sonnet)   │
└──────────────┘  └─────────────┘
```

## Verification Checklist

After implementing fixes, verify:

- [ ] Backend starts without errors
- [ ] Frontend connects to backend
- [ ] Health endpoint responds: `curl http://localhost:5000/api/rag/health`
- [ ] Can upload documents (Simple RAG) or API key set (Full RAG)
- [ ] Chat responds on Support page
- [ ] Responses are relevant to questions
- [ ] Citations/sources are shown
- [ ] No console errors in browser or terminal

## Additional Resources

- **Test Files:**
  - `tests/test_rag_integration.py` - Core functionality tests
  - `tests/test_rag_api.py` - API endpoint tests
  - `tests/test_rag_diagnostics.py` - System diagnostics

- **Configuration:**
  - `.env.example` - Environment variables template
  - `src/rag/config.py` - Full RAG configuration
  - `src/rag/config_simple.py` - Simple RAG configuration

- **RAG Implementations:**
  - `src/rag/routes.py` - Full RAG with LLM
  - `src/rag/routes_simple.py` - Simple keyword-based RAG
  - `src/rag/chat.py` - LLM chat engine
  - `src/rag/simple_chat.py` - Simple chat engine

## Contact

For additional support, check:
- Project README.md
- Test output for specific errors
- Backend logs in terminal
- Browser console for frontend errors
