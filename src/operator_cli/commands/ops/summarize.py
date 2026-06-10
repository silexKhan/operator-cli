import typer
from rich.console import Console
from rich.panel import Panel
from operator_cli.core.utils import get_project_root
from operator_cli.core.models.context import ContextManager
from operator_cli.llm.providers.ollama import LocalLLM
from datetime import datetime, timezone
from typing import Optional

app = typer.Typer(rich_markup_mode="rich")
console = Console()
RECENT_HISTORY_ITEMS_TO_KEEP = 4

@app.command(
    help="""
    [bold magenta]Memory Management & Compaction[/bold magenta]
    
    최근 작업 이력을 요약하여 [bold cyan]MEMORY.md[/bold cyan]를 업데이트합니다.
    """
)
def summarize(
    circuit: Optional[str] = None,
    force: bool = False,
):
    project_root = get_project_root()
    ctx_mgr = ContextManager(context_path=str(project_root / ".operator_context.json"))
    history = ctx_mgr.get_history()

    if not history:
        console.print("[yellow]No conversation history to summarize.[/yellow]")
        raise typer.Exit(0)

    if len(history) < 2 and not force:
        console.print("[yellow]Conversation history is too short to summarize. Use --force to override.[/yellow]")
        raise typer.Exit(0)
    
    active_model = ctx_mgr.get_default_model()
    llm = LocalLLM(model=active_model)

    with console.status("[bold green]Generating structured summary...[/bold green]"):
        try:
            summary = llm.generate_summary(history)
        except Exception as exc:
            console.print(f"[bold red]LLM Error:[/bold red] {exc}")
            raise typer.Exit(1)

    memory_path = project_root / "MEMORY.md"
    timestamp = datetime.now(timezone.utc).isoformat()
    active_circuit = circuit or ctx_mgr.get_active_circuit() or "disconnected"
    
    with open(memory_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n--- Session Summary ({timestamp}, circuit={active_circuit}) ---\n{summary}\n")

    recent_history = history[-RECENT_HISTORY_ITEMS_TO_KEEP:]
    compacted_history = [
        {
            "role": "system",
            "content": f"--- Previous Session Summary ({timestamp}) ---\n{summary}",
        },
        *recent_history,
    ]
    ctx_mgr.save_context(history=compacted_history)

    console.print(f"[bold green]✓[/bold green] MEMORY.md has been updated at [cyan]{memory_path}[/cyan]")
    console.print(Panel(summary, title="Generated Summary", border_style="cyan"))

if __name__ == "__main__":
    app()
