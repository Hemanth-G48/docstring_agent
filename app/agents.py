"""Multi-agent system for docstring generation."""

import time
from typing import List, Optional

from .models import (
    CodeContext,
    DocstringStyle,
    DocstringResult,
    CriticReview,
    DocstringSuggestion,
)
from .tools import CodeAnalyzer, DocstringInjector, ConfidenceScorer
from .config import get_config


class GeneratorAgent:
    """LLM-based docstring generator with multiple style support."""
    
    def __init__(self, model_name: str = None, temperature: float = None):
        config = get_config()
        self.model_name = model_name or config.default_model
        self.temperature = temperature or config.default_temperature
    
    def generate(self, context: CodeContext, style: DocstringStyle) -> str:
        """Generate docstring based on code context and style."""
        # For now, return a formatted fallback docstring
        # In production, this would use LangChain with LLM
        return self._fallback_generate(context, style)
    
    def _format_parameters(self, parameters: List) -> str:
        """Format parameters for display."""
        if not parameters:
            return "None"
        return ", ".join([f"{p.name} ({p.inferred_type or p.type_hint or 'Any'})" for p in parameters])
    
    def _format_docstring(self, context: CodeContext, style: DocstringStyle) -> str:
        """Format docstring according to specified style."""
        if style == DocstringStyle.GOOGLE:
            return self._format_google(context)
        elif style == DocstringStyle.NUMPY:
            return self._format_numpy(context)
        else:
            return self._format_rst(context)
    
    def _format_google(self, context: CodeContext) -> str:
        """Google style docstring."""
        lines = [f'"""{context.name} function.']
        
        if context.parameters:
            lines.append('')
            lines.append('Args:')
            for param in context.parameters:
                type_str = param.inferred_type or param.type_hint or 'Any'
                lines.append(f'    {param.name} ({type_str}): Description of {param.name}.')
        
        if context.returns and context.returns.inferred_type != 'None':
            lines.append('')
            lines.append('Returns:')
            return_type = context.returns.inferred_type or 'Any'
            lines.append(f'    {return_type}: Description of return value.')
        
        if context.raises:
            lines.append('')
            lines.append('Raises:')
            for exc in context.raises:
                lines.append(f'    {exc.exception_type}: When this exception is raised.')
        
        lines.append('"""')
        return '\n'.join(lines)
    
    def _format_numpy(self, context: CodeContext) -> str:
        """NumPy style docstring."""
        lines = [f'"""{context.name} function.']
        
        if context.parameters:
            lines.append('')
            lines.append('Parameters')
            lines.append('----------')
            for param in context.parameters:
                type_str = param.inferred_type or param.type_hint or 'Any'
                lines.append(f'{param.name} : {type_str}')
                lines.append(f'    Description of {param.name}.')
        
        if context.returns and context.returns.inferred_type != 'None':
            lines.append('')
            lines.append('Returns')
            lines.append('-------')
            return_type = context.returns.inferred_type or 'Any'
            lines.append(f'{return_type}')
            lines.append(f'    Description of return value.')
        
        lines.append('"""')
        return '\n'.join(lines)
    
    def _format_rst(self, context: CodeContext) -> str:
        """reStructuredText style docstring."""
        lines = [f'"""{context.name} function.']
        
        if context.parameters:
            lines.append('')
            for param in context.parameters:
                type_str = param.inferred_type or param.type_hint or 'Any'
                lines.append(f':param {param.name}: Description of {param.name}.')
                lines.append(f':type {param.name}: {type_str}')
        
        if context.returns and context.returns.inferred_type != 'None':
            lines.append('')
            return_type = context.returns.inferred_type or 'Any'
            lines.append(f':returns: Description of return value.')
            lines.append(f':rtype: {return_type}')
        
        lines.append('"""')
        return '\n'.join(lines)
    
    def _fallback_generate(self, context: CodeContext, style: DocstringStyle) -> str:
        """Rule-based fallback when LLM fails."""
        return self._format_docstring(context, style)


class CriticAgent:
    """Self-refining critic agent that evaluates docstring quality."""
    
    def __init__(self, model_name: str = None, temperature: float = None):
        config = get_config()
        self.model_name = model_name or config.default_model
        self.temperature = temperature or 0.1
    
    def review(self, code: str, docstring: str, context: CodeContext) -> CriticReview:
        """Review docstring quality and provide feedback."""
        # Simple rule-based review for now
        # In production, this would use LLM
        
        score = 0.7
        issues = []
        suggestions = []
        
        # Check parameter coverage
        if context.parameters:
            for param in context.parameters:
                if param.name not in docstring.lower():
                    issues.append(f"Parameter '{param.name}' not documented")
                    suggestions.append(f"Add documentation for parameter '{param.name}'")
        
        # Check return documentation
        if context.returns and context.returns.inferred_type != 'None':
            if 'returns' not in docstring.lower():
                issues.append("Return value not documented")
                suggestions.append("Add Returns section")
        
        # Check exception coverage
        if context.raises:
            for exc in context.raises:
                if exc.exception_type.lower() not in docstring.lower():
                    issues.append(f"Exception '{exc.exception_type}' not documented")
        
        # Adjust score based on issues
        if issues:
            score = max(0.4, 0.7 - (len(issues) * 0.1))
        
        return CriticReview(
            score=score,
            issues=issues[:5],
            suggestions=suggestions[:5],
            missing_info=[],
            is_accurate=score > 0.7,
            clarity_score=score * 0.9
        )


class DocstringOrchestrator:
    """Orchestrates multi-agent docstring generation with self-refinement."""
    
    def __init__(self, 
                 style: DocstringStyle = DocstringStyle.GOOGLE,
                 max_iterations: int = None,
                 quality_threshold: float = None,
                 skip_existing: bool = True):
        
        config = get_config()
        self.style = style
        self.max_iterations = max_iterations or config.max_iterations
        self.quality_threshold = quality_threshold or config.quality_threshold
        self.skip_existing = skip_existing
        
        self.analyzer = CodeAnalyzer()
        self.generator = GeneratorAgent()
        self.critic = CriticAgent()
        self.injector = DocstringInjector()
        self.confidence_scorer = ConfidenceScorer()
    
    def process_file(self, file_path: str, overwrite: bool = False) -> str:
        """Process a single Python file."""
        with open(file_path, 'r') as f:
            source_code = f.read()
        
        # Analyze code
        contexts = self.analyzer.analyze(source_code)
        
        # Generate docstrings
        results = []
        for context in contexts:
            # Skip if already has docstring and not overwriting
            if self.skip_existing and context.existing_docstring and not overwrite:
                continue
            
            result = self._process_element(context)
            results.append(result)
        
        # Inject docstrings
        enhanced_code = self.injector.inject_docstrings(source_code, results)
        
        return enhanced_code
    
    def process_code(self, source_code: str, overwrite: bool = False) -> str:
        """Process source code directly."""
        # Analyze code
        contexts = self.analyzer.analyze(source_code)
        
        # Generate docstrings
        results = []
        for context in contexts:
            if self.skip_existing and context.existing_docstring and not overwrite:
                continue
            
            result = self._process_element(context)
            results.append(result)
        
        # Inject docstrings
        enhanced_code = self.injector.inject_docstrings(source_code, results)
        
        return enhanced_code
    
    def _process_element(self, context: CodeContext) -> DocstringResult:
        """Process a single code element with self-refinement loop."""
        start_time = time.time()
        best_docstring = None
        best_score = 0
        iteration_result = None
        
        for i in range(self.max_iterations):
            # Generate docstring
            docstring = self.generator.generate(context, self.style)
            
            # Review quality
            review = self.critic.review(context.source_code, docstring, context)
            
            # Calculate confidence
            confidence = self.confidence_scorer.calculate(context, docstring, review)
            
            iteration_result = DocstringResult(
                element_name=context.name,
                generated_docstring=docstring,
                confidence_score=confidence,
                style=self.style.value,
                reasoning=f"Generated with critic review (score: {review.score})",
                warnings=review.issues,
                processing_time=time.time() - start_time,
                improved_from=best_docstring if best_docstring else None,
                iteration=i+1
            )
            
            # Track best
            if confidence > best_score:
                best_docstring = docstring
                best_score = confidence
            
            # Check if quality threshold met
            if confidence >= self.quality_threshold:
                break
            
            # Prepare for next iteration with critic feedback
            if i < self.max_iterations - 1:
                context.existing_docstring = docstring
                context.body_summary = "\n".join(review.suggestions[:3])
        
        return iteration_result
    
    def get_results(self, file_path: str, overwrite: bool = False) -> List[DocstringResult]:
        """Get docstring results without injecting."""
        with open(file_path, 'r') as f:
            source_code = f.read()
        
        contexts = self.analyzer.analyze(source_code)
        results = []
        
        for context in contexts:
            if self.skip_existing and context.existing_docstring and not overwrite:
                continue
            
            result = self._process_element(context)
            results.append(result)
        
        return results
