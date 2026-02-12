import ast
import astor
from typing import List
from ..models.docstring_result import DocstringResult

class DocstringInjector:
    """Inject generated docstrings into source code"""
    
    def inject_docstrings(self, source_code: str, 
                         results: List[DocstringResult]) -> str:
        """Inject docstrings at correct positions"""
        
        tree = ast.parse(source_code)
        
        # Create a mapping of function names to docstrings
        docstring_map = {r.element_name: r.generated_docstring for r in results}
        
        # Modify AST to add docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name in docstring_map:
                    self._add_docstring(node, docstring_map[node.name])
        
        # Convert back to source code
        return astor.to_source(tree)
    
    def _add_docstring(self, node, docstring: str):
        """Add docstring to AST node"""
        
        # Parse docstring into AST
        docstring_expr = ast.Expr(value=ast.Constant(value=docstring))
        
        # Remove existing docstring if present
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            node.body.pop(0)
        
        # Insert new docstring at beginning
        node.body.insert(0, docstring_expr)
