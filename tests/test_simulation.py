import pytest
import pandas as pd
import numpy as np

# Assuming the project structure allows these imports from the 'src' directory
from src.config_loader import load_config, Config
from src.simulation.components import (
    simulate_daily_variable_expenses,
    simulate_periodic_expenses,
)


@pytest.fixture(scope="module")
def config() -> Config:
    """Loads the default configuration for testing."""
    # Assuming the test is run from the project root where 'config/default.yaml' is accessible
    return load_config()


@pytest.fixture(scope="module")
def rng(config: Config) -> np.random.Generator:
    """Creates a seeded random number generator for consistent test results."""
    return np.random.default_rng(config.simulation.random_seed)


def test_daily_variable_simulation_output(config: Config, rng: np.random.Generator):
    """Test the shape and columns of the variable expenses simulation."""
    df = simulate_daily_variable_expenses(config, rng)
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == config.simulation.mc_trials

    # FIX: The simulation now explicitly includes 'transport' in its output,
    # which is not listed under variable_expenses.means in the config.
    # The test should check for the actual, hardcoded output columns.
    expected_cols = ["transport", "food", "social"]
    assert list(df.columns) == expected_cols


def test_periodic_simulation_output(config: Config, rng: np.random.Generator):
    """Test the shape and columns of the periodic expenses simulation."""
    df = simulate_periodic_expenses(config, rng)
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == config.simulation.mc_trials

    # FIX: The simulation logic was updated to output detailed categories
    # instead of a single 'fixed_expenses' column. This test now verifies
    # that all the new, specific category columns are present.
    expected_cols = [
        "memberships",
        "subscriptions",
        "household",
        "family_support",
        "medical",
        "insurance_and_loans",
        "professional_and_financial",
        "miscellaneous",
        "hobbies",
    ]
    assert all(col in df.columns for col in expected_cols)
    assert len(df.columns) == len(expected_cols)
