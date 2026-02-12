from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
import time
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from ..core.ast_analyzer import CodeAnalyzer
from ..agents.generator_agent import GeneratorAgent
from ..agents.critic_agent import CriticAgent
from ..core.docstring_injector import DocstringInjector
from ..models.code_context import CodeContext, DocstringStyle
from ..models.docstring_result import DocstringResult
from ..utils.confidence_scorer import ConfidenceScorer

console = Console()

class DocstringOrchestrator:
    """Orchestrates multi-agent docstring generation with self-refinement"""
    
    def __init__(self, 
                 style: DocstringStyle = DocstringStyle.GOOGLE,
                 max_iterations: int = 3,
                 quality_threshold: float = 0.8,
                 skip_existing: bool = True):
        
        self.style = style
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold
        self.skip_existing = skip_existing
        
        self.analyzer = CodeAnalyzer()
        self.generator = GeneratorAgent()
        self.critic = CriticAgent()
        self.injector = DocstringInjector()
        self.confidence_scorer = ConfidenceScorer()
        
    def process_file(self, file_path: str, overwrite: bool = False) -> str:
        """Process a single Python file"""
        
        console.print(f"\n[bold blue]📄 Processing: {file_path}[/bold blue]")
        
        with open(file_path, 'r') as f:
            source_code = f.read()
        
        # Analyze code
        contexts = self.analyzer.analyze(source_code)
        console.print(f"[green]✓ Found {len(contexts)} functions/classes[/green]")
        
        # Generate docstrings
        results = []
        with Progress() as progress:
            task = progress.add_task("[cyan]Generating docstrings...", total=len(contexts))
            
            for context in contexts:
                # Skip if already has docstring and not overwriting
                if self.skip_existing and context.existing_docstring and not overwrite:
                    console.print(f"[yellow]⏭ Skipping {context.name} (existing docstring)[/yellow]")
                    progress.advance(task)
                    continue
                
                result = self._process_element(context)
                results.append(result)
                progress.advance(task)
        
        # Generate report
        self._show_report(results)
        
        # Inject docstrings
        enhanced_code = self.injector.inject_docstrings(source_code, results)
        
        return enhanced_code
    
    def _process_element(self, context: CodeContext) -> DocstringResult:
        """Process a single code element with self-refinement loop"""
        
        start_time = time.time()
        best_docstring = None
        best_score = 0
        iterations = []
        
        for i in range(self.max_iterations):
            console.print(f"  [dim]Iteration {i+1} for {context.name}...[/dim]")
            
            # Generate docstring
            docstring = self.generator.generate(context, self.style)
            
            # Review quality
            review = self.critic.review(context.source_code, docstring, context)
            
            # Calculate confidence
            confidence = self.confidence_scorer.calculate(
                context, docstring, review
            )
            
            iteration_result = DocstringResult(
                element_name=context.name,
                generated_docstring=docstring,
                confidence_score=confidence,
                style=self.style.value,
                reasoning=f"Generated via LangChain with critic review (score: {review.score})",
                warnings=review.issues,
                processing_time=time.time() - start_time,
                improved_from=best_docstring if best_docstring else None,
                iteration=i+1
            )
            
            iterations.append(iteration_result)
            
            # Track best
            if confidence > best_score:
                best_docstring = docstring
                best_score = confidence
            
            # Check if quality threshold met
            if confidence >= self.quality_threshold:
                console.print(f"  [green]✓ Quality threshold met ({confidence:.2f})[/green]")
                break
            
            # Prepare for next iteration with critic feedback
            if i < self.max_iterations - 1:
                context.existing_docstring = docstring
                context.body_summary = "\n".join(review.suggestions[:3])
        
        return iteration_result
    
    def _show_report(self, results: List[DocstringResult]):
        """Display generation report"""
        
        if not results:
            console.print("[yellow]No docstrings generated[/yellow]")
            return
        
        table = Table(title="Docstring Generation Report")
        table.add_column("Function", style="cyan")
        table.add_column("Confidence", style="green")
        table.add_column("Iterations", style="yellow")
        table.add_column("Warnings", style="red")
        table.add_column("Time (s)", style="white")
        
        for r in results:
            table.add_row(
                r.element_name,
                f"{r.confidence_score:.2%}",
                str(r.iteration),
                str(len(r.warnings)),
                f"{r.processing_time:.2f}"
            )
        
        console.print(table)
        
        # Summary statistics
        avg_confidence = sum(r.confidence_score for r in results) / len(results)
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  • Average Confidence: {avg_confidence:.2%}")
        console.print(f"  • Total Elements: {len(results)}")
        console.print(f"  • Style: {self.style.value}")
