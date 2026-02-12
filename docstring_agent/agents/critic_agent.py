from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from typing import List
import os

class CriticReview(BaseModel):
    score: float = Field(ge=0, le=1, description="Quality score from 0 to 1")
    issues: List[str] = Field(description="List of issues found")
    suggestions: List[str] = Field(description="Specific improvement suggestions")
    missing_info: List[str] = Field(description="Missing critical information")
    is_accurate: bool = Field(description="Whether docstring matches code behavior")
    clarity_score: float = Field(ge=0, le=1, description="Clarity and readability score")

class CriticAgent:
    """Self-refining critic agent that evaluates docstring quality"""
    
    def __init__(self, model_name="gpt-4", temperature=0.1):
        # Support OpenRouter or OpenAI
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        is_openrouter = os.getenv("OPENROUTER_API_KEY") is not None
        
        if is_openrouter:
            base_url = "https://openrouter.ai/api/v1"
            model = model_name if model_name != "gpt-4" else "anthropic/claude-3.5-sonnet"
        else:
            base_url = None
            model = model_name
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            base_url=base_url
        )
    
    def review(self, code: str, docstring: str, context) -> CriticReview:
        """Review docstring quality and provide feedback"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a strict Python documentation reviewer.
            Evaluate docstrings for accuracy, clarity, and completeness.
            Be critical - identify every issue and suggest specific fixes.
            Ensure the docstring actually matches what the code does."""),
            
            ("human", """
            Review this docstring for the following code:
            
            CODE:
            ```
            {code}
            ```
            
            DOCSTRING:
            {docstring}
            
            Evaluate:
            1. Accuracy - Does it correctly describe the behavior?
            2. Completeness - Are all parameters, returns, raises documented?
            3. Clarity - Is it easy to understand?
            4. Style - Does it follow consistent formatting?
            5. Examples - Should there be usage examples?
            
            Provide a score (0-1), list of specific issues, and suggestions.
            """)
        ])
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "code": code,
                "docstring": docstring
            })
            
            # Parse response into structured review
            return self._parse_review(response.content)
            
        except Exception as e:
            return CriticReview(
                score=0.5,
                issues=["Unable to complete review due to error"],
                suggestions=["Regenerate docstring"],
                missing_info=["Complete review failed"],
                is_accurate=False,
                clarity_score=0.5
            )
    
    def _parse_review(self, content: str) -> CriticReview:
        """Parse LLM response into structured review"""
        # Simple parsing logic - in production, use structured output
        score = 0.7  # Default
        issues = []
        suggestions = []
        
        lines = content.lower().split('\n')
        for line in lines:
            if 'score:' in line or 'rating:' in line:
                try:
                    score = float(''.join(c for c in line if c.isdigit() or c == '.'))
                except:
                    pass
            elif 'issue:' in line or 'problem:' in line:
                issues.append(line.split(':', 1)[1].strip())
            elif 'suggest:' in line or 'fix:' in line:
                suggestions.append(line.split(':', 1)[1].strip())
        
        return CriticReview(
            score=min(1.0, max(0.0, score)),
            issues=issues[:5],
            suggestions=suggestions[:5],
            missing_info=[],
            is_accurate=score > 0.7,
            clarity_score=score * 0.9
        )
