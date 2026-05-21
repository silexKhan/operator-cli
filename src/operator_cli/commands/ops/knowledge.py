import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from operator_cli.core.knowledge.manager import KnowledgeManager
from operator_cli.core.knowledge.extractor import KnowledgeExtractor
from operator_cli.llm.providers.ollama import LocalLLM

app = typer.Typer(rich_markup_mode="rich")
console = Console()

@app.command(name="query")
def query_knowledge(
    keyword: str = typer.Argument(..., help="검색할 키워드")
):
    """
    [bold cyan]지식 검색[/bold cyan]
    지식 베이스(Markdown)에서 키워드를 검색합니다.
    """
    manager = KnowledgeManager()
    results = manager.query_knowledge(keyword)
    
    if not results:
        console.print(f"[yellow]'{keyword}'에 대한 검색 결과가 없습니다.[/yellow]")
        return

    table = Table(title=f"Knowledge Search Results: {keyword}", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=12)
    table.add_column("Category", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Context", style="white")

    for meta, context in results:
        table.add_row(meta.id, meta.category, meta.title, context)

    console.print(table)

@app.command(name="list")
def list_knowledge(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="조회할 카테고리 (library, proposals, basement)")
):
    """
    [bold cyan]지식 목록 출력[/bold cyan]
    현재 저장된 지식 목록을 테이블 형식으로 출력합니다.
    """
    manager = KnowledgeManager()
    knowledges = manager.list_knowledge(category=category)
    
    table = Table(title="OAKS Knowledge Library", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=12)
    table.add_column("Category", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Updated At", style="blue")
    table.add_column("Tags", style="yellow")

    for meta in knowledges:
        table.add_row(
            meta.id, 
            meta.category, 
            meta.title, 
            meta.updated_at.strftime("%Y-%m-%d %H:%M"),
            ", ".join(meta.tags)
        )

    console.print(table)

@app.command(name="propose")
def propose_knowledge(
    text: str = typer.Argument(..., help="지식을 추출할 원본 텍스트 또는 파일 경로"),
    is_file: bool = typer.Option(False, "--file", "-f", help="입력값이 파일 경로임을 명시합니다.")
):
    """
    [bold cyan]새로운 지식 제안[/bold cyan]
    텍스트나 파일에서 지식을 추출하여 proposals 폴더에 저장합니다.
    """
    input_text = text
    if is_file:
        from pathlib import Path
        path = Path(text)
        if path.exists():
            input_text = path.read_text(encoding="utf-8")
        else:
            console.print(f"[bold red]Error:[/bold red] 파일을 찾을 수 없습니다: {text}")
            raise typer.Exit(1)

    extractor = KnowledgeExtractor()
    manager = KnowledgeManager()
    
    with console.status("[bold green]Extracting knowledge candidates...[/bold green]"):
        candidates = extractor.extract_from_text(input_text)
    
    if not candidates:
        console.print("[yellow]추출된 지식 후보가 없습니다.[/yellow]")
        return

    for raw_data in candidates:
        metadata, content = extractor.create_knowledge_proposal(raw_data)
        
        # 충돌 감지 (Conflict Detection)
        conflicts = manager.detect_conflicts(metadata)
        if conflicts:
            console.print(f"\n[bold yellow]⚠ Conflict Warning for '{metadata.title}':[/bold yellow]")
            for existing, reason in conflicts:
                console.print(f"  - [dim][{existing.category}][/dim] {existing.title} ({existing.id}): [italic]{reason}[/italic]")
            console.print("[yellow]제안된 지식이 기존 지식과 중복되거나 유사할 수 있습니다. 검토가 필요합니다.[/yellow]\n")

        saved_path = manager.save_knowledge(metadata, content)
        console.print(f"[bold green]✔ Proposed:[/bold green] {metadata.title} ({metadata.id}) -> [dim]{saved_path}[/dim]")

@app.command(name="approve")
def approve_knowledge(
    proposal_id: str = typer.Argument(..., help="승인할 제안서 ID")
):
    """
    [bold cyan]지식 승인[/bold cyan]
    제안된 지식(proposals)을 검토 후 승인하여 library로 이동합니다.
    """
    manager = KnowledgeManager()
    try:
        new_path = manager.approve_proposal(proposal_id)
        console.print(f"[bold green]✔ Approved:[/bold green] Knowledge {proposal_id} has been moved to library.")
        console.print(f"[dim]Location: {new_path}[/dim]")
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {str(e)}")
        raise typer.Exit(1)

@app.command(name="refresh")
def refresh_wiki():
    """
    [bold cyan]OAKS Wiki 갱신[/bold cyan]
    llms.txt 및 llms-full.txt 파일을 최신 지식 기반으로 수동 갱신합니다.
    """
    from operator_cli.core.knowledge.generator import WikiGenerator
    
    generator = WikiGenerator()
    try:
        with console.status("[bold green]Refreshing OAKS Passive Interface (llms.txt)...[/bold green]"):
            generator.refresh()
        console.print("[bold green]✔ Success:[/bold green] llms.txt and llms-full.txt have been refreshed.")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)
