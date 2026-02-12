import ast
import astor
from typing import List, Optional, Dict, Any
from ..models.code_context import *
import re

class CodeAnalyzer:
    """Advanced AST analyzer with type inference and complexity metrics"""
    
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
        """Extract all functions and classes with context"""
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
        """Analyze a single function with deep type inference"""
        
        # Extract parameters with type inference
        parameters = []
        for arg in node.args.args:
            param = Parameter(
                name=arg.arg,
                type_hint=self._get_type_hint(arg),
                inferred_type=self._infer_parameter_type(node, arg.arg)
            )
            
            # Check for default value
            if node.args.defaults:
                default_index = len(node.args.args) - len(node.args.defaults)
                if node.args.args.index(arg) >= default_index:
                    default_node = node.args.defaults[node.args.args.index(arg) - default_index]
                    param.default_value = astor.to_source(default_node).strip()
            
            parameters.append(param)
        
        # Analyze return statements
        returns = self._analyze_returns(node)
        
        # Detect exceptions
        raises = self._detect_exceptions(node)
        
        # Calculate complexity
        complexity = self._calculate_complexity(node)
        
        # Get existing docstring
        existing_doc = ast.get_docstring(node)
        
        # Check if async
        is_async = isinstance(node, ast.AsyncFunctionDef)
        
        return CodeContext(
            element_type=CodeElementType.FUNCTION,
            name=node.name,
            qualified_name=self._get_qualified_name(node),
            parameters=parameters,
            returns=returns,
            raises=raises,
            existing_docstring=existing_doc,
            source_code=astor.to_source(node).strip(),
            line_number=node.lineno,
            complexity_score=complexity,
            decorators=[astor.to_source(d).strip() for d in node.decorator_list],
            is_async=is_async
        )
    
    def _analyze_class(self, node: ast.ClassDef, source_code: str) -> List[CodeContext]:
        """Analyze a class and its methods"""
        contexts = []
        
        # Analyze class-level docstring
        existing_doc = ast.get_docstring(node)
        
        # Analyze methods
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
        """Extract type hint from argument annotation"""
        if arg.annotation:
            return astor.to_source(arg.annotation).strip()
        return None
    
    def _get_qualified_name(self, node) -> str:
        """Get fully qualified function name"""
        return node.name
    
    def _infer_parameter_type(self, node, param_name: str) -> Optional[str]:
        """Infer parameter type based on usage in function body"""
        type_scores = {t: 0 for t in self.type_patterns.keys()}
        
        for child in ast.walk(node):
            if isinstance(child, ast.BinOp) and isinstance(child.left, ast.Name):
                if child.left.id == param_name:
                    if isinstance(child.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                        type_scores['int'] += 2
                        type_scores['float'] += 1
                    elif isinstance(child.op, ast.Mod):
                        type_scores['int'] += 2
                        type_scores['float'] += 1
            
            elif isinstance(child, ast.Call):
                for arg in child.args:
                    if isinstance(arg, ast.Name) and arg.id == param_name:
                        if isinstance(child.func, ast.Name):
                            if child.func.id in ['int', 'float', 'str', 'list', 'dict']:
                                type_scores[child.func.id] += 3
                            elif child.func.id in ['len', 'sum', 'max', 'min']:
                                type_scores['list'] += 2
                                type_scores['tuple'] += 2
        
        # Return highest scoring type
        if type_scores and max(type_scores.values()) > 0:
            best_type = max(type_scores.items(), key=lambda x: x[1])[0]
            return best_type
        return None
    
    def _analyze_returns(self, node) -> ReturnInfo:
        """Analyze return statements to infer return type"""
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
                    # Infer return type
                    for type_name, pattern in self.type_patterns.items():
                        source_str = astor.to_source(child.value).strip()
                        if re.match(pattern, source_str):
                            return_types.add(type_name)
        
        if return_types:
            return_info.inferred_type = ', '.join(return_types)
        
        return return_info
    
    def _detect_exceptions(self, node) -> List[ExceptionInfo]:
        """Detect raised exceptions"""
        exceptions = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Raise):
                if child.exc:
                    if isinstance(child.exc, ast.Call):
                        if isinstance(child.exc.func, ast.Name):
                            exceptions.append(
                                ExceptionInfo(
                                    exception_type=child.exc.func.id
                                )
                            )
        
        return exceptions
    
    def _calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, 
                                  ast.ExceptHandler, ast.With,
                                  ast.Assert, ast.BoolOp)):
                complexity += 1
        
        return complexity
