import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from operator_cli.core.utils import get_project_root

app = typer.Typer(rich_markup_mode="rich")
console = Console()


def _status_style(status: str) -> str:
    match status:
        case "PASS":
            return "green"
        case "WARN":
            return "yellow"
        case "FAIL":
            return "red"
        case _:
            return "white"


def _add_check(checks, name: str, status: str, detail: str, critical: bool = False):
    checks.append(
        {
            "name": name,
            "status": status,
            "detail": detail,
            "critical": critical,
        }
    )


@app.callback(invoke_without_command=True)
def doctor(
    skip_ollama: bool = False,
    strict: bool = False,
):
    """
    Check Operator runtime files, protocols, context, knowledge indexes, and optional Ollama connectivity.
    """
    project_root = get_project_root()
    checks = []

    _add_check(checks, "Project root", "PASS", str(project_root))

    protocols_dir = project_root / "protocols"
    global_protocol = protocols_dir / "global.md"
    circuits_dir = protocols_dir / "circuits"
    units_dir = protocols_dir / "units"
    circuit_files = sorted(circuits_dir.glob("*.md")) if circuits_dir.exists() else []
    unit_files = sorted(units_dir.glob("*.md")) if units_dir.exists() else []

    if protocols_dir.exists() and global_protocol.exists():
        _add_check(checks, "Global protocol", "PASS", str(global_protocol))
    else:
        _add_check(checks, "Global protocol", "FAIL", f"Missing {global_protocol}", critical=True)

    if circuit_files:
        _add_check(checks, "Circuits", "PASS", f"{len(circuit_files)} circuit file(s)")
    else:
        _add_check(checks, "Circuits", "FAIL", f"No circuit files under {circuits_dir}", critical=True)

    if unit_files:
        _add_check(checks, "Units", "PASS", f"{len(unit_files)} unit file(s)")
    else:
        _add_check(checks, "Units", "WARN", f"No unit files under {units_dir}")

    context_path = project_root / ".operator_context.json"
    if context_path.exists():
        try:
            json.loads(context_path.read_text(encoding="utf-8"))
            _add_check(checks, "Context file", "PASS", str(context_path))
        except json.JSONDecodeError as exc:
            _add_check(checks, "Context file", "FAIL", f"Invalid JSON: {exc}", critical=True)
    else:
        _add_check(checks, "Context file", "WARN", f"Not found: {context_path}")

    knowledge_dir = project_root / "knowledge"
    if knowledge_dir.exists():
        _add_check(checks, "Knowledge directory", "PASS", str(knowledge_dir))
    else:
        _add_check(checks, "Knowledge directory", "WARN", f"Not found: {knowledge_dir}")

    for index_name in ("llms.txt", "llms-full.txt"):
        index_path = project_root / index_name
        if index_path.exists():
            _add_check(checks, index_name, "PASS", str(index_path))
        else:
            _add_check(checks, index_name, "WARN", f"Not found: {index_path}")

    release_candidates = [
        project_root / "release" / "operator_mac" / "operator" / "operator",
        project_root / "release" / "operator_mac" / "operator",
        project_root / "release" / "operator_win" / "operator.exe",
    ]
    existing_release = next((path for path in release_candidates if path.exists()), None)
    if existing_release:
        _add_check(checks, "Release binary", "PASS", str(existing_release))
    else:
        _add_check(checks, "Release binary", "WARN", "No release binary found")

    if skip_ollama:
        _add_check(checks, "Ollama", "WARN", "Skipped by --skip-ollama")
    else:
        try:
            import ollama

            ollama.Client().list()
            _add_check(checks, "Ollama", "PASS", "Local Ollama API responded")
        except Exception as exc:
            _add_check(checks, "Ollama", "WARN", f"Unavailable: {exc}")

    table = Table(title="Operator Doctor", header_style="bold cyan")
    table.add_column("Check", style="white")
    table.add_column("Status", no_wrap=True)
    table.add_column("Detail", overflow="fold")

    for item in checks:
        table.add_row(
            item["name"],
            f"[{_status_style(item['status'])}]{item['status']}[/{_status_style(item['status'])}]",
            item["detail"],
        )

    console.print(table)

    has_failure = any(item["critical"] and item["status"] == "FAIL" for item in checks)
    has_warning = any(item["status"] == "WARN" for item in checks)
    if has_failure or (strict and has_warning):
        raise typer.Exit(1)
