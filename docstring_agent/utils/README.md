# Utils Module

Utility functions supporting the docstring generation pipeline.

## Overview

This module contains helper utilities for quality assessment and scoring.

## Components

### Confidence Scorer (`confidence_scorer.py`)

Multi-factor confidence scoring system for generated docstrings.

**Features:**
- Weighted scoring algorithm
- Parameter coverage analysis
- Return value documentation check
- Exception documentation check
- Clarity metrics evaluation

**Scoring Weights:**
| Factor | Weight | Description |
|--------|--------|-------------|
| Critic Score | 40% | LLM critic evaluation |
| Parameter Coverage | 20% | All parameters documented |
| Return Coverage | 15% | Return value documented |
| Exception Coverage | 10% | Exceptions documented |
| Clarity Metrics | 15% | Readability and formatting |

**Key Class:**
```python
class ConfidenceScorer:
    def calculate(context: CodeContext, 
                  docstring: str, 
                  review: CriticReview) -> float
```

**Scoring Details:**

1. **Critic Score**: Direct score from Critic Agent (0-1)

2. **Parameter Coverage**:
   - Checks if all parameter names appear in docstring
   - Returns 1.0 if no parameters
   - Ratio of documented parameters

3. **Return Coverage**:
   - Checks for return-related keywords
   - Returns 1.0 for None returns
   - Binary score (0 or 1)

4. **Exception Coverage**:
   - Checks if all exception types are documented
   - Returns 1.0 if no exceptions raised
   - Ratio of documented exceptions

5. **Clarity Metrics**:
   - Length check: 10-200 words optimal
   - Complete sentences detection
   - Proper formatting (triple quotes)
   - Required sections (Args/Parameters)

## Usage

```python
from docstring_agent.utils.confidence_scorer import ConfidenceScorer
from docstring_agent.agents.critic_agent import CriticReview

scorer = ConfidenceScorer()

confidence = scorer.calculate(
    context=context,
    docstring=generated_docstring,
    review=critic_review
)

print(f"Confidence Score: {confidence:.2%}")
```

## Thresholds

The orchestrator uses confidence scores to determine:
- Whether to accept a docstring (≥ threshold)
- Whether to trigger refinement (< threshold)
- Which version to keep (highest score wins)

Default threshold: **0.8 (80%)**
