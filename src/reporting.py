import pandas as pd
import matplotlib

# Use a non-interactive backend suitable for saving files
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.config_loader import Config


def create_report(results_df: pd.DataFrame, config: Config, output_dir: Path):
    """
    Generates a full financial report with tables and visualizations.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    console = Console()

    sns.set_theme("paper", style="dark", font="Fira Sans")
    # --- 1. Main Expense Summary Table ---
    daily_avg = results_df.mean()
    total_daily_expense = daily_avg.sum()

    expense_table = Table(
        title="Expense Simulation Summary (Daily Averages)", header_style="bold magenta"
    )
    expense_table.add_column("Expense Category", style="cyan", no_wrap=True)
    expense_table.add_column("Daily Avg", justify="right", style="green")
    expense_table.add_column("Monthly Avg", justify="right", style="yellow")
    expense_table.add_column("Yearly Avg", justify="right", style="red")

    for category, avg_cost in daily_avg.items():
        if avg_cost > 0.01:  # Only display significant expenses
            expense_table.add_row(
                category.replace("_", " ").title(),
                f"₹{avg_cost:.2f}",
                f"₹{avg_cost * config.time.days_in_month:.2f}",
                f"₹{avg_cost * 365.25:.2f}",
            )

    expense_table.add_section()
    expense_table.add_row(
        "[bold]Total Estimated Expenses[/bold]",
        f"[bold]₹{total_daily_expense:.2f}[/bold]",
        f"[bold]₹{total_daily_expense * config.time.days_in_month:.2f}[/bold]",
        f"[bold]₹{total_daily_expense * 365.25:.2f}[/bold]",
    )
    console.print(expense_table)

    # --- 2. Investment Allocation Breakdown ---
    fin_config = config.financials
    if fin_config.monthly_investable_amount > 0:
        profile_name = fin_config.active_investment_profile
        profile = config.investment_profiles.get(profile_name)

        if profile:
            investment_table = Table(
                title=f"Investment Allocation ({profile_name} Profile)",
                header_style="bold blue",
            )
            investment_table.add_column("Asset Class", style="cyan")
            investment_table.add_column("Allocation %", justify="right", style="yellow")
            investment_table.add_column(
                "Monthly Amount", justify="right", style="green"
            )

            for asset, percentage in profile.items():
                amount = fin_config.monthly_investable_amount * percentage
                investment_table.add_row(
                    asset.replace("_", " ").title(),
                    f"{percentage:.0%}",
                    f"₹{amount:,.2f}",
                )

            investment_table.add_section()
            investment_table.add_row(
                "[bold]Total Investment[/bold]",
                "",
                f"[bold]₹{fin_config.monthly_investable_amount:,.2f}[/bold]",
            )
            console.print(investment_table)
        else:
            console.print(
                f"[bold red]Warning: Active investment profile '{profile_name}' not found in config.[/bold red]"
            )

    # --- 3. Visualizations ---

    # Expense Breakdown Pie Chart
    plt.figure(figsize=(10, 8))
    # Filter out very small values for a cleaner pie chart
    plot_data = daily_avg[daily_avg > 0.01]
    plot_data.plot(
        kind="pie",
        autopct="%1.1f%%",
        startangle=120,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    plt.title("Average Daily Expense Breakdown", fontsize=16, weight="bold")
    plt.ylabel("")  # Hide the y-label
    plt.tight_layout()
    pie_chart_path = output_dir / "expense_breakdown.png"
    plt.savefig(pie_chart_path, dpi=150)
    plt.close()

    # Total Daily Cost Distribution Histogram
    total_daily_costs = results_df.sum(axis=1)
    plt.figure(figsize=(12, 6))
    sns.histplot(total_daily_costs, kde=True, bins=50, color="skyblue")
    plt.title("Distribution of Total Daily Costs", fontsize=16, weight="bold")
    plt.xlabel("Total Cost (₹)", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    median_cost = total_daily_costs.median()
    plt.axvline(
        median_cost, color="r", linestyle="--", label=f"Median: ₹{median_cost:.2f}"
    )
    plt.legend()
    plt.tight_layout()
    hist_path = output_dir / "daily_cost_distribution.png"
    plt.savefig(hist_path, dpi=150)
    plt.close()

    console.print(
        f"\n[bold green]✔ Visual reports saved to:[/] {pie_chart_path.parent.resolve()}"
    )
