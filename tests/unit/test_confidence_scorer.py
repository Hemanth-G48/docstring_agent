import pytest
from docstring_agent.utils.confidence_scorer import ConfidenceScorer
from docstring_agent.models.code_context import CodeContext, CodeElementType, Parameter
from docstring_agent.agents.critic_agent import CriticReview

class TestConfidenceScorer:
    def setup_method(self):
        self.scorer = ConfidenceScorer()
    
    def test_perfect_score(self):
        context = CodeContext(
            element_type=CodeElementType.FUNCTION,
            name="test_func",
            qualified_name="test_func",
            source_code="def test(): pass",
            line_number=1,
            parameters=[Parameter(name="x"), Parameter(name="y")]
        )
        
        docstring = '''"""Test function.

Args:
    x: First parameter
    y: Second parameter

Returns:
    int: Result
"""'''
        
        review = CriticReview(
            score=1.0,
            issues=[],
            suggestions=[],
            missing_info=[],
            is_accurate=True,
            clarity_score=1.0
        )
        
        score = self.scorer.calculate(context, docstring, review)
        assert score >= 0.8
    
    def test_missing_parameters(self):
        context = CodeContext(
            element_type=CodeElementType.FUNCTION,
            name="test_func",
            qualified_name="test_func",
            source_code="def test(a, b): pass",
            line_number=1,
            parameters=[Parameter(name="a"), Parameter(name="b")]
        )
        
        docstring = '"""Test function with no Args section."""'
        
        review = CriticReview(
            score=0.5,
            issues=["Missing parameter documentation"],
            suggestions=["Add Args section"],
            missing_info=["parameter a", "parameter b"],
            is_accurate=True,
            clarity_score=0.6
        )
        
        score = self.scorer.calculate(context, docstring, review)
        assert score < 0.7
    
    def test_no_parameters(self):
        context = CodeContext(
            element_type=CodeElementType.FUNCTION,
            name="test_func",
            qualified_name="test_func",
            source_code="def test(): pass",
            line_number=1,
            parameters=[]
        )
        
        docstring = '"""Simple function."""'
        
        review = CriticReview(
            score=0.8,
            issues=[],
            suggestions=[],
            missing_info=[],
            is_accurate=True,
            clarity_score=0.8
        )
        
        score = self.scorer.calculate(context, docstring, review)
        assert score >= 0.7
