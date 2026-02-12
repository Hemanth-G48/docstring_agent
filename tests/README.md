# Tests

Test suite for the docstring generation agent.

## Overview

Comprehensive tests covering unit and integration testing.

## Structure

```
tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_ast_analyzer.py      # AST parsing tests
│   ├── test_docstring_injector.py # Injection tests
│   └── test_confidence_scorer.py  # Scoring tests
└── integration/
    └── __init__.py
```

## Unit Tests

### AST Analyzer Tests (`test_ast_analyzer.py`)

Tests for code analysis functionality:
- Function extraction
- Class and method extraction
- Type inference accuracy
- Complexity calculation
- Parameter parsing
- Exception detection

**Example Test Cases:**
- Simple function analysis
- Class with methods
- Async functions
- Functions with decorators
- Type hint extraction

### Docstring Injector Tests (`test_docstring_injector.py`)

Tests for code modification:
- Docstring insertion
- Existing docstring replacement
- Position accuracy
- Code preservation
- Multiple injections

### Confidence Scorer Tests (`test_confidence_scorer.py`)

Tests for quality scoring:
- Score calculation accuracy
- Parameter coverage detection
- Return coverage detection
- Exception coverage detection
- Clarity metrics

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=docstring_agent

# Run specific test file
pytest tests/unit/test_ast_analyzer.py

# Run with verbose output
pytest -v

# Run with specific marker
pytest -m "slow"
```

## Test Fixtures

Sample code snippets used in tests:

```python
# Simple function fixture
SIMPLE_FUNCTION = """
def add(a, b):
    return a + b
"""

# Class fixture  
CLASS_WITH_METHODS = """
class Calculator:
    def __init__(self):
        self.value = 0
    
    def add(self, x):
        self.value += x
        return self.value
"""

# Async function fixture
ASYNC_FUNCTION = """
async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        return await session.get(url)
"""
```

## CI Integration

Tests run automatically on:
- Push to main branch
- Pull requests
- Multiple Python versions (3.9, 3.10, 3.11)

See `.github/workflows/ci.yml` for configuration.

## Coverage Goals

- Core modules: >90%
- Agent modules: >80%
- Utilities: >85%

## Adding Tests

When adding new features:
1. Add unit tests for new functions/classes
2. Update integration tests if API changes
3. Ensure coverage doesn't decrease
4. Follow existing test patterns
