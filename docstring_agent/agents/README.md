# Agents Module

The agents module implements a multi-agent architecture for docstring generation using LangChain and LLMs.

## Overview

This module contains three specialized agents that work together:

- **Generator Agent**: Creates initial docstrings using LLM prompts
- **Critic Agent**: Reviews and evaluates docstring quality
- **Orchestrator**: Coordinates the workflow and manages iterations

## Components

### Generator Agent (`generator_agent.py`)

Generates docstrings with multiple style support.

**Features:**
- LLM-based generation using GPT-4
- Structured output with Pydantic models
- Multiple docstring styles: Google, NumPy, reStructuredText
- Fallback rule-based generation when LLM fails
- Type inference integration

**Key Class:**
```python
class GeneratorAgent:
    def generate(context: CodeContext, style: DocstringStyle) -> str
```

### Critic Agent (`critic_agent.py`)

Self-refining critic that evaluates docstring quality.

**Features:**
- Multi-factor quality assessment
- Structured review output (score, issues, suggestions)
- Accuracy validation
- Clarity scoring

**Key Class:**
```python
class CriticAgent:
    def review(code: str, docstring: str, context) -> CriticReview
```

### Orchestrator (`orchestrator.py`)

Central coordinator managing the generation workflow.

**Features:**
- File processing pipeline
- Iterative refinement loop
- Progress tracking with Rich
- Quality threshold enforcement
- Report generation

**Key Class:**
```python
class DocstringOrchestrator:
    def process_file(file_path: str, overwrite: bool = False) -> str
```

## Workflow

1. **Analyze**: Parse source code with AST analyzer
2. **Generate**: Create docstring for each function/class
3. **Review**: Critic evaluates quality
4. **Score**: Calculate confidence score
5. **Refine**: Iterate if below threshold
6. **Inject**: Insert best docstring into code

## Usage

```python
from docstring_agent.agents.orchestrator import DocstringOrchestrator
from docstring_agent.models.code_context import DocstringStyle

orchestrator = DocstringOrchestrator(
    style=DocstringStyle.GOOGLE,
    max_iterations=3,
    quality_threshold=0.8
)

result = orchestrator.process_file("my_module.py")
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `style` | GOOGLE | Docstring format style |
| `max_iterations` | 3 | Maximum refinement iterations |
| `quality_threshold` | 0.8 | Minimum confidence score |
| `skip_existing` | True | Skip functions with existing docstrings |
