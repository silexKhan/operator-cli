import typer
from rich.console import Console
from operator_cli.core.models.context import ContextManager
from operator_cli.core.utils import get_project_root, get_engine

app = typer.Typer(
    help="""
    [bold yellow]System Status Checker[/bold yellow]
    
    오퍼레이터의 현재 연결 상태 및 활성 프로토콜 정보를 확인하거나 초기화합니다.
    """,
    rich_markup_mode="rich"
)

@app.callback(invoke_without_command=True)
def status():
    """
    [bold yellow]Status[/bold yellow]: 현재 오퍼레이터의 연결 상태와 활성 회선 리포트를 출력합니다.
    """
    from rich.console import Console
    from operator_cli.core.models.context import ContextManager
    
    from operator_cli.core.utils import S_CIRCUIT, S_PROTO, S_ERR
    
    console = Console()
    PROJECT_ROOT = get_project_root()
    ctx_mgr = ContextManager(context_path=str(PROJECT_ROOT / ".operator_context.json"))
    active_circuit = ctx_mgr.get_active_circuit()
    
    console.print(f"\n[bold yellow]{S_CIRCUIT} Operator Status Report[/bold yellow]")
    console.print("-" * 30)
    
    if active_circuit:
        console.print(f"Active Circuit : [bold green]{active_circuit}[/bold green]")
        console.print(f"Protocol Mode  : [cyan]Enabled[/cyan]")
        
        from rich.panel import Panel
        from rich.text import Text
        proto_engine = get_engine()
        full_protocol = proto_engine.get_full_context(active_circuit)
        
        console.print(f"\n[bold cyan]{S_PROTO} Active Protocols:[/bold cyan]")
        # Disable markup to avoid conflict with [LITERAL] tags
        console.print(Panel(Text(full_protocol), border_style="dim"))
    else:
        console.print("Active Circuit : [italic white]Disconnected[/italic white]")
        console.print("Protocol Mode  : [dim]Standby[/dim]")
        
    console.print("System Engine  : [green]Online[/green]")
    console.print("-" * 30)

    # Windows Compatibility Check (배포 편의성 강화)
    import sys
    if sys.platform == "win32":
        from operator_cli.core.utils import S_INFO, S_LIGHT
        console.print(f"\n[bold blue]{S_INFO} Windows Compatibility Note:[/bold blue]")
        
        # 인코딩 체크
        current_enc = sys.stdout.encoding.lower()
        if 'utf-8' not in current_enc:
            console.print(f"  - [yellow]Current encoding is {current_enc}.[/yellow]")
            console.print(f"  - {S_LIGHT} Run [bold cyan]'chcp 65001'[/bold cyan] for best experience.")
        else:
            console.print("  - [green]UTF-8 encoding is active. (Excellent)[/green]")
            
        console.print(f"  - {S_LIGHT} Use [bold]Windows Terminal[/bold] or [bold]PowerShell Core[/bold] for better visuals.\n")

    console.print("\n")

@app.command("reset")
def reset():
    """
    Clear the current active circuit and reset the operator context.
    """
    from rich.console import Console
    from operator_cli.core.models.context import ContextManager
    from operator_cli.core.utils import S_ERR
    
    console = Console()
    PROJECT_ROOT = get_project_root()
    ctx_mgr = ContextManager(context_path=str(PROJECT_ROOT / ".operator_context.json"))
    ctx_mgr.clear_active_circuit()
    console.print(f"[bold red]{S_ERR}[/bold red] Operator context has been reset. All circuits disconnected.")
