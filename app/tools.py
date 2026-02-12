"""Tools and utilities for code analysis and docstring generation."""

import ast
import re
from typing import List, Optional

from .models import (
    CodeContext,
    CodeElementType,
    Parameter,
    ReturnInfo,
    ExceptionInfo,
    DocstringResult,
    CriticReview,
)


class CodeAnalyzer:
    """Advanced AST analyzer with type inference and complexity metrics."""
    
    def __init__(self):
        self.type_patterns = {
            'int': r'[+\-*/%]|\d+',
            'float': r'\d+\.\d+',
            'str': r'[\'"].*?[\'"]|str\(|\.format|\+[ ]*[\'"]',
            'bool': r'==|!=|<|>|is |not |True|False',
            'list': r'\[.*\]|list\(|\.append|\.extend',
            'dict': r'\{.*:.*\}|dict\(|\.keys\(\)|\.values\(\)',
            'set': r'\{.*\}|set\(\)',
            'tuple': r'\(.*,.*\)',
        }
    
    def analyze(self, source_code: str) -> List[CodeContext]:
        """Extract all functions and classes with context."""
        tree = ast.parse(source_code)
        contexts = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                context = self._analyze_function(node, source_code)
                contexts.append(context)
            elif isinstance(node, ast.ClassDef):
                contexts.extend(self._analyze_class(node, source_code))
        
        return contexts
    
    def _analyze_function(self, node, source_code: str) -> CodeContext:
        """Analyze a single function with deep type inference."""
        parameters = []
        for arg in node.args.args:
            param = Parameter(
                name=arg.arg,
                type_hint=self._get_type_hint(arg),
                inferred_type=self._infer_parameter_type(node, arg.arg)
            )
            parameters.append(param)
        
        returns = self._analyze_returns(node)
        raises = self._detect_exceptions(node)
        complexity = self._calculate_complexity(node)
        existing_doc = ast.get_docstring(node)
        is_async = isinstance(node, ast.AsyncFunctionDef)
        
        return CodeContext(
            element_type=CodeElementType.FUNCTION,
            name=node.name,
            qualified_name=node.name,
            parameters=parameters,
            returns=returns,
            raises=raises,
            existing_docstring=existing_doc,
            source_code=ast.unparse(node).strip(),
            line_number=node.lineno,
            complexity_score=complexity,
            decorators=[ast.unparse(d).strip() for d in node.decorator_list],
            is_async=is_async
        )
    
    def _analyze_class(self, node: ast.ClassDef, source_code: str) -> List[CodeContext]:
        """Analyze a class and its methods."""
        contexts = []
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_context = self._analyze_function(item, source_code)
                method_context.element_type = (
                    CodeElementType.CONSTRUCTOR if item.name == '__init__' 
                    else CodeElementType.METHOD
                )
                method_context.qualified_name = f"{node.name}.{item.name}"
                contexts.append(method_context)
        
        return contexts
    
    def _get_type_hint(self, arg) -> Optional[str]:
        """Extract type hint from argument annotation."""
        if arg.annotation:
            return ast.unparse(arg.annotation).strip()
        return None
    
    def _infer_parameter_type(self, node, param_name: str) -> Optional[str]:
        """Infer parameter type based on usage in function body."""
        type_scores = {t: 0 for t in self.type_patterns.keys()}
        
        for child in ast.walk(node):
            if isinstance(child, ast.BinOp) and isinstance(child.left, ast.Name):
                if child.left.id == param_name:
                    if isinstance(child.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                        type_scores['int'] += 2
                        type_scores['float'] += 1
            
            elif isinstance(child, ast.Call):
                for arg in child.args:
                    if isinstance(arg, ast.Name) and arg.id == param_name:
                        if isinstance(child.func, ast.Name):
                            if child.func.id in ['int', 'float', 'str', 'list', 'dict']:
                                type_scores[child.func.id] += 3
        
        if type_scores and max(type_scores.values()) > 0:
            best_type = max(type_scores.items(), key=lambda x: x[1])[0]
            return best_type
        return None
    
    def _analyze_returns(self, node) -> ReturnInfo:
        """Analyze return statements to infer return type."""
        return_info = ReturnInfo()
        return_types = set()
        
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value:
                if isinstance(child.value, ast.Tuple):
                    return_info.is_multiple = True
                    return_types.add('tuple')
                elif isinstance(child.value, ast.Yield):
                    return_info.is_generator = True
                    return_types.add('generator')
                else:
                    source_str = ast.unparse(child.value).strip()
                    for type_name, pattern in self.type_patterns.items():
                        if re.match(pattern, source_str):
                            return_types.add(type_name)
        
        if return_types:
            return_info.inferred_type = ', '.join(return_types)
        
        return return_info
    
    def _detect_exceptions(self, node) -> List[ExceptionInfo]:
        """Detect raised exceptions."""
        exceptions = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Raise):
                if child.exc:
                    if isinstance(child.exc, ast.Call):
                        if isinstance(child.exc.func, ast.Name):
                            exceptions.append(
                                ExceptionInfo(exception_type=child.exc.func.id)
                            )
        
        return exceptions
    
    def _calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, 
                                  ast.ExceptHandler, ast.With,
                                  ast.Assert, ast.BoolOp)):
                complexity += 1
        
        return complexity


class DocstringInjector:
    """Inject generated docstrings into source code."""
    
    def inject_docstrings(self, source_code: str, 
                         results: List[DocstringResult]) -> str:
        """Inject docstrings at correct positions."""
        tree = ast.parse(source_code)
        
        # Create a mapping of function names to docstrings
        docstring_map = {r.element_name: r.generated_docstring for r in results}
        
        # Modify AST to add docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name in docstring_map:
                    self._add_docstring(node, docstring_map[node.name])
        
        # Convert back to source code
        return ast.unparse(tree)
    
    def _add_docstring(self, node, docstring: str):
        """Add docstring to AST node."""
        docstring_expr = ast.Expr(value=ast.Constant(value=docstring))
        
        # Remove existing docstring if present
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            node.body.pop(0)
        
        # Insert new docstring at beginning
        node.body.insert(0, docstring_expr)


class ConfidenceScorer:
    """Calculate confidence scores for generated docstrings."""
    
    def calculate(self, context: CodeContext, 
                 docstring: str, 
                 review: CriticReview) -> float:
        """Calculate weighted confidence score."""
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
        """Check if all parameters are documented."""
        if not context.parameters:
            return 1.0
        
        documented = 0
        doc_lower = docstring.lower()
        
        for param in context.parameters:
            if param.name in doc_lower:
                documented += 1
        
        return documented / len(context.parameters)
    
    def _check_return_coverage(self, context: CodeContext, docstring: str) -> float:
        """Check if return value is documented."""
        if not context.returns or context.returns.inferred_type == 'None':
            return 1.0
        
        doc_lower = docstring.lower()
        keywords = ['returns', 'return', 'yields', 'generator']
        
        if any(k in doc_lower for k in keywords):
            return 1.0
        return 0.0
    
    def _check_exception_coverage(self, context: CodeContext, docstring: str) -> float:
        """Check if exceptions are documented."""
        if not context.raises:
            return 1.0
        
        documented = 0
        doc_lower = docstring.lower()
        
        for exc in context.raises:
            if exc.exception_type.lower() in doc_lower:
                documented += 1
        
        return documented / len(context.raises)
    
    def _check_clarity(self, docstring: str) -> float:
        """Check docstring clarity metrics."""
        score = 0.0
        
        # Check length
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
