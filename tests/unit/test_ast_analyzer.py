import ast
import pytest
from docstring_agent.core.ast_analyzer import CodeAnalyzer
from docstring_agent.models.code_context import CodeElementType

class TestCodeAnalyzer:
    def setup_method(self):
        self.analyzer = CodeAnalyzer()
    
    def test_simple_function(self):
        code = """
def add(a, b):
    return a + b
"""
        contexts = self.analyzer.analyze(code)
        assert len(contexts) == 1
        assert contexts[0].name == "add"
        assert contexts[0].element_type == CodeElementType.FUNCTION
        assert len(contexts[0].parameters) == 2
    
    def test_function_with_type_hints(self):
        code = """
def greet(name: str, age: int) -> str:
    return f"Hello {name}, you are {age}"
"""
        contexts = self.analyzer.analyze(code)
        assert len(contexts) == 1
        assert contexts[0].parameters[0].type_hint == "str"
        assert contexts[0].parameters[1].type_hint == "int"
    
    def test_class_with_methods(self):
        code = """
class Calculator:
    def __init__(self):
        self.value = 0
    
    def add(self, x):
        self.value += x
        return self.value
"""
        contexts = self.analyzer.analyze(code)
        # Should have __init__ and add methods
        assert len(contexts) == 2
        assert any(c.name == "__init__" for c in contexts)
        assert any(c.name == "add" for c in contexts)
    
    def test_type_inference(self):
        code = """
def process(data):
    result = data + 1
    return result * 2
"""
        contexts = self.analyzer.analyze(code)
        # Should infer int type based on arithmetic operations
        assert contexts[0].parameters[0].inferred_type is not None
    
    def test_complexity_calculation(self):
        code = """
def complex_logic(x):
    if x > 0:
        if x % 2 == 0:
            return "positive even"
        else:
            return "positive odd"
    elif x < 0:
        return "negative"
    else:
        return "zero"
"""
        contexts = self.analyzer.analyze(code)
        # Should have complexity > 1 due to multiple branches
        assert contexts[0].complexity_score > 1
    
    def test_existing_docstring(self):
        code = '''
def documented():
    """This is a docstring."""
    pass
'''
        contexts = self.analyzer.analyze(code)
        assert contexts[0].existing_docstring == "This is a docstring."
    
    def test_async_function(self):
        code = """
async def fetch_data(url):
    return await http.get(url)
"""
        contexts = self.analyzer.analyze(code)
        assert contexts[0].is_async is True
