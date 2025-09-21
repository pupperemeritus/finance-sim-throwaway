import subprocess
import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel

# Add the project's 'src' directory to the Python path
# This makes `from src...` imports work when running from the project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config_loader import load_config
from src.model import ExpenseModel
from src.reporting import create_report

from src.simulation.components import (
    simulate_daily_variable_expenses,
    simulate_periodic_expenses,
)

app = typer.Typer(
    name="finance-sim",
    help="A comprehensive personal finance simulator with Monte Carlo analysis.",
)
console = Console()


@app.command()
def run(
    config_path: Path = typer.Option(
        "config/default.yaml",
        "--config",
        "-c",
        help="Path to the configuration YAML file.",
    )
):
    """
    Run the financial simulation and generate a report.
    """
    try:
        console.print(
            f"📊 Loading configuration from: [bold cyan]{config_path}[/bold cyan]"
        )
        config = load_config(config_path)

        console.print(
            f"⚙️ Initializing model for [bold yellow]{config.simulation.mc_trials:,}[/bold yellow] trials..."
        )
        model = ExpenseModel(config)

        # --- FIX: Register the simulation components with the model ---
        model.register(simulate_daily_variable_expenses)
        model.register(simulate_periodic_expenses)

        console.print("🚀 Running simulation...")
        results_df = model.run_simulation()

        console.print(
            "\n[bold green]✔ Simulation Complete![/bold green] Generating report..."
        )
        reports_dir = Path("reports")
        create_report(results_df, config, reports_dir)

    except Exception as e:
        console.print(
            Panel(
                f"An unexpected error occurred:\n[bold red]{e}[/bold red]",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(code=1)


@app.command()
def test():
    """
    Run the project's test suite using pytest.
    """
    console.print("🧪 Running test suite...")
    result = subprocess.run(["pytest"], capture_output=True, text=True)
    if result.returncode == 0:
        console.print("[bold green]✔ All tests passed![/bold green]")
        console.print(result.stdout)
    else:
        console.print("[bold red]❌ Tests failed![/bold red]")
        console.print(result.stdout)
        console.print(result.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
