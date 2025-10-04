# Utilities Folder

This folder contains utility scripts and helper files that are not part of the main test suite but are useful for debugging, development, and data management.

## Scripts

### Debug Scripts

- **debug_rag.py** - Debug the RAG system to check current state and test responses
- **debug_config.py** - Debug RAG configuration and file loading paths
- **debug_flask_vs_direct.py** - Compare Flask RAG vs Direct RAG to diagnose issues

### Data Management Scripts

- **clean_knowledge_base.py** - Clean and remove shallow/test documents from knowledge base
- **enhance_knowledge_base.py** - Add comprehensive documentation to the RAG knowledge base
- **fix_rag_chunks.py** - Rebuild chunks for all documents in the RAG system

### Test Data

- **sample_answers.py** - Sample answers for testing DSL and PySpark code generation

## Usage

These scripts are meant to be run directly from the repository root:

```bash
# Debug RAG system
python utilities/debug_rag.py

# Fix RAG chunks
python utilities/fix_rag_chunks.py

# Clean knowledge base
python utilities/clean_knowledge_base.py
```

## Note

These utilities are not part of the automated test suite (in the `tests/` folder) but are valuable tools for development and maintenance.
