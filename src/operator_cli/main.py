import sys
from typing import Optional

__version__ = "0.1.3"

if len(sys.argv) > 1 and sys.argv[1] in {"--version", "-v"}:
    print(f"Operator CLI Version: {__version__}")
    raise SystemExit(0)

import typer
from operator_cli.core.utils import get_circuit_names, get_unit_names

# Windows 유니코드 인코딩 문제 해결 (cp949 대응)
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except Exception:
        pass

def get_tree_str(items, color="gold1"):
    """도움말용 트리 구조 문자열 생성 (ASCII Safe)"""
    if not items: return ""
    lines = [""]
    for i, item in enumerate(items):
        # 유니코드 에러 방지를 위해 표준 ASCII 기호 사용
        connector = "+--" if i == len(items) - 1 else "|--"
        lines.append(f"      [bold {color}]{connector} {item}[/bold {color}]")
    return "\n".join(lines)

BANNER = """[bold cyan] ██████╗ ██████╗ ███████╗██████╗  █████╗ ████████╗██████╗ ██████╗ 
██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗
██║   ██║██████╔╝█████╗  ██████╔╝███████║   ██║   ██║  ██║██████╔╝
██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗██╔══██║   ██║   ██║  ██║██╔══██╗
╚██████╔╝██║     ███████╗██║  ██║██║  ██║   ██║   ██████╔╝██║  ██║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═════╝ ╚═╝  ╚═╝[/bold cyan]"""

app = typer.Typer(
    name="operator",
    help="[bold blue]Operator CLI[/bold blue] - A lightweight agentic command line interface for context-aware AI operations.",
    add_completion=False,
    rich_markup_mode="rich",
)

# 1. CORE OPERATIONS
@app.command(name="agent", help="AI Agent Executor (Local LLM).")
def agent_cmd(
    instruction: str = typer.Argument(..., help="실행할 AI 에이전트 명령"),
    execute: bool = typer.Option(False, "--execute", "-e", help="제안된 쉘 커맨드를 자동으로 실행할지 묻는 프롬프트를 활성화합니다."),
    model: str = typer.Option(None, "--model", "-m", help="사용할 로컬 LLM 모델 이름"),
    thinking: str = typer.Option("medium", "--thinking", "-t", help="추론 강도 설정")
):
    from operator_cli.commands.ops.agent import agent
    return agent(instruction, execute, model, thinking)

@app.command(name="summarize", help="Memory Management & Compaction.")
def summarize_cmd(
    circuit: Optional[str] = typer.Argument(None, help="압축할 회선 이름"),
    force: bool = typer.Option(False, "--force", "-f", help="강제 압축 실행")
):
    from operator_cli.commands.ops.summarize import summarize
    return summarize(circuit, force)

@app.command(name="call", help="Circuit Switcher (Connect to Node).")
def call_cmd(
    node: str = typer.Argument(..., help="연결할 노드(회선) 이름")
):
    from operator_cli.commands.ops.run import call
    return call(node)

@app.command(name="doctor", help="Run Operator environment diagnostics.")
def doctor_cmd(
    skip_ollama: bool = typer.Option(False, "--skip-ollama", help="Ollama 연결 점검을 건너뜁니다."),
    strict: bool = typer.Option(False, "--strict", help="경고가 있어도 실패 코드로 종료합니다.")
):
    from operator_cli.commands.info.doctor import doctor
    return doctor(skip_ollama, strict)

# 2. KNOWLEDGE MANAGEMENT
knowledge_items = [
    "query       [grey50](Search verified knowledge base; supports --format json)[/grey50]",
    "list        [grey50](List all verified/proposed items)[/grey50]",
    "propose     [grey50](Extract and propose new knowledge)[/grey50]",
    "approve     [grey50](Review and approve proposals)[/grey50]",
    "doctor      [grey50](Check OAKS store integrity)[/grey50]",
    "refresh     [grey50](Refresh llms.txt index)[/grey50]",
    "backup      [grey50](Backup OAKS knowledge and indices to zip)[/grey50]"
]
import operator_cli.commands.ops.knowledge as knowledge
app.add_typer(
    knowledge.app, 
    name="knowledge", 
    help=f"OAKS Knowledge Management System.{get_tree_str(knowledge_items, 'cyan')}"
)

# 3. GRAPH MANAGEMENT
graph_items = [
    "run         [grey50](Run graphify extraction/update)[/grey50]",
    "label       [grey50](Generate community labels from existing graph output)[/grey50]",
    "viz         [grey50](Generate graph.html from existing graph output)[/grey50]",
    "open        [grey50](Open graph report or interactive HTML)[/grey50]"
]
import operator_cli.commands.ops.graph as graph
app.add_typer(
    graph.app,
    name="graph",
    help=f"Knowledge Graph Management (Graphify).{get_tree_str(graph_items, 'plum1')}"
)

# 4. SETTING (Configuration)
setting_items = [
    "models          [grey50](List available local LLM models (Ollama))[/grey50]",
    "set-model       [grey50](Set the default local LLM model)[/grey50]",
    "graphify-delay  [grey50](Set the delay for automatic Graphify updates after knowledge changes)[/grey50]"
]
from operator_cli.commands.config import setting
app.add_typer(
    setting.app,
    name="setting",
    help=f"Configure Operator CLI settings.{get_tree_str(setting_items, 'khaki1')}"
)

# 5. Information Commands
from operator_cli.commands.info import status, circuits, units
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
from operator_cli.commands.config import connect
from operator_cli.commands.ops import run
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

# Entry point for console script
import os
if os.path.basename(sys.argv[0]) in ("operator", "operator.exe"):
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in {"--help", "-h"}):
        from rich.console import Console
        Console().print(BANNER)

if __name__ == "__main__":
    app()
