import numpy as np
import pandas as pd
from scipy.stats import lognorm, beta
import datetime
from src.config_loader import Config


def get_seasonality_multipliers() -> dict[str, float]:
    """
    Returns seasonality multipliers for different expense categories based on the current month.

    This model increases social and household spending during the Indian festival
    season (Oct/Nov) and utility costs during peak summer (May).

    Returns:
        A dictionary mapping expense categories to their monthly multiplier.
    """
    current_month = datetime.datetime.now().month

    # Default multipliers
    multipliers = {
        "social": 1.0,
        "household": 1.0,
        "food": 1.0,
        # Other categories can be added here
    }

    # Festival Season (Dussehra/Diwali)
    if current_month in [10, 11]:
        multipliers["social"] = 1.3  # 30% increase in social/gifting
        multipliers["household"] = 1.1  # 10% increase in household/groceries

    # Peak Summer
    if current_month == 5:
        # This would be applied to a "utilities" sub-category if it were variable
        pass

    return multipliers


def _calculate_analytical_transport_stats(config: Config) -> tuple[float, float]:
    """
    Calculates the analytical mean and standard deviation of daily transport costs.
    This is needed as an input for the correlated multivariate simulation.
    """
    c_transport = config.transport
    p_workday = config.time.workdays_per_month / config.time.days_in_month

    # Probabilities of each commute type
    p_bike = c_transport.bike_days_per_month / config.time.days_in_month
    p_hitch_any = c_transport.hitch_days_per_month / config.time.days_in_month
    p_hitch_two_way = p_hitch_any * c_transport.hitch_two_way_frac
    p_rare = c_transport.rare_hitch_rapido_prob
    p_one_way_non_combo = p_hitch_any - p_hitch_two_way - p_rare
    p_metro = 1.0 - (sum([p_bike, p_hitch_two_way, p_one_way_non_combo, p_rare]))

    probs = np.array([p_bike, p_hitch_two_way, p_one_way_non_combo, p_rare, p_metro])

    # Costs associated with each commute type on a workday
    km_work = np.array([c_transport.office_oneway_km * 2, 0, 0, 0, 0])
    km_gym_transport = c_transport.gym_oneway_km * 2
    bike_km = (km_work + km_gym_transport) * p_workday  # Expected km only on workdays
    fuel_cost = (bike_km / c_transport.bike_kmpl) * c_transport.petrol_price_rs_per_l
    nonfuel_cost = (
        np.array(
            [
                0,
                0,
                c_transport.metro_one_way_rs,
                c_transport.rare_rapido_rs,
                c_transport.metro_one_way_rs * 2,
            ]
        )
        * p_workday
    )

    daily_costs = fuel_cost + nonfuel_cost

    # Calculate analytical mean and variance
    expected_mean = np.sum(probs * daily_costs)
    expected_variance = np.sum(probs * (daily_costs - expected_mean) ** 2)
    expected_std = np.sqrt(expected_variance)

    return expected_mean, expected_std


def simulate_daily_variable_expenses(
    config: Config, rng: np.random.Generator
) -> pd.DataFrame:
    """
    Simulates all daily variable expenses (transport, food, social)
    considering their inter-correlations.
    """
    n_trials = config.simulation.mc_trials
    var_exp = config.variable_expenses

    # 1. Get analytical stats for transport to use in the correlated model
    transport_mean, transport_std = _calculate_analytical_transport_stats(config)

    # 2. Combine with other variable expense stats from config
    means = np.array([transport_mean, var_exp.means["food"], var_exp.means["social"]])
    stds = np.array([transport_std, var_exp.stds["food"], var_exp.stds["social"]])
    corr_matrix = np.array(var_exp.correlation_matrix)

    # 3. Create covariance matrix and generate correlated samples
    cov_matrix = np.outer(stds, stds) * corr_matrix
    samples = rng.multivariate_normal(means, cov_matrix, size=n_trials)

    # 4. Post-processing
    samples[samples < 0] = 0  # Ensure no negative expenses

    # Apply seasonality multipliers
    seasonality = get_seasonality_multipliers()
    samples[:, 1] *= seasonality.get("food", 1.0)  # Food is the 2nd column
    samples[:, 2] *= seasonality.get("social", 1.0)  # Social is the 3rd column

    return pd.DataFrame(samples, columns=["transport", "food", "social"])


def simulate_periodic_expenses(
    config: Config, rng: np.random.Generator
) -> pd.DataFrame:
    """
    Calculates the daily average for each periodic expense sub-category
    and simulates semi-variable costs like maintenance.
    """
    n_trials = config.simulation.mc_trials
    c = config.periodic_expenses
    days_in_month = config.time.days_in_month

    # --- Calculate daily averages for each category individually ---
    subscriptions_monthly = (
        c.subscriptions.internet_monthly
        + (c.subscriptions.mobile_90_days / 3)
        + c.subscriptions.google_one_monthly
        + c.subscriptions.spotify_monthly
        + c.subscriptions.news_monthly
        + c.subscriptions.other_apps_monthly
        + (c.subscriptions.cloud_backup_yearly / 12)
        + (c.subscriptions.antivirus_yearly / 12)
    )
    household_monthly = (
        c.household.rent_contribution_monthly
        + c.household.society_maintenance_monthly
        + c.household.groceries_monthly
        + c.household.utilities_monthly
        + c.household.emergency_repair_fund_monthly
        + c.household.appliance_replacement_fund_monthly
        + c.household.wfh_equipment_fund_monthly
        + (c.household.seasonal_clothing_yearly / 12)
    )
    family_support_monthly = (
        c.family_support.child_elder_care_monthly
        + c.family_support.caregiver_wages_monthly
        + c.family_support.school_tuition_monthly
        + c.family_support.education_fund_monthly
    )
    medical_monthly = (
        c.medical.consumables_monthly
        + c.medical.long_term_meds_monthly
        + (c.medical.specialist_consultations_yearly / 12)
        + (c.medical.dental_procedures_yearly / 12)
        + (c.medical.optical_costs_yearly / 12)
        + (c.medical.emergency_buffer_yearly / 12)
        + (c.medical.health_checkup_yearly / 12)
    )
    insurance_loans_monthly = (
        c.insurance_and_loans.loan_emi_monthly
        + c.insurance_and_loans.credit_card_payment_monthly
        + (c.insurance_and_loans.life_insurance_yearly / 12)
        + (c.insurance_and_loans.hospitalization_copay_yearly / 12)
    )
    professional_financial_monthly = (
        (c.professional_and_financial.income_tax_provision_yearly / 12)
        + (c.professional_and_financial.bank_charges_yearly / 12)
        + (c.professional_and_financial.investment_platform_fees_yearly / 12)
        + (c.professional_and_financial.advisory_fees_yearly / 12)
        + (c.professional_and_financial.legal_services_yearly / 12)
        + (c.professional_and_financial.professional_license_yearly / 12)
        + (c.professional_and_financial.tax_filing_assistance_yearly / 12)
    )
    misc_monthly = (
        c.miscellaneous.donations_monthly
        + c.miscellaneous.pet_care_monthly
        + c.miscellaneous.inflation_buffer_monthly
        + (c.miscellaneous.gifts_and_occasions_yearly / 12)
    )

    # Store daily averages in a dictionary
    daily_averages = {
        "memberships": (c.memberships.gym_yearly / 365.25),
        "subscriptions": subscriptions_monthly / days_in_month,
        "household": household_monthly / days_in_month,
        "family_support": family_support_monthly / days_in_month,
        "medical": medical_monthly / days_in_month,
        "insurance_and_loans": insurance_loans_monthly / days_in_month,
        "professional_and_financial": professional_financial_monthly / days_in_month,
        "miscellaneous": misc_monthly / days_in_month,
    }
    df = pd.DataFrame(daily_averages, index=range(n_trials))

    # --- Simulate and add right-skewed and event-based costs ---

    # Bike Maintenance (lognormal)
    c_prof = c.professional_and_financial
    mu = np.log(c_prof.bike_maintenance_mean_monthly) - (
        c_prof.bike_maintenance_sigma**2 / 2
    )
    monthly_maintenance = lognorm.rvs(
        s=c_prof.bike_maintenance_sigma,
        scale=np.exp(mu),
        size=n_trials,
        random_state=rng,
    )
    df["professional_and_financial"] += monthly_maintenance / days_in_month

    # Hobbies/Cricket (event-based)
    c_periodic = config.periodic_expenses
    p_cricket = c_periodic.hobbies.cricket_days_per_month / days_in_month
    is_cricket_day = rng.random(n_trials) < p_cricket
    cricket_samples = rng.uniform(
        c_periodic.hobbies.cricket_cost_min,
        c_periodic.hobbies.cricket_cost_max,
        n_trials,
    )
    df["hobbies"] = np.where(is_cricket_day, cricket_samples, 0)

    return df
