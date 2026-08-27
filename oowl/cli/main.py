from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from oowl.pipeline.main import run_security_pipeline

app = typer.Typer(
    name="oowl",
    help="OOWL-GATE — AI-powered IaC security analysis.",
)

console = Console()

@app.command()
def scan(
    target: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="IaC file or directory to scan.",
    ),
    threshold: float = typer.Option(
        40.0,
        "--threshold",
        "-t",
        help="Security risk threshold.",
    )
) -> None:
    """
    Run the complete OOWL security pipeline and render a terminal summary.
    """
    try:
        result = run_security_pipeline(
            iac_source=str(target),
            policy_config={"threshold": threshold},
        )
    except FileNotFoundError as exc:
        console.print(f"[red]Input error:[/red] {exc}")
        raise typer.Exit(code=1)
    except Exception as exc:
        console.print(f"[bold red]OOWL execution failed:[/bold red] {exc}")
        raise typer.Exit(code=1)

    exit_code = render_summary(result, threshold)
    raise typer.Exit(code=exit_code)

def render_summary(result: dict, threshold: float) -> int:
    """
    Renders a human-friendly terminal output showing the security scan summary.
    """
    decision = result.get("decision", {})
    risk_report = result.get("risk_report", {})
    model = result.get("infrastructure_model", {})

    table = Table(title="OOWL Security Scan", show_header=True)
    table.add_column("Metric")
    table.add_column("Value")

    def safe_get(obj, key, default=None):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    resource_count = len(safe_get(model, "resources", []))
    relationship_count = len(safe_get(model, "relationships", []))
    
    score = safe_get(risk_report, "overall_risk_score", safe_get(risk_report, "risk_score", 0.0))
    status = safe_get(decision, "decision_status", "UNKNOWN")
    status_value = safe_get(status, "value", str(status))

    table.add_row("Resources", str(resource_count))
    table.add_row("Relationships", str(relationship_count))
    table.add_row("Risk Score", f"{float(score):.2f}")
    table.add_row("Threshold", f"{threshold:.2f}")
    
    color = "red" if status_value == "BLOCK" else "yellow" if status_value == "WARN" else "green"
    table.add_row("Decision", f"[bold {color}]{status_value}[/]")

    console.print(Panel.fit("[bold cyan]🦅 OOWL-GATE[/bold cyan]"))
    console.print(table)

    reasons = safe_get(decision, "blocking_reasons", [])
    if reasons:
        console.print("\n[bold yellow]Security Findings:[/bold yellow]")
        for reason in reasons[:5]:
            console.print(f"  • {reason}")

    return int(safe_get(decision, "exit_code", 0))

if __name__ == "__main__":
    app()
