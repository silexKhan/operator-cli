import typer
from operator_cli.core.utils import get_project_root, get_engine, get_circuit_names

app = typer.Typer(
    help="""
    [bold blue]Circuit Connection Manager[/bold blue]
    
    회선(Circuit)에 연결하여 프로젝트 전용 프로토콜을 활성화합니다.
    """,
    rich_markup_mode="rich"
)

def get_circuit_list_str():
    """가용한 회선 목록을 실시간으로 스캔하여 도움말 문자열 생성"""
    try:
        circuits = get_circuit_names()
        if circuits:
            return f"(가용: [green]{', '.join(circuits)}[/green])"
    except Exception:
        pass
    return ""

@app.callback(invoke_without_command=True)
def connect(
    circuit: str = typer.Argument(..., help=f"연결할 회선 이름 {get_circuit_list_str()}")
):
    """
    [bold green]Connect[/bold green]: 지정된 회선에 연결하고 해당 프로토콜을 로드합니다.
    """
    from rich.console import Console
    from operator_cli.core.models.context import ContextManager

    console = Console()
    console.print(f"[bold blue]Connecting to circuit:[/bold blue] [green]{circuit}[/green]")
    
    PROJECT_ROOT = get_project_root()
    ctx_mgr = ContextManager(context_path=str(PROJECT_ROOT / ".operator_context.json"))
    proto_engine = get_engine()
    
    ctx_mgr.save_context(active_circuit=circuit)
    full_protocol = proto_engine.get_full_context(circuit)
    
    from rich.panel import Panel
    if full_protocol:
        console.print(f"[bold green]✓[/bold green] Successfully connected to [bold]{circuit}[/bold].")
        console.print(Panel(full_protocol, title=f"[bold cyan]Loaded Protocols for {circuit}[/bold cyan]", border_style="cyan"))
    else:
        console.print(f"[yellow]![/yellow] Warning: Circuit [bold]{circuit}[/bold] connected, but no protocols found.")

@app.command("list")
def list_circuits():
    """
    List all available circuits based on the protocols directory.
    """
    from rich.console import Console
    from rich.table import Table
    from operator_cli.core.utils import get_circuit_list
    
    console = Console()
    circuits = get_circuit_list()
    
    table = Table(title="Available Circuits")
    table.add_column("Circuit Name", style="cyan")
    table.add_column("Description", style="dim")
    
    for c in circuits:
        table.add_row(c["name"], c["description"])
        
    console.print(table)
