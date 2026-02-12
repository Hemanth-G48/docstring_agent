# Models Module

Pydantic data models defining the structure of code context and generation results.

## Overview

This module provides type-safe data structures used throughout the docstring generation pipeline.

## Components

### Code Context (`code_context.py`)

Defines the structure of analyzed code elements.

**Enums:**
```python
class CodeElementType(str, Enum):
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    CONSTRUCTOR = "constructor"

class DocstringStyle(str, Enum):
    GOOGLE = "google"
    NUMPY = "numpy"
    RST = "rst"
```

**Models:**

#### `Parameter`
Represents a function parameter.
- `name`: Parameter name
- `type_hint`: Explicit type annotation
- `default_value`: Default value if any
- `inferred_type`: Type inferred from usage
- `description`: Generated description

#### `ReturnInfo`
Represents return value information.
- `type_hint`: Explicit return type
- `inferred_type`: Inferred return type
- `description`: Return description
- `is_generator`: Whether function is a generator
- `is_multiple`: Whether returns multiple values

#### `ExceptionInfo`
Represents raised exceptions.
- `exception_type`: Exception class name
- `description`: When/why it's raised

#### `CodeContext`
Complete context for a code element.
- `element_type`: Function, class, method, or constructor
- `name`: Element name
- `qualified_name`: Fully qualified name
- `parameters`: List of Parameter objects
- `returns`: ReturnInfo object
- `raises`: List of ExceptionInfo objects
- `existing_docstring`: Current docstring if any
- `source_code`: Complete source code
- `line_number`: Line number in file
- `complexity_score`: Cyclomatic complexity
- `decorators`: List of decorators
- `is_async`: Whether async function
- `body_summary`: Summary for refinement

### Docstring Result (`docstring_result.py`)

Defines the structure of generation results.

#### `DocstringResult`
Represents a generated docstring with metadata.
- `element_name`: Function/class name
- `generated_docstring`: The generated docstring
- `confidence_score`: Quality score (0-1)
- `style`: Docstring style used
- `reasoning`: Generation reasoning
- `warnings`: List of issues/warnings
- `processing_time`: Time taken to generate
- `improved_from`: Previous version if refined
- `iteration`: Iteration number

## Usage

```python
from docstring_agent.models.code_context import CodeContext, DocstringStyle
from docstring_agent.models.docstring_result import DocstringResult

# Create context
context = CodeContext(
    element_type=CodeElementType.FUNCTION,
    name="my_function",
    qualified_name="my_module.my_function",
    parameters=[],
    source_code="def my_function(): pass",
    line_number=1
)

# Create result
result = DocstringResult(
    element_name="my_function",
    generated_docstring='"""My function."""',
    confidence_score=0.85,
    style="google",
    reasoning="Generated via LLM",
    processing_time=1.5
)
```

## Design Principles

1. **Type Safety**: All models use Pydantic for validation
2. **Immutability**: Models are frozen after creation
3. **Serialization**: Easy JSON serialization for API responses
4. **Extensibility**: Easy to add new fields
