import typer
from typing import Optional
from operator_cli.core.utils import get_engine, get_unit_list, get_unit_names

app = typer.Typer(help="List all available units.", rich_markup_mode="rich")

def get_units_help():
    try:
        names = get_unit_names()
        if names:
            return f"상세 내용을 확인할 유닛 이름 (가용: [green]{', '.join(names)}[/green])"
    except Exception: pass
    return "상세 내용을 확인할 유닛 이름"

@app.callback(invoke_without_command=True)
def list_units(
    unit: Optional[str] = typer.Argument(None, help=get_units_help())
):
    """
    [bold green]Units[/bold green]: 가용한 모든 유닛 목록을 출력하거나 특정 유닛의 상세 규약을 확인합니다.
    """
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    
    console = Console()
    proto_engine = get_engine()
    
    if unit:
        # 특정 유닛 상세 보기
        content = proto_engine.load_unit_protocol(unit)
        if content:
            metadata, raw_md = proto_engine._parse_frontmatter(content)
            console.print(Panel(
                raw_md, 
                title=f"[bold green]Unit: {unit}[/bold green]", 
                subtitle=metadata.get("description", ""),
                border_style="green",
                box=box.ROUNDED
            ))
        else:
            console.print(f"[bold red]Error:[/bold red] Unit '[yellow]{unit}[/yellow]' not found.")
        return

    # 유닛 목록 출력
    units = get_unit_list()
    table = Table(
        title="[bold green]Available Operator Units[/bold green]", 
        header_style="bold magenta",
        box=box.ROUNDED,
        expand=True
    )
    table.add_column("Unit Name", style="green", no_wrap=True, width=15)
    table.add_column("Description", style="white", overflow="fold")
    table.add_column("Protocol File", style="dim", width=30)
    
    for u in units:
        table.add_row(u["name"], u["description"], f"protocols/units/{u['name']}.md")
        
    console.print(table)
    console.print(f"\n[dim]Tip: [bold green]'operator units [NAME]'[/bold green]을 입력하여 해당 유닛의 상세 규약을 확인하세요.[/dim]")
