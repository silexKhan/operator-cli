import typer
from typing import Optional
from operator_cli.core.utils import get_engine, get_circuit_list, get_circuit_names

app = typer.Typer(help="List all available circuits.", rich_markup_mode="rich")

def get_circuits_help():
    try:
        names = get_circuit_names()
        if names:
            return f"상세 내용을 확인할 회선 이름 (가용: [cyan]{', '.join(names)}[/cyan])"
    except Exception: pass
    return "상세 내용을 확인할 회선 이름"

@app.callback(invoke_without_command=True)
def list_circuits(
    circuit: Optional[str] = typer.Argument(None, help=get_circuits_help())
):
    """
    [bold cyan]Circuits[/bold cyan]: 가용한 모든 회선 목록을 출력하거나 특정 회선의 상세 프로토콜을 확인합니다.
    """
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    
    console = Console()
    proto_engine = get_engine()
    
    if circuit:
        # 특정 회선 상세 보기
        full_context = proto_engine.get_full_context(circuit)
        data = proto_engine.get_full_context_data(circuit)
        
        if data["circuit_protocol"]: # 프로토콜 내용이 있는 경우
            console.print(Panel(
                full_context, 
                title=f"[bold cyan]Circuit: {circuit}[/bold cyan]", 
                subtitle=data["description"],
                border_style="cyan",
                box=box.ROUNDED
            ))
        else:
            console.print(f"[bold red]Error:[/bold red] Circuit '[yellow]{circuit}[/yellow]' not found.")
        return

    # 회선 목록 출력
    circuits = get_circuit_list()
    table = Table(
        title="[bold cyan]Available Operator Circuits[/bold cyan]", 
        header_style="bold magenta",
        box=box.ROUNDED,
        expand=True
    )
    table.add_column("Circuit Name", style="cyan", no_wrap=True, width=15)
    table.add_column("Description", style="white", overflow="fold")
    table.add_column("Protocol File", style="dim", width=30)
    
    for c in circuits:
        table.add_row(c["name"], c["description"], f"protocols/circuits/{c['name']}.md")
        
    console.print(table)
    console.print(f"\n[dim]Tip: [bold cyan]'operator circuits [NAME]'[/bold cyan]을 입력하여 해당 회선의 상세 프로토콜을 확인하세요.[/dim]")
