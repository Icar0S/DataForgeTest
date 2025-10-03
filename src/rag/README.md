# RAG (Retrieval-Augmented Generation) Module

This module contains the RAG system implementation with two different approaches for flexibility based on requirements.

## Architecture Overview

The system provides two implementations:

### 1. Simple RAG (Currently Active)
- **Files**: `routes_simple.py`, `simple_rag.py`, `simple_chat.py`, `config_simple.py`
- **Description**: Lightweight implementation using keyword-based search without external LLM dependencies
- **Use Case**: Testing, development, or when external API costs are a concern
- **Dependencies**: None (pure Python)
- **Activated in**: `src/api.py` (line 12: `from rag.routes_simple import rag_bp`)

### 2. Full RAG with LLM
- **Files**: `routes.py`, `chat.py`, `ingest.py`, `config.py`
- **Description**: Production-grade implementation using LlamaIndex with Anthropic Claude
- **Use Case**: Production environment requiring high-quality AI responses
- **Dependencies**: 
  - llama-index
  - llama-index-llms-anthropic
  - llama-index-embeddings-openai
  - anthropic API key
- **Activation**: Change `src/api.py` line 12 to `from rag.routes import rag_bp`

## Configuration

Both implementations use environment variables:

### Simple RAG (`config_simple.py`)
```env
VECTOR_STORE_PATH=./storage/vectorstore
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=4
MAX_UPLOAD_MB=10
```

### Full RAG (`config.py`)
```env
# All Simple RAG variables plus:
LLM_API_KEY=sk-ant-api03-...
LLM_MODEL=claude-3-haiku-20240307
EMBED_MODEL=text-embedding-3-small
```

## API Endpoints

Both implementations provide the same API endpoints:

- `POST /api/rag/chat` - Send a chat message
- `GET /api/rag/chat` - Stream chat response via EventSource
- `POST /api/rag/upload` - Upload a document
- `GET /api/rag/sources` - List all indexed documents
- `DELETE /api/rag/sources/<doc_id>` - Delete a document
- `GET /api/rag/health` - Health check

### Simple RAG Additional Endpoints
- `GET /api/rag/debug` - Debug RAG system state
- `POST /api/rag/reload` - Reload RAG system

### Full RAG Additional Endpoints
- `POST /api/rag/reindex` - Rebuild entire index

## Switching Implementations

To switch from Simple RAG to Full RAG:

1. Install dependencies:
   ```bash
   pip install llama-index-llms-anthropic llama-index-embeddings-openai llama-index-core
   ```

2. Set up environment variables in `.env`:
   ```env
   LLM_API_KEY=your-anthropic-api-key
   LLM_MODEL=claude-3-haiku-20240307
   EMBED_MODEL=text-embedding-3-small
   ```

3. Update `src/api.py` line 12:
   ```python
   # FROM:
   from rag.routes_simple import rag_bp
   
   # TO:
   from rag.routes import rag_bp
   ```

4. Restart the backend

## File Structure

```
src/rag/
├── __init__.py              # Module initialization
├── config.py                # Full RAG configuration
├── config_simple.py         # Simple RAG configuration
├── chat.py                  # Full RAG chat engine (LlamaIndex)
├── simple_chat.py           # Simple RAG chat engine (keyword-based)
├── ingest.py                # Full RAG document ingestion (LlamaIndex)
├── simple_rag.py            # Simple RAG document storage and search
├── routes.py                # Full RAG Flask routes
└── routes_simple.py         # Simple RAG Flask routes
```

## Design Decisions

### Why Two Implementations?

1. **Development Flexibility**: Simple RAG allows rapid development without API costs
2. **Testing**: Simple RAG can be tested without external dependencies
3. **Cost Management**: Simple RAG for demos, Full RAG for production
4. **Gradual Migration**: Can switch between implementations without changing frontend

### Why Not Merge?

The two implementations have fundamentally different architectures:
- Simple RAG: In-memory JSON storage with keyword matching
- Full RAG: Vector database with semantic search and LLM generation

Keeping them separate maintains clarity and allows easy switching based on needs.

## Code Quality

All files in this module follow Python best practices:
- PEP 8 style guide
- Type hints where applicable
- Comprehensive docstrings
- Pylint compliance (with documented exceptions)
- Proper error handling

## Testing

Tests for both implementations are in the `tests/` folder:
- `test_rag_simple.py` - Simple RAG tests
- `test_rag_integration.py` - Integration tests
- `test_rag_api.py` - API endpoint tests
- `test_rag_diagnostics.py` - Diagnostic tests

## Maintenance

When making changes:
1. Ensure both implementations maintain API compatibility
2. Update this README if endpoints or behavior changes
3. Run tests: `python -m pytest tests/`
4. Check code quality: `pylint src/rag/*.py`
