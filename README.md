# Personal Finance Monte Carlo Simulator

<!--toc:start-->

- [Personal Finance Monte Carlo Simulator](#personal-finance-monte-carlo-simulator)
  - [Key Features](#key-features)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Usage](#usage)
    - [Run a Simulation](#run-a-simulation)
    - [Run Tests](#run-tests)
  - [Understanding the Output](#understanding-the-output)
  - [Project Structure](#project-structure)
  - [How It Works: Technical Details](#how-it-works-technical-details)
  <!--toc:end-->

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A professional-grade command-line tool for simulating and forecasting personal daily expenses using Monte Carlo methods. It provides detailed financial insights through statistical analysis and data visualization.

This simulator moves beyond simple spreadsheets by modeling the inherent randomness and interconnectedness of daily financial life, helping you understand the _distribution_ of possible outcomes, not just a single average.

## Key Features

- **Monte Carlo Simulation**: Run hundreds of thousands of trials in seconds for statistically robust results on your daily, monthly, and yearly expense estimates.
- **Correlated Variables**: Accurately models the relationships between different expense types (e.g., higher social spending might correlate with higher food costs) using a multivariate normal distribution.
- **Comprehensive Configuration**: Define all your financial variables—from daily discretionary spending to fixed yearly subscriptions—in a single, easy-to-understand YAML file.
- **Rich Console Reporting**: Generates beautiful, easy-to-read summary tables directly in your terminal using Rich, providing an immediate overview of your financial landscape.
- **Data Visualization**: Automatically creates and saves insightful charts, including an expense breakdown pie chart and a total daily cost distribution histogram, allowing you to see where your money goes.
- **Modular & Extensible**: The simulation engine is designed to be easily extended. You can add new, complex financial components (e.g., a stock market model) without altering existing code.
- **Modern CLI**: Powered by Typer for a clean, user-friendly, and self-documenting command-line experience.

## Installation

To get started, clone the repository and install the package in an editable mode. Using a virtual environment is highly recommended.

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/pupperemeritus/personal-finance-simulator.git](https://github.com//finance-sim-throwaway.git)
   cd finance-sim-throwaway
   ```

2. **Create and activate a virtual environment:**

   ```bash
   # For Unix/macOS
   python3 -m venv .venv
   source .venv/bin/activate

   # For Windows
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install the project and its dependencies:**
   The `-e` flag (editable) allows you to modify the source code and have the changes immediately reflected. The `[test]` part installs testing libraries like `pytest`.

   ```bash
   pip install -e ".[test]"
   ```

## Configuration

The entire simulation is controlled by a single configuration file.

1. **Create your configuration:**
   In the `config/` directory, copy the template file:

   ```bash
   cp config/template.yaml config/default.yaml
   ```

2. **Customize `config/default.yaml`:**
   Open `config/default.yaml` in your favorite editor and adjust the values to reflect your personal financial situation. This is the most crucial step to getting meaningful results.

## Usage

The project is run from the command line using the `finance-sim` script created during installation.

### Run a Simulation

To run the simulation using the default configuration file (`config/default.yaml`):

```bash
finance-sim run
```

To specify a different configuration file, use the `--config` or `-c` option. This is useful for modeling different scenarios (e.g., "with-car" vs. "no-car").

```bash
finance-sim run --config config/another_scenario.yaml
```

### Run Tests

To ensure everything is working correctly, you can run the project's test suite:

```bash
finance-sim test
```

## Understanding the Output

After a successful run, you will see two main outputs:

1. **Console Tables**: A detailed summary of your daily, monthly, and yearly expenses, along with a breakdown of your investment allocations, will be printed to the console.

   _Example Console Output:_

   ```
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃                      Expense Simulation Summary (Daily Averages)                      ┃
    ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
    │ Expense Category              │ Daily Avg │ Monthly Avg │ Yearly Avg   │
    ├───────────────────────────────┼───────────┼─────────────┼──────────────┤
    │ Transport                     │  ₹105.14  │  ₹3,200.08  │  ₹38,401.00  │
    │ Food                          │  ₹450.00  │  ₹13,696.88 │  ₹164,362.50 │
    │ Social                        │  ₹200.00  │  ₹6,087.50  │  ₹73,050.00  │
    │ ...                           │    ...    │     ...     │      ...     │
    │ Professional And Financial    │  ₹375.31  │  ₹11,424.32 │  ₹137,091.86 │
    │ Hobbies                       │   ₹26.29  │    ₹799.98  │   ₹9,599.75  │
    ├───────────────────────────────┴───────────┴─────────────┴──────────────┤
    │ Total Estimated Expenses      │ ₹2,166.45 │ ₹65,938.81  │ ₹791,265.75  │
    └─────────────────────────────────────────────────────────────────────────┘
   ```

2. **Visual Reports**: Two PNG images will be saved to the `reports/` directory:
   - `expense_breakdown.png`: A pie chart showing the proportion of each expense category.
   - `daily_cost_distribution.png`: A histogram showing the frequency of different total daily costs. This is crucial for understanding your financial risk and variability.

## Project Structure

The project is organized with a clear separation of concerns to promote maintainability and extensibility.

```
personal-finance-simulator/
├── config/
│   └── template.yaml         # A template to base new configurations on
├── reports/                  # Output directory for generated charts
│   ├── expense_breakdown.png
│   └── daily_cost_distribution.png
├── src/
│   ├── __init__.py
│   ├── components.py         # Core simulation logic for different expense types
│   ├── config_loader.py      # Pydantic models for loading and validating config
│   ├── model.py              # Orchestrator for running simulation components
│   └── reporting.py          # Logic for generating console and visual reports
├── tests/                    # Unit and integration tests
├── main.py                   # Entry point for the Typer CLI application
├── pyproject.toml            # Project metadata and dependencies
└── README.md                 # This file
```

## How It Works: Technical Details

- **Configuration Loading**: `Pydantic` is used to define a strict schema for the `config.yaml`. This ensures that the configuration is valid before the simulation starts, preventing runtime errors.
- **Simulation Core**: The `ExpenseModel` class in `model.py` acts as an orchestrator. It maintains a list of "expense components"—functions that simulate a specific part of your finances.
- **Expense Components**: Each function in `components.py` models a different financial aspect:
  - `simulate_daily_variable_expenses`: Uses `numpy.random.multivariate_normal` to generate samples of correlated expenses (transport, food, social). This is the statistical heart of the simulation.
  - `simulate_periodic_expenses`: Converts fixed monthly/yearly costs into a daily average and simulates semi-variable costs like vehicle maintenance using a `lognormal` distribution to model its right-skewed nature (many small costs, few very large costs).
- **Aggregation**: The main `run_simulation` method calls each registered component, and the results (which are `pandas` DataFrames) are concatenated to form a complete picture of all expenses for every trial.
