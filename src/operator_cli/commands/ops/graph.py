import typer
import subprocess
import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
from operator_cli.core.utils import get_project_root, S_OK, S_ERR
from operator_cli.core.models.context import ContextManager
from operator_cli.llm.providers.ollama import LocalLLM

app = typer.Typer(rich_markup_mode="rich")
console = Console()

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
    no_viz: bool = typer.Option(False, "--no-viz", help="시각화 HTML 생성을 건너뜜"),
    force: bool = typer.Option(False, "--force", "-f", help="유예 시간을 무시하고 강제 실행")
):
    """
    [bold cyan]Graphify 실행[/bold cyan]
    프로젝트의 지식 그래프를 생성하거나 갱신합니다.
    지식 승인 후 설정된 유예 시간(기본 30분)이 지나야 자동으로 실행됩니다.
    """
    project_root = get_project_root()
    
    # 릴리즈 폴더 내 실행 시 상위 탐색 보완
    potential_venv = project_root / ".venv"
    if not potential_venv.exists() and "release" in str(project_root):
        project_root = project_root.parent.parent
        
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
        venv_python = project_root / ".venv" / "bin" / "python3"
        if venv_python.exists():
            cmd = [str(venv_python), "-m", "graphify"]
        else:
            import shutil
            graphify_bin = shutil.which("graphify")
            if graphify_bin:
                cmd = [graphify_bin]
            else:
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
        if no_viz:
            cmd.append("--no-viz")

        result = subprocess.run(cmd, cwd=project_root)
        if result.returncode == 0:
            # 1. 로컬 LLM을 통한 커뮤니티 레이블링
            label_communities(project_root, ctx_mgr)
            
            # 2. 시각화 파일(HTML) 강제 생성 (cluster-only)
            if not no_viz:
                console.print(f"[bold blue]🎨 Generating visualization (graph.html)...[/bold blue]")
                viz_cmd = cmd[:3] + ["cluster-only", "."]
                subprocess.run(viz_cmd, cwd=project_root, stdout=subprocess.DEVNULL)
                
            console.print(f"[bold green]{S_OK} Graphify completed successfully![/bold green]")
        else:
            console.print(f"[bold red]{S_ERR} Graphify failed with exit code {result.returncode}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

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
