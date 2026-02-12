import pytest
from docstring_agent.core.docstring_injector import DocstringInjector
from docstring_agent.models.docstring_result import DocstringResult

class TestDocstringInjector:
    def setup_method(self):
        self.injector = DocstringInjector()
    
    def test_inject_simple_function(self):
        source_code = "def test():\n    pass"
        results = [
            DocstringResult(
                element_name="test",
                generated_docstring='"""Test function."""',
                confidence_score=0.9,
                style="google",
                reasoning="Test",
                warnings=[],
                processing_time=0.1
            )
        ]
        
        enhanced = self.injector.inject_docstrings(source_code, results)
        assert '"""Test function."""' in enhanced
    
    def test_replace_existing_docstring(self):
        source_code = '''def test():
    """Old docstring."""
    pass'''
        results = [
            DocstringResult(
                element_name="test",
                generated_docstring='"""New docstring."""',
                confidence_score=0.9,
                style="google",
                reasoning="Test",
                warnings=[],
                processing_time=0.1
            )
        ]
        
        enhanced = self.injector.inject_docstrings(source_code, results)
        assert '"""New docstring."""' in enhanced
        assert '"""Old docstring."""' not in enhanced
    
    def test_multiple_functions(self):
        source_code = """
def func1():
    pass

def func2():
    pass
"""
        results = [
            DocstringResult(
                element_name="func1",
                generated_docstring='"""Function 1."""',
                confidence_score=0.9,
                style="google",
                reasoning="Test",
                warnings=[],
                processing_time=0.1
            ),
            DocstringResult(
                element_name="func2",
                generated_docstring='"""Function 2."""',
                confidence_score=0.9,
                style="google",
                reasoning="Test",
                warnings=[],
                processing_time=0.1
            )
        ]
        
        enhanced = self.injector.inject_docstrings(source_code, results)
        assert '"""Function 1."""' in enhanced
        assert '"""Function 2."""' in enhanced
