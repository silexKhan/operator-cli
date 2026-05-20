import typer
from rich.console import Console
from rich.panel import Panel
from operator_cli.core.utils import get_project_root
from operator_cli.core.models.context import ContextManager
from operator_cli.llm.providers.ollama import LocalLLM
from pathlib import Path
import os

app = typer.Typer(rich_markup_mode="rich")
console = Console()

@app.command(
    help="""
    [bold magenta]Memory Management & Compaction[/bold magenta]
    
    최근 작업 이력을 요약하여 [bold cyan]MEMORY.md[/bold cyan]를 업데이트합니다.
    """
)
def summarize():
    PROJECT_ROOT = get_project_root()
    ctx_mgr = ContextManager(context_path=str(PROJECT_ROOT / ".operator_context.json"))
    
    active_model = ctx_mgr.get_default_model()
    llm = LocalLLM(model=active_model)
    
    # TODO: 실제 히스토리 수집 로직 통합 필요
    # 현재는 데모를 위해 고정된 메시지 구조 사용
    dummy_history = [
        {"role": "user", "content": "operator-cli에 요약 기능을 추가해줘."},
        {"role": "assistant", "content": "네, compaction.py 모듈을 만들고 LLM에 요약 메서드를 추가하겠습니다."},
        {"role": "tool", "content": "Successfully created operator_cli/core/compaction.py"}
    ]
    
    with console.status("[bold green]Generating structured summary...[/bold green]"):
        summary = llm.generate_summary(dummy_history)
        
    memory_path = Path.cwd() / "MEMORY.md"
    
    with open(memory_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n--- Session Summary ---\n{summary}\n")
        
    console.print(f"[bold green]✓[/bold green] MEMORY.md has been updated at [cyan]{memory_path}[/cyan]")
    console.print(Panel(summary, title="Generated Summary", border_style="cyan"))

if __name__ == "__main__":
    app()
