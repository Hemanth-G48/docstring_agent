from ..models.code_context import CodeContext
from ..agents.critic_agent import CriticReview
import re

class ConfidenceScorer:
    """Calculate confidence scores for generated docstrings"""
    
    def calculate(self, context: CodeContext, 
                 docstring: str, 
                 review: CriticReview) -> float:
        
        scores = []
        
        # 1. Critic score (40% weight)
        scores.append(review.score * 0.4)
        
        # 2. Parameter coverage (20% weight)
        param_coverage = self._check_param_coverage(context, docstring)
        scores.append(param_coverage * 0.2)
        
        # 3. Return coverage (15% weight)
        return_coverage = self._check_return_coverage(context, docstring)
        scores.append(return_coverage * 0.15)
        
        # 4. Exception coverage (10% weight)
        exception_coverage = self._check_exception_coverage(context, docstring)
        scores.append(exception_coverage * 0.1)
        
        # 5. Clarity metrics (15% weight)
        clarity = self._check_clarity(docstring)
        scores.append(clarity * 0.15)
        
        return sum(scores)
    
    def _check_param_coverage(self, context: CodeContext, docstring: str) -> float:
        """Check if all parameters are documented"""
        if not context.parameters:
            return 1.0
        
        documented = 0
        doc_lower = docstring.lower()
        
        for param in context.parameters:
            if param.name in doc_lower:
                documented += 1
        
        return documented / len(context.parameters)
    
    def _check_return_coverage(self, context: CodeContext, docstring: str) -> float:
        """Check if return value is documented"""
        if not context.returns or context.returns.inferred_type == 'None':
            return 1.0
        
        doc_lower = docstring.lower()
        keywords = ['returns', 'return', 'yields', 'generator']
        
        if any(k in doc_lower for k in keywords):
            return 1.0
        return 0.0
    
    def _check_exception_coverage(self, context: CodeContext, docstring: str) -> float:
        """Check if exceptions are documented"""
        if not context.raises:
            return 1.0
        
        documented = 0
        doc_lower = docstring.lower()
        
        for exc in context.raises:
            if exc.exception_type.lower() in doc_lower:
                documented += 1
        
        return documented / len(context.raises)
    
    def _check_clarity(self, docstring: str) -> float:
        """Check docstring clarity metrics"""
        score = 0.0
        
        # Check length (not too short, not too long)
        words = len(docstring.split())
        if 10 <= words <= 200:
            score += 0.3
        
        # Check for complete sentences
        sentences = docstring.split('.')
        if len(sentences) >= 2:
            score += 0.3
        
        # Check formatting
        if '"""' in docstring:
            score += 0.2
        
        # Check for Args/Returns sections
        if 'Args:' in docstring or 'Parameters' in docstring:
            score += 0.2
        
        return min(1.0, score)
