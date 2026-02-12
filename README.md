# Docstring Generation Agent

An AI-powered tool that automatically generates professional docstrings for Python code using multi-agent architecture with self-improving critics and confidence scoring.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents
- [🚀 Quick Start](#-quick-start)
- [🐳 Docker Usage](#-docker-usage)
- [✨ Core Features](#-core-features)
- [📟 CLI Commands](#-cli-commands)
- [🌐 API Server](#-api-server)
- [🎨 Docstring Styles](#-docstring-styles)
- [🧠 AI Features](#-ai-features)
- [🔧 Configuration](#-configuration)
- [❓ FAQ](#-faq)

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/docstring-agent.git
cd docstring-agent

# Install dependencies
pip install -r requirements.txt

# Set up your OpenAI API key (optional - has rule-based fallback)
export OPENAI_API_KEY="your-api-key-here"

# Run the application
python -m app --help
```

### 30 Second Demo

```bash
# Create a test file
echo "def add(a, b): return a + b" > test.py

# Generate docstring
python -m app generate test.py --style google

# View the result
cat test.py
```

**Output:**
```python
def add(a, b):
    """Add function.

    Args:
        a (int): Description of a.
        b (Any): Description of b.

    Returns:
        Any: Description of return value.
    """
    return a + b
```

---

## 🐳 Docker Usage

### Quick Start with Docker

```bash
# Build the image
docker build -t docstring-agent .

# Run CLI command
docker run -v $(pwd):/code docstring-agent python -m app generate /code/test.py

# Run API server
docker run -p 8000:8000 docstring-agent python -m app server --host 0.0.0.0
```

### Using Docker Compose

```bash
# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Start API server
docker-compose up -d server

# The API will be available at http://localhost:8000
```

### Docker Compose Services

| Service | Purpose | Example Usage |
|---------|---------|---------------|
| `server` | API server mode | `docker-compose up -d server` |
| `generate` | Single file generation | `docker-compose run --rm generate python -m app generate file.py` |
| `batch` | Batch processing | `docker-compose run --rm batch python -m app batch ./src --recursive` |
| `analyze` | Code analysis | `docker-compose run --rm analyze python -m app analyze file.py` |

### Examples

```bash
# Start API server
docker-compose up -d server

# Generate docstrings for a single file
docker-compose run --rm generate python -m app generate /code/myfile.py --style google

# Batch process a directory
docker-compose run --rm batch python -m app batch /code/src --recursive

# Analyze code
docker-compose run --rm analyze python -m app analyze /code/myfile.py

# View API documentation
curl http://localhost:8000/docs
```

---

## ✨ Core Features

- **📝 Multi-Style Docstring Generation**: Google, NumPy, and reStructuredText formats
- **🔍 Smart Code Analysis**: AST-based parsing with type inference and complexity calculation
- **🤖 Self-Improving AI**: Generator + Critic agent collaboration with iterative refinement
- **📊 Confidence Scoring**: Multi-factor quality assessment
- **🖥️ CLI & API**: Command-line interface and REST API server
- **📦 Batch Processing**: Repository-wide documentation

---

## 📟 CLI Commands

### 🔹 `generate` - Document Single File

```bash
# Basic usage
python -m app generate <file.py>

# With style selection
python -m app generate <file.py> --style google
python -m app generate <file.py> --style numpy
python -m app generate <file.py> --style rst

# Output to different file
python -m app generate <file.py> --output documented.py

# Overwrite existing docstrings
python -m app generate <file.py> --overwrite

# Preview changes without writing
python -m app generate <file.py> --diff

# Set refinement iterations (default: 3)
python -m app generate <file.py> --max-iterations 5

# Set quality threshold 0-1 (default: 0.8)
python -m app generate <file.py> --threshold 0.9
```

**Examples:**
```bash
# Document with Google style
python -m app generate calculator.py --style google

# Force update with preview
python -m app generate legacy_code.py --overwrite --diff

# High quality requirement with more iterations
python -m app generate critical.py --threshold 0.95 --max-iterations 5
```

---

### 🔹 `batch` - Document Multiple Files

```bash
# Process all Python files in directory
python -m app batch <directory>

# Recursive (include subdirectories)
python -m app batch <directory> --recursive

# Specify docstring style
python -m app batch <directory> --style numpy
```

**Examples:**
```bash
# Document entire project
python -m app batch ./src --recursive --style google

# Document with NumPy style
python -m app batch ./project --style numpy
```

---

### 🔹 `analyze` - Code Analysis Only

```bash
# Analyze code without generating
python -m app analyze <file.py>
```

**Example Output:**
```
        Code Analysis: calculator.py        
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Element         ┃ Type     ┃ Parameters ┃ Complexity ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ add             │ function │ a, b       │ 1          │
│ calculate_mean  │ function │ numbers    │ 4          │
└─────────────────┴──────────┴────────────┴────────────┘
```

---

### 🔹 `server` - Start API Server

```bash
# Start server with defaults (port 8000)
python -m app server

# Custom port
python -m app server --port 8080
```

**Example:**
```bash
# Start development server
python -m app server --port 8000
```

---

## 🌐 API Server

### Starting the Server

```bash
python -m app server --port 8000
```

The server will start at `http://localhost:8000`

### Interactive Documentation

OpenAPI/Swagger UI is available at:
```
http://localhost:8000/docs
```

### API Endpoints

#### POST `/generate`
Generate docstrings for a code snippet.

**Request:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
    "style": "google"
  }'
```

**Response:**
```json
{
  "success": true,
  "code": "def factorial(n):\n    \"\"\"Factorial function.\n\n    Args:\n        n (Any): Description of n.\n\n    Returns:\n        Any: Description of return value.\n    \"\"\"\n    return 1 if n <= 1 else n * factorial(n-1)",
  "confidence": 0.75,
  "iterations": 2
}
```

---

## 🎨 Docstring Styles

### Google Style (Default)

```bash
python -m app generate file.py --style google
```

```python
def calculate_mean(numbers):
    """Calculate the mean of a list of numbers.

    Args:
        numbers (list): List of numeric values.

    Returns:
        float: Arithmetic mean of the numbers.

    Raises:
        ValueError: If empty list provided.
    """
```

### NumPy Style

```bash
python -m app generate file.py --style numpy
```

```python
def calculate_mean(numbers):
    """Calculate the mean of a list of numbers.

    Parameters
    ----------
    numbers : list
        List of numeric values.

    Returns
    -------
    float
        Arithmetic mean of the numbers.

    Raises
    ------
    ValueError
        If empty list provided.
    """
```

### reStructuredText Style

```bash
python -m app generate file.py --style rst
```

```python
def calculate_mean(numbers):
    """Calculate the mean of a list of numbers.

    :param numbers: List of numeric values.
    :type numbers: list
    :returns: Arithmetic mean of the numbers.
    :rtype: float
    :raises ValueError: If empty list provided.
    """
```

---

## 🧠 AI Features

### Self-Improving Critic Loop

The system uses a Generator + Critic pattern:

1. **Generator Agent** creates initial docstring
2. **Critic Agent** evaluates quality and provides feedback
3. **Iterative refinement** continues until quality threshold is met or max iterations reached

Control the process with:
```bash
# Higher quality threshold requires better scores
python -m app generate file.py --threshold 0.9

# More iterations for better refinement
python -m app generate file.py --max-iterations 5
```

### Confidence Scoring

Each generated docstring receives a confidence score (0-1) based on:
- Parameter documentation completeness (20%)
- Return value documentation (15%)
- Exception documentation (10%)
- Description clarity (15%)
- Critic review score (40%)

Scores below the threshold trigger additional refinement iterations.

### Type Inference

The system analyzes your code to infer parameter types:

```python
def process_items(items):
    # Analyzes usage patterns:
    # - items.append(1)  → list
    # - items[0] = 2     → supports indexing
    # - len(items)       → has length
    result = items[0]
    return result
```

Inferred types are included in the generated docstring.

---

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI API Key (optional - has fallback)
export OPENAI_API_KEY="sk-..."

# Default docstring style
export DOCGEN_STYLE="google"

# Default quality threshold
export DOCGEN_THRESHOLD="0.8"
```

### .env File

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_key_here
DEFAULT_STYLE=google
MAX_ITERATIONS=3
QUALITY_THRESHOLD=0.8
```

---

## ❓ FAQ

### General

**Q: What Python versions are supported?**  
A: Python 3.9+

**Q: Can I use it without OpenAI?**  
A: Yes! The system has a rule-based fallback that generates docstrings without requiring an API key.

**Q: Is it free?**  
A: Yes, MIT License - free for all use.

**Q: Does it handle async/await?**  
A: Yes - full support for coroutines and async functions.

### Technical

**Q: How accurate is type inference?**  
A: Type inference is based on AST analysis of usage patterns. It works well for common patterns but may need manual review for complex cases.

**Q: Can it document classes?**  
A: Yes - classes, methods, properties, and constructors are all supported.

**Q: What's the maximum file size?**  
A: No hard limit, but very large files (>1MB) may take longer to process.

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

**🚀 Ready to document your codebase?**

```bash
python -m app --help
```

---

<div align="center">
  <sub>Built with ❤️ using LangChain and FastAPI</sub>
  <br>
  <sub>© 2024 Docstring Agent. All rights reserved.</sub>
</div>
