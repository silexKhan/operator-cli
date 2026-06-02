from pathlib import Path
from typing import Optional
import typer
from operator_cli.core.utils import get_project_root, get_engine

app = typer.Typer(rich_markup_mode="rich")

@app.command(
    help="""
    [bold magenta]Local LLM Agent Executor[/bold magenta]
    
    현재 활성화된 회선의 컨텍스트를 바탕으로 AI 에이전트가 임무를 수행합니다.
    - [bold cyan]operator agent "[명령]"[/bold cyan]: 현재 회선에서 AI 임무 수행.
    """
)
def agent(
    instruction: str = typer.Argument(..., help="실행할 AI 에이전트 명령"),
    execute: bool = typer.Option(False, "--execute", "-e", help="제안된 쉘 커맨드를 자동으로 실행할지 묻는 프롬프트를 활성화합니다."),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="사용할 로컬 LLM 모델 이름 (미지정 시 설정된 기본값 사용)"),
    thinking: str = typer.Option("medium", "--thinking", "-t", help="추론 강도 설정 (minimal, low, medium, high, xhigh)")
):
    from rich.console import Console
    from rich.panel import Panel
    from operator_cli.core.models.context import ContextManager
    from operator_cli.llm.providers.ollama import LocalLLM
    from operator_cli.executor.shell import ShellExecutor

    console = Console()
    PROJECT_ROOT = get_project_root()
    ctx_mgr = ContextManager(context_path=str(PROJECT_ROOT / ".operator_context.json"))
    proto_engine = get_engine()

    target_circuit = ctx_mgr.get_active_circuit()

    # 모델 결정 (옵션 -> 컨텍스트)
    active_model = model if model else ctx_mgr.get_default_model()

    if not target_circuit:
        console.print(f"[bold red]Error:[/bold red] No active node. Please switch to a node first (e.g., [cyan]'operator call matrix'[/cyan]).")
        raise typer.Exit(1)

    full_context = proto_engine.get_full_context(target_circuit, context_mgr=ctx_mgr)
    console.print(f"[bold blue]⚡ Active Circuit:[/bold blue] {target_circuit}")
    console.print(f"[bold blue]🤖 Model         :[/bold blue] {active_model}")
    console.print(f"[bold blue]🧠 Thinking      :[/bold blue] {thinking}")

    with console.status(f"[bold green]Local LLM Agent ({thinking}) is thinking...[/bold green]"):
        try:
            llm = LocalLLM(model=active_model, thinking_level=thinking)
            # 히스토리 기반 응답 생성
            history = ctx_mgr.get_history()
            response = llm.generate_response_with_history(
                system_prompt=full_context, 
                user_instruction=instruction,
                history=history
            )
            
            # 히스토리 업데이트 (User 요청 및 Assistant 응답)
            ctx_mgr.add_history("user", instruction)
            ctx_mgr.add_history("assistant", response)
            
        except Exception as e:
            console.print(f"[bold red]LLM Error:[/bold red] {str(e)}")
            raise typer.Exit(1)
    
    console.print(Panel(response, title=f"[bold green]Local LLM Agent Analysis[/bold green]", border_style="green", expand=False))
    
    # Check for suggested commands
    import re
    commands = re.findall(r"```(?:bash|sh|zsh)?\n(.*?)\n```", response, re.DOTALL)
    if not commands and "```" in response:
        commands = re.findall(r"```\n(.*?)\n```", response, re.DOTALL)

    for cmd in commands:
        cmd = cmd.strip()
        if not cmd: continue
        
        console.print(f"\n[bold yellow]⚠ Suggested Command:[/bold yellow] [bold cyan]{cmd}[/bold cyan]")
        if execute or typer.confirm("Do you want to execute this command?"):
            with console.status("[bold yellow]Executing...[/bold yellow]"):
                output = ShellExecutor.execute(cmd)
            console.print(Panel(output if output.strip() else "[dim]Command executed with no output.[/dim]", title="[bold yellow]Execution Result[/bold yellow]"))
