from pathlib import Path
from typing import Optional
import typer
from operator_cli.core.utils import get_project_root, get_engine, get_circuit_names

app = typer.Typer(
    help="""
    [bold cyan]Circuit Switcher (The Unified 'call')[/bold cyan]
    
    특정 회선으로 연결을 전환하고 해당 프로토콜을 확인합니다.
    - [bold cyan]operator call [node][/bold cyan]: 해당 회선으로 즉시 연결 전환.
    """,
    rich_markup_mode="rich"
)

@app.callback(invoke_without_command=True)
def call(
    node: str = typer.Argument(..., help="전환할 회선 이름 (예: gdr, matrix, research)")
):
    from rich.console import Console
    from rich.panel import Panel
    from operator_cli.core.models.context import ContextManager
    
    console = Console()
    PROJECT_ROOT = get_project_root()
    ctx_mgr = ContextManager(context_path=str(PROJECT_ROOT / ".operator_context.json"))
    proto_engine = get_engine()
    
    available_circuits = get_circuit_names()
    
    if node in available_circuits:
        ctx_mgr.save_context(active_circuit=node)
        full_protocol = proto_engine.get_full_context(node)
        from rich.text import Text
        from operator_cli.core.utils import S_OK
        console.print(f"[bold green]{S_OK}[/bold green] Successfully linked to [bold cyan]{node}[/bold cyan] node.")
        console.print(Panel(Text(full_protocol), title=f"[bold cyan]Active Protocols for {node}[/bold cyan]", border_style="cyan"))
    else:
        console.print(f"[bold red]Error:[/bold red] Circuit '[bold yellow]{node}[/bold yellow]' not found.")
        console.print(f"Available circuits: [gold1]{', '.join(available_circuits)}[/gold1]")
        raise typer.Exit(1)
