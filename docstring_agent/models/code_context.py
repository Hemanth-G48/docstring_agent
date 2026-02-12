from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class CodeElementType(str, Enum):
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    CONSTRUCTOR = "constructor"

class DocstringStyle(str, Enum):
    GOOGLE = "google"
    NUMPY = "numpy"
    RST = "rst"

class Parameter(BaseModel):
    name: str
    type_hint: Optional[str] = None
    default_value: Optional[str] = None
    inferred_type: Optional[str] = None
    description: Optional[str] = None

class ReturnInfo(BaseModel):
    type_hint: Optional[str] = None
    inferred_type: Optional[str] = None
    description: Optional[str] = None
    is_generator: bool = False
    is_multiple: bool = False

class ExceptionInfo(BaseModel):
    exception_type: str
    description: Optional[str] = None

class CodeContext(BaseModel):
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
