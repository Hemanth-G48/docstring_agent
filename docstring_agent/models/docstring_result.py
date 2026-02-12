from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DocstringResult(BaseModel):
    element_name: str
    generated_docstring: str
    confidence_score: float
    style: str
    reasoning: str
    warnings: List[str] = []
    processing_time: float
    improved_from: Optional[str] = None
    iteration: int = 1
