import typer
from rich.console import Console
from rich.table import Table
from operator_cli.core.models.context import ContextManager
from operator_cli.core.utils import get_project_root

app = typer.Typer(help="Configure Operator CLI settings.", rich_markup_mode="rich")

@app.command(name="models")
def list_models():
    """List available local LLM models (Ollama)."""
    import ollama
    console = Console()
    try:
        client = ollama.Client()
        models_resp = client.list()
        
        PROJECT_ROOT = get_project_root()
        ctx_mgr = ContextManager(context_path=str(PROJECT_ROOT / ".operator_context.json"))
        current_model = ctx_mgr.get_default_model()
        
        table = Table(title="Available Local LLMs (Ollama)")
        table.add_column("Status", style="bold green", justify="center")
        table.add_column("Name", style="cyan")
        table.add_column("Size (GB)", style="magenta")
        table.add_column("Family", style="blue")
        
        models = models_resp.get('models', [])
        if not models:
            console.print("[yellow]No models found in Ollama.[/yellow]")
            return

        for model in models:
            # Defensive attribute/key access for different ollama-python versions
            if isinstance(model, dict):
                name = model.get('model', model.get('name', 'N/A'))
                size = model.get('size', 0)
                details = model.get('details', {})
                family = details.get('family', 'N/A')
            else:
                name = getattr(model, 'model', getattr(model, 'name', 'N/A'))
                size = getattr(model, 'size', 0)
                details = getattr(model, 'details', {})
                family = details.get('family', 'N/A') if isinstance(details, dict) else getattr(details, 'family', 'N/A')

            # Match logic: exact match or name-only match (without :latest)
            is_active = ""
            if name == current_model:
                is_active = "*"
            elif ":" in name and name.split(':')[0] == current_model:
                is_active = "*"
            elif ":" not in current_model and f"{current_model}:latest" == name:
                is_active = "*"
            
            size_gb = size / (1024**3)
            
            table.add_row(
                is_active,
                name,
                f"{size_gb:.2f}",
                family
            )
        console.print(table)
        console.print(f"\n[dim]* Current default model: [bold cyan]{current_model}[/bold cyan][/dim]")
    except Exception as e:
        console.print(f"[bold red]Error listing models:[/bold red] {e}")

@app.command(name="set-model")
def set_model(model_name: str = typer.Argument(..., help="변경할 로컬 LLM 모델 이름")):
    """Set the default local LLM model."""
    console = Console()
    PROJECT_ROOT = get_project_root()
    ctx_mgr = ContextManager(context_path=str(PROJECT_ROOT / ".operator_context.json"))
    
    # Verify if model exists in Ollama
    import ollama
    try:
        client = ollama.Client()
        models_resp = client.list()
        models = models_resp.get('models', [])
        available_models = []
        for m in models:
            if isinstance(m, dict):
                available_models.append(m.get('model', m.get('name', '')))
            else:
                available_models.append(getattr(m, 'model', getattr(m, 'name', '')))
        
        if model_name not in available_models:
            # Try with :latest suffix if not provided
            if ":" not in model_name and f"{model_name}:latest" in available_models:
                model_name = f"{model_name}:latest"
            else:
                console.print(f"[bold yellow]Warning:[/bold yellow] Model '[bold cyan]{model_name}[/bold cyan]' not found in your Ollama library.")
                console.print(f"Use [cyan]'operator setting models'[/cyan] to see available models.")
                if not typer.confirm("Do you want to set it anyway?"):
                    return
    except Exception as e:
        pass # Silently continue if Ollama is not running or other errors occur

    ctx_mgr.save_context(default_model=model_name)
    console.print(f"[bold green]✓[/bold green] Default local LLM has been set to: [bold cyan]{model_name}[/bold cyan]")

@app.command(name="graphify-delay")
def set_graphify_delay(minutes: int = typer.Argument(..., help="Graphify 자동 업데이트 유예 시간 (분)")):
    """Set the delay for automatic Graphify updates after knowledge changes."""
    console = Console()
    PROJECT_ROOT = get_project_root()
    ctx_mgr = ContextManager(context_path=str(PROJECT_ROOT / ".operator_context.json"))
    
    ctx_mgr.save_context(graphify_delay=minutes)
    console.print(f"[bold green]✓[/bold green] Graphify auto-update delay has been set to: [bold cyan]{minutes}[/bold cyan] minutes")
