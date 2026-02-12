"""Entry point for the docstring generation agent CLI."""

import typer
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress

from .agents import DocstringOrchestrator
from .models import DocstringStyle
from .config import Config

app = typer.Typer(help="AI-powered Python docstring generator")
console = Console()


@app.command()
def generate(
    file_path: Path = typer.Argument(..., help="Python file to process"),
    style: DocstringStyle = typer.Option(DocstringStyle.GOOGLE, help="Docstring style"),
    output: Optional[Path] = typer.Option(None, help="Output file path"),
    overwrite: bool = typer.Option(False, help="Overwrite existing docstrings"),
    max_iterations: int = typer.Option(3, help="Max refinement iterations"),
    threshold: float = typer.Option(0.8, help="Quality threshold (0-1)"),
    diff: bool = typer.Option(False, help="Show diff preview"),
):
    """Generate docstrings for Python files using AI agents."""
    
    orchestrator = DocstringOrchestrator(
        style=style,
        max_iterations=max_iterations,
        quality_threshold=threshold
    )
    
    # Generate docstrings
    enhanced_code = orchestrator.process_file(str(file_path), overwrite)
    
    # Show diff if requested
    if diff:
        with open(file_path, 'r') as f:
            original = f.read()
        
        console.print("\n[bold]Changes Preview:[/bold]")
        if original != enhanced_code:
            console.print("[green]Docstrings added/updated[/green]")
    
    # Save or display
    if output:
        with open(output, 'w') as f:
            f.write(enhanced_code)
        console.print(f"\n[green]Saved to {output}[/green]")
    else:
        # Write back to original file
        with open(file_path, 'w') as f:
            f.write(enhanced_code)
        console.print(f"\n[green]Updated {file_path}[/green]")
        
        # Show preview
        syntax = Syntax(enhanced_code, "python", theme="monokai")
        console.print(syntax)


@app.command()
def batch(
    directory: Path = typer.Argument(..., help="Directory to process"),
    style: DocstringStyle = typer.Option(DocstringStyle.GOOGLE, help="Docstring style"),
    recursive: bool = typer.Option(True, help="Process subdirectories"),
):
    """Process all Python files in a directory."""
    
    pattern = "**/*.py" if recursive else "*.py"
    py_files = list(directory.glob(pattern))
    
    console.print(f"[bold]Found {len(py_files)} Python files[/bold]")
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Processing files...", total=len(py_files))
        
        for file_path in py_files:
            try:
                orchestrator = DocstringOrchestrator(style=style)
                enhanced_code = orchestrator.process_file(str(file_path))
                
                # Save back to file
                with open(file_path, 'w') as f:
                    f.write(enhanced_code)
                    
                console.print(f"[green]Updated {file_path}[/green]")
                
            except Exception as e:
                console.print(f"[red]Failed {file_path}: {e}[/red]")
            
            progress.advance(task)


@app.command()
def server(
    host: str = typer.Option("0.0.0.0", help="Host to bind"),
    port: int = typer.Option(8000, help="Port to bind"),
):
    """Start a local web server with API endpoint."""
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
        import uvicorn
    except ImportError:
        console.print("[red]FastAPI and uvicorn required. Run: pip install fastapi uvicorn[/red]")
        raise typer.Exit(1)
    
    fastapi_app = FastAPI(title="Docstring Generator Agent")
    
    class CodeRequest(BaseModel):
        code: str
        style: str = "google"
    
    @fastapi_app.post("/generate")
    async def generate_docstring(request: CodeRequest):
        orchestrator = DocstringOrchestrator(
            style=DocstringStyle(request.style)
        )
        
        try:
            enhanced_code = orchestrator.process_code(request.code)
            return {"success": True, "code": enhanced_code}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    console.print("[bold green]Starting docstring API server...[/bold green]")
    console.print(f"[blue]API Documentation: http://{host}:{port}/docs[/blue]")
    uvicorn.run(fastapi_app, host=host, port=port)


@app.command()
def analyze(
    file_path: Path = typer.Argument(..., help="Python file to analyze"),
):
    """Analyze code structure without generating docstrings."""
    from .tools import CodeAnalyzer
    
    analyzer = CodeAnalyzer()
    
    with open(file_path, 'r') as f:
        source_code = f.read()
    
    contexts = analyzer.analyze(source_code)
    
    table = Table(title=f"Code Analysis: {file_path}")
    table.add_column("Element", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Parameters", style="yellow")
    table.add_column("Complexity", style="red")
    
    for ctx in contexts:
        params = ", ".join([p.name for p in ctx.parameters]) or "None"
        table.add_row(
            ctx.name,
            ctx.element_type.value,
            params,
            str(ctx.complexity_score or "N/A")
        )
    
    console.print(table)


if __name__ == "__main__":
    app()
