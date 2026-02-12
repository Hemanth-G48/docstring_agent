# CLI Module

Command-line interface for the docstring generation agent.

## Overview

Provides a user-friendly CLI using Typer with support for:
- Single file processing
- Batch directory processing  
- API server mode
- Rich output formatting

## File Location

`cli.py` (in project root)

## Commands

### `generate`

Generate docstrings for a single Python file.

```bash
python cli.py generate <file_path> [options]
```

**Options:**
| Option | Default | Description |
|--------|---------|-------------|
| `--style` | google | Docstring style (google/numpy/rst) |
| `--output` | None | Output file path |
| `--overwrite` | False | Overwrite existing docstrings |
| `--max-iterations` | 3 | Maximum refinement iterations |
| `--threshold` | 0.8 | Quality threshold (0-1) |
| `--diff` | False | Show diff preview |

**Example:**
```bash
# Generate with Google style
python cli.py generate my_script.py

# Generate with NumPy style and save to file
python cli.py generate my_script.py --style numpy --output documented.py

# Overwrite existing docstrings
python cli.py generate my_script.py --overwrite

# Show changes preview
python cli.py generate my_script.py --diff
```

### `batch`

Process all Python files in a directory.

```bash
python cli.py batch <directory> [options]
```

**Options:**
| Option | Default | Description |
|--------|---------|-------------|
| `--style` | google | Docstring style |
| `--recursive` | True | Process subdirectories |

**Example:**
```bash
# Process all Python files recursively
python cli.py batch ./src

# Process only top-level files
python cli.py batch ./src --no-recursive
```

### `server`

Start a FastAPI server for API access.

```bash
python cli.py server [options]
```

**Options:**
| Option | Default | Description |
|--------|---------|-------------|
| `--host` | 0.0.0.0 | Host to bind |
| `--port` | 8000 | Port to bind |

**Example:**
```bash
# Start server on default port
python cli.py server

# Start on custom port
python cli.py server --port 8080
```

**API Endpoint:**
```bash
POST /generate
Content-Type: application/json

{
  "code": "def add(a, b): return a + b",
  "style": "google"
}
```

## Output Formatting

The CLI uses Rich for beautiful output:
- Syntax-highlighted code preview
- Progress bars for batch operations
- Colored status messages
- Tabular reports

## Exit Codes

- `0`: Success
- `1`: Error in processing

## Environment Variables

Required in `.env` file:
```env
OPENAI_API_KEY=your_api_key_here
```
