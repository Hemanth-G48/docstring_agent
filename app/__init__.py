"""Docstring Generation Agent - AI-powered Python documentation generator."""

from .models import (
    CodeContext,
    CodeElementType,
    DocstringStyle,
    Parameter,
    ReturnInfo,
    ExceptionInfo,
    DocstringResult,
    CriticReview,
    DocstringSuggestion,
)
from .tools import (
    CodeAnalyzer,
    DocstringInjector,
    ConfidenceScorer,
)
from .agents import (
    GeneratorAgent,
    CriticAgent,
    DocstringOrchestrator,
)
from .config import Config, get_config, set_config

__version__ = "1.0.0"
__all__ = [
    # Models
    "CodeContext",
    "CodeElementType",
    "DocstringStyle",
    "Parameter",
    "ReturnInfo",
    "ExceptionInfo",
    "DocstringResult",
    "CriticReview",
    "DocstringSuggestion",
    # Tools
    "CodeAnalyzer",
    "DocstringInjector",
    "ConfidenceScorer",
    # Agents
    "GeneratorAgent",
    "CriticAgent",
    "DocstringOrchestrator",
    # Config
    "Config",
    "get_config",
    "set_config",
]
