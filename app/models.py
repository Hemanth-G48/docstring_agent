"""Pydantic data models for the docstring generation agent."""

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class CodeElementType(str, Enum):
    """Types of code elements that can be documented."""
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    CONSTRUCTOR = "constructor"


class DocstringStyle(str, Enum):
    """Supported docstring format styles."""
    GOOGLE = "google"
    NUMPY = "numpy"
    RST = "rst"


class Parameter(BaseModel):
    """Represents a function parameter with type information."""
    name: str
    type_hint: Optional[str] = None
    default_value: Optional[str] = None
    inferred_type: Optional[str] = None
    description: Optional[str] = None


class ReturnInfo(BaseModel):
    """Represents return value information."""
    type_hint: Optional[str] = None
    inferred_type: Optional[str] = None
    description: Optional[str] = None
    is_generator: bool = False
    is_multiple: bool = False


class ExceptionInfo(BaseModel):
    """Represents information about raised exceptions."""
    exception_type: str
    description: Optional[str] = None


class CodeContext(BaseModel):
    """Complete context for a code element being analyzed."""
    element_type: CodeElementType
    name: str
    qualified_name: str
    parameters: List[Parameter] = []
    returns: Optional[ReturnInfo] = None
    raises: List[ExceptionInfo] = []
    existing_docstring: Optional[str] = None
    source_code: str
    line_number: int
    complexity_score: Optional[int] = None
    decorators: List[str] = []
    is_async: bool = False
    body_summary: Optional[str] = None


class DocstringResult(BaseModel):
    """Result of docstring generation for a code element."""
    element_name: str
    generated_docstring: str
    confidence_score: float
    style: str
    reasoning: str
    warnings: List[str] = []
    processing_time: float
    improved_from: Optional[str] = None
    iteration: int = 1


class CriticReview(BaseModel):
    """Review output from the critic agent."""
    score: float = Field(ge=0, le=1, description="Quality score from 0 to 1")
    issues: List[str] = Field(description="List of issues found")
    suggestions: List[str] = Field(description="Specific improvement suggestions")
    missing_info: List[str] = Field(description="Missing critical information")
    is_accurate: bool = Field(description="Whether docstring matches code behavior")
    clarity_score: float = Field(ge=0, le=1, description="Clarity and readability score")


class DocstringSuggestion(BaseModel):
    """Structured output from the generator agent."""
    summary: str = Field(description="One-line summary of what the code does")
    description: str = Field(description="Detailed description of the behavior")
    args_description: List[str] = Field(description="Description of each argument")
    returns_description: str = Field(description="Description of return value")
    raises_description: List[str] = Field(description="Description of exceptions raised")
    side_effects: List[str] = Field(description="Any side effects the code has")
    example: Optional[str] = Field(description="Optional example usage")
