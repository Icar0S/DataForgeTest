# Tests

This directory contains all tests for DataForgeTest, organized by layer (frontend/backend) and test type.

## Directory Structure

```
tests/
├── backend/
│   ├── unit/           # Unit tests for individual modules and functions
│   ├── api/            # Tests for API endpoints (Flask routes)
│   ├── security/       # Security and code quality tests
│   ├── integration/    # Integration tests for multiple components
│   └── e2e/            # End-to-end workflow tests
├── frontend/
│   ├── unit/           # Unit tests for React components and pages
│   ├── api/            # Tests for frontend API calls
│   ├── security/       # Frontend security tests
│   ├── integration/    # Integration tests for frontend components
│   └── e2e/            # End-to-end UI workflow tests
└── README.md
```

## Backend Tests

Run backend tests from the project root:

```bash
pytest tests/backend/unit/
pytest tests/backend/api/
pytest tests/backend/integration/
pytest tests/backend/e2e/
pytest tests/backend/
```

## Frontend Tests

Frontend tests are run from the `frontend/` directory using React Scripts:

```bash
cd frontend

# Run all tests (including tests/frontend/ directory)
npm test -- --watchAll=false

# Run specific test suites
npm test -- --testPathPattern=unit --watchAll=false
npm test -- --testPathPattern=integration --watchAll=false

# Run with coverage
npm test -- --watchAll=false --coverage
```

## Utility Scripts

The following diagnostic and utility scripts remain at the root of `tests/`:

- `check_routes.py` - Check registered Flask routes
- `debug_imports.py` - Debug import issues
- `diagnose_import_issue.py` - Diagnose import problems
- `diagnose_llm_production.py` - Diagnose LLM in production
- `diagnose_rag_llm.py` - Diagnose RAG/LLM issues
- `fix_entry_points.py` - Fix entry point issues
- `manual_test_user_scenario.py` - Manual test user scenarios
- `run_404_fix_tests.py` - Run 404 fix validation tests
