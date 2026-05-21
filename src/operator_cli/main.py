import typer
from operator_cli.core.utils import get_circuit_names, get_unit_names

__version__ = "0.1.3"

def get_tree_str(items, color="gold1"):
    """도움말용 트리 구조 문자열 생성"""
    if not items: return ""
    lines = [""]
    for i, item in enumerate(items):
        connector = "└──" if i == len(items) - 1 else "├──"
        lines.append(f"      [bold {color}]{connector} {item}[/bold {color}]")
    return "\n".join(lines)

app = typer.Typer(
    name="operator",
    help="[bold blue]Operator CLI[/bold blue] - A lightweight agentic command line interface for context-aware AI operations.",
    add_completion=False,
    rich_markup_mode="rich",
)

# 명령어 모듈 로드
from operator_cli.commands.ops import run, agent, summarize, knowledge
from operator_cli.commands.info import status, circuits, units
from operator_cli.commands.config import connect, setting

# 1. CORE OPERATIONS
app.command(name="agent", help="AI Agent Executor (Local LLM).")(agent.agent)
app.command(name="summarize", help="Memory Management & Compaction.")(summarize.summarize)
app.command(name="call", help="Circuit Switcher (Connect to Node).")(run.call)

# 2. KNOWLEDGE MANAGEMENT
knowledge_items = [
    "query       [grey50](Search verified knowledge base)[/grey50]",
    "list        [grey50](List all verified/proposed items)[/grey50]",
    "propose     [grey50](Extract and propose new knowledge)[/grey50]",
    "approve     [grey50](Review and approve proposals)[/grey50]",
    "refresh     [grey50](Refresh llms.txt index)[/grey50]"
]
app.add_typer(
    knowledge.app, 
    name="knowledge", 
    help=f"OAKS Knowledge Management System.{get_tree_str(knowledge_items, 'cyan')}"
)

# 3. SETTING (Configuration)
app.add_typer(setting.app, name="setting", help="Configure Operator CLI settings.")

# 4. Information Commands
app.add_typer(status.app, name="status", help="System Status Checker.")
app.add_typer(
    circuits.app, 
    name="circuits", 
    help=f"List all available circuits.{get_tree_str(get_circuit_names(), 'gold1')}"
)

unit_items = [
    "markdown    [grey50](Expert assistant for Markdown writing)[/grey50]",
    "planning    [grey50](Strategic guide for task planning)[/grey50]",
    "python      [grey50](Professional expert for Python development)[/grey50]",
    "sentinel    [grey50](Autonomous supervisor for quality & QA)[/grey50]",
    "swift       [grey50](Expert for type-safe Swift development)[/grey50]"
]
app.add_typer(
    units.app, 
    name="units", 
    help=f"List all available units.{get_tree_str(unit_items, 'khaki1')}"
)

# --- 하위 호환성 및 숨김 명령어 ---
app.command(name="connect", hidden=True)(connect.connect)
app.command(name="run", hidden=True)(run.call)
app.command(name="do", hidden=True)(run.call)

@app.command(name="?", hidden=True)
def help_alias(ctx: typer.Context):
    """Alias for showing help."""
    from rich.console import Console
    console = Console()
    console.print(ctx.parent.get_help() if ctx.parent else ctx.get_help())

def version_callback(value: bool):
    if value:
        from rich.console import Console
        console = Console()
        console.print(f"Operator CLI Version: [bold cyan]{__version__}[/bold cyan]")
        raise typer.Exit()

@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True, help="Show the version and exit."
    ),
):
    """
    [bold green]Welcome to Operator CLI.[/bold green]
    """
    pass

if __name__ == "__main__":
    app()
