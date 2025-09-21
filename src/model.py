import pandas as pd
import numpy as np
from typing import Callable, Dict
from src.config_loader import Config


class ExpenseModel:
    """Orchestrates the simulation by managing a list of expense components."""

    # Define a type hint for our functional components for clarity.
    # We expect each component to return a DataFrame for easy concatenation.
    ExpenseFunc = Callable[[Config, np.random.Generator], pd.DataFrame]

    def __init__(self, config: Config):
        self.config = config
        self.rng = np.random.default_rng(config.simulation.random_seed)
        self.expense_functions: Dict[str, "ExpenseModel.ExpenseFunc"] = {}

    def register(self, func: "ExpenseModel.ExpenseFunc"):
        """
        Registers an expense simulation function.
        The function's name is used as the component name.
        """
        component_name = func.__name__
        self.expense_functions[component_name] = func
        print(f"✔️ Registered expense component: {component_name}")

    def run_simulation(self) -> pd.DataFrame:
        """Runs the simulation for all registered components and aggregates results."""
        if not self.expense_functions:
            raise ValueError("No expense functions have been registered.")

        # Each registered function returns a DataFrame. We concatenate them all horizontally.
        all_results_dfs = [
            func(self.config, self.rng) for func in self.expense_functions.values()
        ]

        return pd.concat(all_results_dfs, axis=1)
