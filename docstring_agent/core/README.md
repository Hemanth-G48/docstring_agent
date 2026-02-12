# Core Module

The core module provides foundational functionality for code analysis and docstring injection.

## Overview

This module handles:
- AST-based code parsing and analysis
- Type inference from code patterns
- Docstring injection into source code

## Components

### AST Analyzer (`ast_analyzer.py`)

Advanced Python code analyzer using the Abstract Syntax Tree.

**Features:**
- Function and class extraction
- Parameter analysis with type inference
- Return type detection
- Exception detection
- Cyclomatic complexity calculation
- Async function support

**Key Class:**
```python
class CodeAnalyzer:
    def analyze(source_code: str) -> List[CodeContext]
    def _analyze_function(node, source_code: str) -> CodeContext
    def _analyze_class(node: ast.ClassDef, source_code: str) -> List[CodeContext]
```

**Type Inference:**
- Pattern-based type detection from code usage
- Supports: int, float, str, bool, list, dict, set, tuple
- Combines with explicit type hints

**Metrics Calculated:**
- Cyclomatic complexity (branches, loops, conditionals)
- Function length and structure
- Parameter defaults

### Docstring Injector (`docstring_injector.py`)

Injects generated docstrings back into source code.

**Features:**
- AST-based code modification
- Preserves code formatting
- Removes existing docstrings
- Inserts at correct positions

**Key Class:**
```python
class DocstringInjector:
    def inject_docstrings(source_code: str, results: List[DocstringResult]) -> str
```

## Usage

```python
from docstring_agent.core.ast_analyzer import CodeAnalyzer
from docstring_agent.core.docstring_injector import DocstringInjector

# Analyze code
analyzer = CodeAnalyzer()
contexts = analyzer.analyze(source_code)

# Inject docstrings
injector = DocstringInjector()
enhanced_code = injector.inject_docstrings(source_code, results)
```

## Data Flow

```
Source Code → AST Parser → CodeContext Objects → Docstring Generation → AST Modification → Enhanced Code
```

## Dependencies

- `ast`: Python standard library AST module
- `astor`: AST to source code conversion
- Custom models from `docstring_agent.models`
