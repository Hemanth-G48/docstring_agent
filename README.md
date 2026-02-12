# Docstring Generation Agent

A production-ready, multi-agent docstring generation system with advanced features like self-refining critics, confidence scoring, and type inference.

## Features

- **Multi-Agent Architecture**: Generator, Critic, and Orchestrator agents working together
- **Self-Refining Critic**: Iterative quality improvement with feedback loops
- **Confidence Scoring**: Multi-factor quality assessment
- **Type Inference**: Static analysis for parameter types
- **Multiple Styles**: Google, NumPy, and reStructuredText docstring formats
- **CLI & API**: Command-line interface and REST API server
- **Batch Processing**: Repository-wide documentation

## Project Structure

```
app/
├── __init__.py          # Package exports
├── __main__.py          # CLI entry point
├── config.py            # Configuration management
├── models.py            # Pydantic data models
├── tools.py             # Analysis and injection tools
└── agents.py            # Multi-agent system
```

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd docstring-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Quick Start

### CLI Usage

```bash
# Run as a module
python -m app generate my_script.py --style google

# Batch process a directory
python -m app batch ./src --style numpy --recursive

# Analyze code structure
python -m app analyze my_script.py

# Start API server
python -m app server --port 8000
```

### Python API

```python
from app import DocstringOrchestrator, DocstringStyle

# Initialize orchestrator
orchestrator = DocstringOrchestrator(
    style=DocstringStyle.GOOGLE,
    max_iterations=3,
    quality_threshold=0.8
)

# Process a file
enhanced_code = orchestrator.process_file("my_module.py")

# Or process code directly
source_code = """
def add(a, b):
    return a + b
"""
result = orchestrator.process_code(source_code)
```

### API Usage

```bash
# Start the server
python -m app server

# Make a request
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b): return a + b",
    "style": "google"
  }'
```

## Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
DEFAULT_MODEL=gpt-4
DEFAULT_TEMPERATURE=0.2
DEFAULT_STYLE=google
MAX_ITERATIONS=3
QUALITY_THRESHOLD=0.8
```

Or configure programmatically:

```python
from app import Config, set_config

config = Config(
    openai_api_key="your_key",
    default_model="gpt-4",
    quality_threshold=0.9
)
set_config(config)
```

## Architecture

### Models (`models.py`)
- `CodeContext`: Represents analyzed code elements
- `DocstringResult`: Generated docstring with metadata
- `CriticReview`: Quality assessment output
- Enums for styles and element types

### Tools (`tools.py`)
- `CodeAnalyzer`: AST-based code parsing and type inference
- `DocstringInjector`: Injects docstrings into source code
- `ConfidenceScorer`: Multi-factor quality scoring

### Agents (`agents.py`)
- `GeneratorAgent`: Creates docstrings with style support
- `CriticAgent`: Evaluates docstring quality
- `DocstringOrchestrator`: Coordinates the workflow

### Config (`config.py`)
- Environment-based configuration
- Global config management
- Default values

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Format code
black app
isort app

# Type checking
mypy app
```

## Docker

```bash
# Build image
docker build -t docstring-agent .

# Run CLI
docker run -v $(pwd):/code docstring-agent python -m app generate /code/my_script.py

# Run server
docker run -p 8000:8000 docstring-agent python -m app server
```

## License

MIT License
