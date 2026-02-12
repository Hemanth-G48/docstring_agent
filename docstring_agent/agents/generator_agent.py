from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
from ..models.code_context import CodeContext, DocstringStyle

class DocstringSuggestion(BaseModel):
    summary: str = Field(description="One-line summary of what the code does")
    description: str = Field(description="Detailed description of the behavior")
    args_description: List[str] = Field(description="Description of each argument")
    returns_description: str = Field(description="Description of return value")
    raises_description: List[str] = Field(description="Description of exceptions raised")
    side_effects: List[str] = Field(description="Any side effects the code has")
    example: Optional[str] = Field(description="Optional example usage")

class GeneratorAgent:
    """LLM-based docstring generator with multiple style support"""
    
    def __init__(self, model_name="gpt-4", temperature=0.2):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.output_parser = PydanticOutputParser(pydantic_object=DocstringSuggestion)
        
    def generate(self, context: CodeContext, style: DocstringStyle) -> str:
        """Generate docstring based on code context and style"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Python documentation generator. 
            Generate clear, accurate, and comprehensive docstrings.
            Focus on understanding the code's intent, not just syntax.
            Follow the specified docstring style exactly."""),
            
            ("human", """
            Generate a docstring for this {element_type}: {name}
            
            Code:
            ```
            {code}
            ```
            
            Context:
            - Parameters: {parameters}
            - Return type: {return_type}
            - Exceptions: {exceptions}
            - Existing docstring: {existing_docstring}
            - Complexity: {complexity}
            
            Style: {style}
            
            {format_instructions}
            
            Ensure the docstring is:
            1. Accurate - matches actual behavior
            2. Clear - easy to understand
            3. Complete - covers parameters, returns, raises
            4. Concise - no unnecessary information
            """)
        ])
        
        chain = prompt | self.llm | self.output_parser
        
        try:
            result = chain.invoke({
                "element_type": context.element_type.value,
                "name": context.name,
                "code": context.source_code,
                "parameters": self._format_parameters(context.parameters),
                "return_type": context.returns.inferred_type if context.returns else "None",
                "exceptions": [e.exception_type for e in context.raises],
                "existing_docstring": context.existing_docstring or "None",
                "complexity": context.complexity_score or "Unknown",
                "style": style.value,
                "format_instructions": self.output_parser.get_format_instructions()
            })
            
            return self._format_docstring(result, context, style)
            
        except Exception as e:
            return self._fallback_generate(context, style)
    
    def _format_parameters(self, parameters: List) -> str:
        """Format parameters for display in prompt"""
        if not parameters:
            return "None"
        return ", ".join([f"{p.name} ({p.inferred_type or p.type_hint or 'Any'})" for p in parameters])
    
    def _format_docstring(self, suggestion: DocstringSuggestion, 
                          context: CodeContext, 
                          style: DocstringStyle) -> str:
        """Format docstring according to specified style"""
        
        if style == DocstringStyle.GOOGLE:
            return self._format_google(suggestion, context)
        elif style == DocstringStyle.NUMPY:
            return self._format_numpy(suggestion, context)
        else:
            return self._format_rst(suggestion, context)
    
    def _format_google(self, suggestion: DocstringSuggestion, context: CodeContext) -> str:
        """Google style docstring"""
        lines = [f'"""{suggestion.summary}']
        
        if suggestion.description:
            lines.append('')
            lines.append(suggestion.description)
        
        if context.parameters:
            lines.append('')
            lines.append('Args:')
            for param, desc in zip(context.parameters, suggestion.args_description):
                type_str = param.inferred_type or param.type_hint or 'Any'
                lines.append(f'    {param.name} ({type_str}): {desc}')
        
        if context.returns and context.returns.inferred_type != 'None':
            lines.append('')
            lines.append('Returns:')
            return_type = context.returns.inferred_type or 'Any'
            lines.append(f'    {return_type}: {suggestion.returns_description}')
        
        if context.raises:
            lines.append('')
            lines.append('Raises:')
            for exc, desc in zip(context.raises, suggestion.raises_description):
                lines.append(f'    {exc.exception_type}: {desc}')
        
        if suggestion.side_effects:
            lines.append('')
            lines.append('Note:')
            for effect in suggestion.side_effects:
                lines.append(f'    {effect}')
        
        lines.append('"""')
        return '\n'.join(lines)
    
    def _format_numpy(self, suggestion: DocstringSuggestion, context: CodeContext) -> str:
        """NumPy style docstring"""
        lines = [f'"""{suggestion.summary}']
        
        if suggestion.description:
            lines.append('')
            lines.append(suggestion.description)
        
        if context.parameters:
            lines.append('')
            lines.append('Parameters')
            lines.append('----------')
            for param, desc in zip(context.parameters, suggestion.args_description):
                type_str = param.inferred_type or param.type_hint or 'Any'
                lines.append(f'{param.name} : {type_str}')
                lines.append(f'    {desc}')
        
        if context.returns and context.returns.inferred_type != 'None':
            lines.append('')
            lines.append('Returns')
            lines.append('-------')
            return_type = context.returns.inferred_type or 'Any'
            lines.append(f'{return_type}')
            lines.append(f'    {suggestion.returns_description}')
        
        lines.append('"""')
        return '\n'.join(lines)
    
    def _format_rst(self, suggestion: DocstringSuggestion, context: CodeContext) -> str:
        """reStructuredText style docstring"""
        lines = [f'"""{suggestion.summary}']
        
        if suggestion.description:
            lines.append('')
            lines.append(suggestion.description)
        
        if context.parameters:
            lines.append('')
            lines.append(':param:')
            for param, desc in zip(context.parameters, suggestion.args_description):
                type_str = param.inferred_type or param.type_hint or 'Any'
                lines.append(f'    :param {param.name}: {desc}')
                lines.append(f'    :type {param.name}: {type_str}')
        
        if context.returns and context.returns.inferred_type != 'None':
            lines.append('')
            return_type = context.returns.inferred_type or 'Any'
            lines.append(f':returns: {suggestion.returns_description}')
            lines.append(f':rtype: {return_type}')
        
        lines.append('"""')
        return '\n'.join(lines)
    
    def _fallback_generate(self, context: CodeContext, style: DocstringStyle) -> str:
        """Rule-based fallback when LLM fails"""
        lines = [f'"""{context.name} function.']
        
        if context.parameters:
            lines.append('')
            lines.append('Args:')
            for param in context.parameters:
                lines.append(f'    {param.name}: Description missing')
        
        if context.returns and context.returns.inferred_type != 'None':
            lines.append('')
            lines.append('Returns:')
            lines.append(f'    {context.returns.inferred_type or "Any"}: Description missing')
        
        lines.append('"""')
        return '\n'.join(lines)
