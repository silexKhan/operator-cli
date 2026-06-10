import typer
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime
from rich.console import Console
from operator_cli.core.utils import get_project_root, S_OK, S_ERR

app = typer.Typer(rich_markup_mode="rich")
console = Console()


def get_graph_project_root() -> Path:
    project_root = get_project_root()
    if not (project_root / ".venv").exists() and "release" in str(project_root):
        return project_root.parent.parent
    return project_root


def get_graphify_base_command(project_root: Path) -> list[str] | None:
    venv_python = project_root / ".venv" / "bin" / "python3"
    if venv_python.exists():
        return [str(venv_python), "-m", "graphify"]

    graphify_bin = shutil.which("graphify")
    if graphify_bin:
        return [graphify_bin]

    return None


def run_subprocess(command: list[str], project_root: Path, quiet: bool = False) -> int:
    stdout = subprocess.DEVNULL if quiet else None
    result = subprocess.run(command, cwd=project_root, stdout=stdout)
    return result.returncode


def generate_visualization(project_root: Path) -> bool:
    base_cmd = get_graphify_base_command(project_root)
    if not base_cmd:
        console.print(f"[bold red]{S_ERR} Error:[/bold red] 'graphify' not found in .venv or PATH.")
        return False

    console.print(f"[bold blue]🎨 Generating visualization (graph.html)...[/bold blue]")
    return run_subprocess(base_cmd + ["cluster-only", "."], project_root, quiet=True) == 0

def label_communities(project_root: Path, ctx_mgr):
    """로컬 LLM(Ollama)을 사용하여 커뮤니티 이름을 자동으로 생성합니다."""
    graph_path = project_root / "graphify-out" / "graph.json"
    analysis_path = project_root / "graphify-out" / ".graphify_analysis.json"
    labels_path = project_root / "graphify-out" / ".graphify_labels.json"
    
    if not graph_path.exists() or not analysis_path.exists():
        return False
        
    console.print(f"[bold blue]🧠 Ollama is naming communities...[/bold blue]")
    
    try:
        with open(graph_path, "r") as f:
            graph_data = json.load(f)
        with open(analysis_path, "r") as f:
            analysis_data = json.load(f)
            
        nodes_dict = {n["id"]: n.get("label", n["id"]) for n in graph_data.get("nodes", [])}
        communities = analysis_data.get("communities", {})
        
        # 기존 레이블 로드
        existing_labels = {}
        if labels_path.exists():
            try:
                with open(labels_path, "r") as f:
                    existing_labels = json.load(f)
            except Exception:
                existing_labels = {}
        
        from operator_cli.llm.providers.ollama import LocalLLM

        active_model = getattr(ctx_mgr.context, "default_model", "gemma4:latest")
        llm = LocalLLM(model=active_model, thinking_level="low")
        
        new_labels = existing_labels.copy()
        updated_count = 0
        
        for cid, node_ids in communities.items():
            # 이미 이름이 있거나 "Community N" 형식인 경우만 처리
            current_name = existing_labels.get(cid, "")
            if not current_name or current_name.startswith("Community "):
                labels_in_comm = [nodes_dict.get(nid, nid) for nid in node_ids[:15]]
                if not labels_in_comm: continue
                
                prompt = f"Identify a concise, descriptive name (2-5 words) for a software module containing these elements: {', '.join(labels_in_comm)}. Respond ONLY with the name."
                
                try:
                    name = llm.generate_response(system_prompt="You are a senior software architect. Name this module based on its components.", user_instruction=prompt)
                    name = name.strip().strip('"').strip("'")
                    
                    if ":" in name: name = name.split(":")[-1].strip()
                    
                    new_labels[cid] = name
                    updated_count += 1
                    console.print(f"  - [dim]Community {cid} ->[/dim] [cyan]{name}[/cyan]")
                except Exception as e:
                    console.print(f"  - [yellow]Failed to name community {cid}: {str(e)}[/yellow]")
        
        if updated_count > 0:
            with open(labels_path, "w") as f:
                json.dump(new_labels, f, ensure_ascii=False)
            return True
    except Exception as e:
        console.print(f"[bold red]Naming Error:[/bold red] {str(e)}")
    return False

@app.command(name="run")
def graph_run(
    update: bool = typer.Option(False, "--update", "-u", help="변경사항만 증분 갱신합니다."),
    deep: bool = typer.Option(False, "--deep", "-d", help="딥 모드로 상세 분석을 수행합니다."),
    label: bool = typer.Option(True, "--label/--no-label", help="LLM 기반 community labeling 실행 여부"),
    viz: bool = typer.Option(True, "--viz/--no-viz", help="시각화 HTML 생성 여부"),
    force: bool = typer.Option(False, "--force", "-f", help="유예 시간을 무시하고 강제 실행")
):
    """
    [bold cyan]Graphify 실행[/bold cyan]
    프로젝트의 지식 그래프를 생성하거나 갱신합니다.
    지식 승인 후 설정된 유예 시간(기본 30분)이 지나야 자동으로 실행됩니다.
    """
    from operator_cli.core.models.context import ContextManager

    project_root = get_graph_project_root()
        
    ctx_mgr = ContextManager(context_path=str(project_root / ".operator_context.json"))
    
    # 유예 시간 체크
    last_update_str = getattr(ctx_mgr.context, "last_knowledge_update", None)
    if last_update_str and not force:
        try:
            last_update = datetime.fromisoformat(last_update_str)
            delay_minutes = getattr(ctx_mgr.context, "graphify_auto_update_delay", 30)
            elapsed = (datetime.now() - last_update).total_seconds() / 60
            
            if elapsed < delay_minutes:
                remaining = int(delay_minutes - elapsed)
                console.print(f"[yellow]⌛ Graphify update is scheduled.[/yellow]")
                console.print(f"[dim]Last knowledge update was {int(elapsed)} mins ago. {remaining} mins remaining.[/dim]")
                if not typer.confirm("Do you want to run it now anyway?"):
                    return
        except Exception:
            pass 

    console.print(f"[bold blue]🚀 Running Graphify at:[/bold blue] {project_root}")
    
    try:
        cmd = get_graphify_base_command(project_root)
        if not cmd:
            console.print(f"[bold red]{S_ERR} Error:[/bold red] 'graphify' not found in .venv or PATH.")
            return

        if update:
            cmd.extend(["update", "."])
        else:
            cmd.extend(["extract", "."])

        active_model = getattr(ctx_mgr.context, "default_model", "gemma4:latest")
        cmd.extend(["--backend", "ollama", "--model", active_model])

        if deep:
            cmd.extend(["--mode", "deep"])
        if not viz:
            cmd.append("--no-viz")

        exit_code = run_subprocess(cmd, project_root)
        if exit_code == 0:
            if label:
                label_communities(project_root, ctx_mgr)
            
            if viz:
                generate_visualization(project_root)
                
            console.print(f"[bold green]{S_OK} Graphify completed successfully![/bold green]")
        else:
            console.print(f"[bold red]{S_ERR} Graphify failed with exit code {exit_code}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@app.command(name="label")
def graph_label():
    """
    [bold cyan]Graphify community label 생성[/bold cyan]
    기존 graphify 산출물을 기반으로 LLM community label만 갱신합니다.
    """
    from operator_cli.core.models.context import ContextManager

    project_root = get_graph_project_root()
    ctx_mgr = ContextManager(context_path=str(project_root / ".operator_context.json"))

    if label_communities(project_root, ctx_mgr):
        console.print(f"[bold green]{S_OK} Graphify community labels updated.[/bold green]")
    else:
        console.print(f"[yellow]No Graphify labels were updated.[/yellow]")


@app.command(name="viz")
def graph_viz():
    """
    [bold cyan]Graphify 시각화 생성[/bold cyan]
    기존 graphify 산출물을 기반으로 graph.html만 생성합니다.
    """
    project_root = get_graph_project_root()
    if generate_visualization(project_root):
        console.print(f"[bold green]{S_OK} Graphify visualization generated.[/bold green]")
    else:
        raise typer.Exit(1)

@app.command(name="open")
def graph_open(
    html: bool = typer.Option(False, "--html", help="브라우저에서 대화형 그래프를 엽니다.")
):
    """
    [bold cyan]그래프 결과 조회[/bold cyan]
    생성된 지식 그래프 리포트 또는 HTML을 엽니다.
    """
    project_root = get_project_root()
    report_path = project_root / "graphify-out" / "GRAPH_REPORT.md"
    html_path = project_root / "graphify-out" / "graph.html"
    
    if html:
        if not html_path.exists():
            console.print(f"[bold red]{S_ERR} Error:[/bold red] graph.html not found. Run 'operator graph run' first.")
            return
        console.print(f"[bold blue]🌍 Opening interactive graph:[/bold blue] {html_path}")
        typer.launch(str(html_path))
    else:
        if not report_path.exists():
            console.print(f"[bold red]{S_ERR} Error:[/bold red] GRAPH_REPORT.md not found. Run 'operator graph run' first.")
            return
        console.print(f"[bold blue]📝 Opening graph report:[/bold blue] {report_path}")
        typer.launch(str(report_path))
