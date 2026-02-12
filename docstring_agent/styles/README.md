# Styles Module

Docstring style formatters and definitions.

## Overview

This module handles different docstring formatting styles used in Python projects.

## Supported Styles

### Google Style

The default style used by Google and many Python projects.

```python
def function(arg1, arg2):
    """One-line summary.
    
    Detailed description if needed.
    
    Args:
        arg1 (type): Description of arg1.
        arg2 (type): Description of arg2.
    
    Returns:
        type: Description of return value.
    
    Raises:
        ExceptionType: When/why this exception is raised.
    
    Note:
        Any additional notes or side effects.
    """
```

**Features:**
- Clean, readable format
- Section-based organization
- Type annotations in parentheses
- Widely adopted

### NumPy Style

Used by NumPy, SciPy, and scientific Python projects.

```python
def function(arg1, arg2):
    """One-line summary.
    
    Detailed description if needed.
    
    Parameters
    ----------
    arg1 : type
        Description of arg1.
    arg2 : type
        Description of arg2.
    
    Returns
    -------
    type
        Description of return value.
    """
```

**Features:**
- Underlined section headers
- Type on separate line
- Popular in scientific computing
- Supports extensive documentation

### reStructuredText (RST) Style

Standard format for Sphinx documentation.

```python
def function(arg1, arg2):
    """One-line summary.
    
    Detailed description if needed.
    
    :param arg1: Description of arg1.
    :type arg1: type
    :param arg2: Description of arg2.
    :type arg2: type
    :returns: Description of return value.
    :rtype: type
    """
```

**Features:**
- Sphinx-compatible
- Colon-prefixed directives
- Supports all Sphinx features
- Standard for ReadTheDocs

## Usage

```python
from docstring_agent.models.code_context import DocstringStyle

# Select style
style = DocstringStyle.GOOGLE  # or NUMPY, RST

# Pass to orchestrator
orchestrator = DocstringOrchestrator(style=style)
```

## Style Selection Guide

| Project Type | Recommended Style |
|--------------|-------------------|
| General Python | Google |
| Data Science/ML | NumPy |
| Library with Sphinx docs | RST |
| FastAPI/Modern Python | Google |
| Scientific Computing | NumPy |

## Implementation

Styles are implemented in the Generator Agent:
- `GeneratorAgent._format_google()`
- `GeneratorAgent._format_numpy()`
- `GeneratorAgent._format_rst()`
