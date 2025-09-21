from pydantic import BaseModel, Field
from pathlib import Path
import yaml
from typing import Dict, List

# --- Nested Configuration Models for Clarity and Structure ---


class TransportConfig(BaseModel):
    """Configuration for daily transport simulation."""

    bike_days_per_month: float = 2.0
    hitch_days_per_month: float = 8.0
    hitch_two_way_frac: float = 0.6
    rare_hitch_rapido_prob: float = 0.05
    office_oneway_km: float = 16.0
    gym_oneway_km: float = 1.0
    bike_kmpl: float = 45.0
    petrol_price_rs_per_l: float = 109.5
    metro_one_way_rs: float = 50.0
    rare_rapido_rs: float = 120.0


class MembershipsConfig(BaseModel):
    gym_yearly: float = 0.0


class SubscriptionsConfig(BaseModel):
    internet_monthly: float = 0.0
    mobile_90_days: float = 0.0
    google_one_monthly: float = 0.0
    spotify_monthly: float = 0.0
    cloud_backup_yearly: float = 0.0
    antivirus_yearly: float = 0.0
    news_monthly: float = 0.0
    other_apps_monthly: float = 0.0


class HouseholdConfig(BaseModel):
    rent_contribution_monthly: float = 0.0
    society_maintenance_monthly: float = 0.0
    groceries_monthly: float = 0.0
    utilities_monthly: float = 0.0
    emergency_repair_fund_monthly: float = 0.0
    appliance_replacement_fund_monthly: float = 0.0
    wfh_equipment_fund_monthly: float = 0.0
    seasonal_clothing_yearly: float = 0.0


class FamilySupportConfig(BaseModel):
    child_elder_care_monthly: float = 0.0
    caregiver_wages_monthly: float = 0.0
    school_tuition_monthly: float = 0.0
    education_fund_monthly: float = 0.0


class MedicalConfig(BaseModel):
    consumables_monthly: float = 0.0
    specialist_consultations_yearly: float = 0.0
    dental_procedures_yearly: float = 0.0
    optical_costs_yearly: float = 0.0
    long_term_meds_monthly: float = 0.0
    emergency_buffer_yearly: float = 0.0
    health_checkup_yearly: float = 0.0


class InsuranceAndLoansConfig(BaseModel):
    life_insurance_yearly: float = 0.0
    hospitalization_copay_yearly: float = 0.0
    loan_emi_monthly: float = 0.0
    credit_card_payment_monthly: float = 0.0


class ProfessionalAndFinancialConfig(BaseModel):
    income_tax_provision_yearly: float = 0.0
    bank_charges_yearly: float = 0.0
    investment_platform_fees_yearly: float = 0.0
    advisory_fees_yearly: float = 0.0
    legal_services_yearly: float = 0.0
    professional_license_yearly: float = 0.0
    tax_filing_assistance_yearly: float = 0.0
    bike_maintenance_mean_monthly: float = 0.0
    bike_maintenance_sigma: float = 1.0


class MiscellaneousConfig(BaseModel):
    gifts_and_occasions_yearly: float = 0.0
    donations_monthly: float = 0.0
    pet_care_monthly: float = 0.0
    inflation_buffer_monthly: float = 0.0


class HobbiesConfig(BaseModel):
    cricket_days_per_month: float = 2.0
    cricket_cost_min: float = 300.0
    cricket_cost_max: float = 500.0


class PeriodicExpensesConfig(BaseModel):
    """A unified, nested model for all periodic, fixed, or semi-variable expenses."""

    memberships: MembershipsConfig
    subscriptions: SubscriptionsConfig
    household: HouseholdConfig
    family_support: FamilySupportConfig
    medical: MedicalConfig
    insurance_and_loans: InsuranceAndLoansConfig
    professional_and_financial: ProfessionalAndFinancialConfig
    miscellaneous: MiscellaneousConfig
    hobbies: HobbiesConfig


# --- Main Configuration Models ---


class SimulationConfig(BaseModel):
    mc_trials: int = Field(200000, gt=0)
    random_seed: int = 42


class TimeConfig(BaseModel):
    days_in_month: float = Field(30.4375, gt=0)
    workdays_per_month: int = Field(22, gt=0)


class FinancialsConfig(BaseModel):
    monthly_investable_amount: float = Field(0.0, ge=0)
    active_investment_profile: str = "Balanced"


class VariableExpensesConfig(BaseModel):
    seasonality: Dict[str, float]
    means: Dict[str, float]
    stds: Dict[str, float]
    correlation_matrix: List[List[float]]


class Config(BaseModel):
    """The root configuration model validated by Pydantic."""

    simulation: SimulationConfig
    time: TimeConfig
    financials: FinancialsConfig
    transport: TransportConfig  # Added Transport config
    variable_expenses: VariableExpensesConfig
    periodic_expenses: PeriodicExpensesConfig
    investment_profiles: Dict[str, Dict[str, float]]


def load_config(path: Path = Path("config/default.yaml")) -> Config:
    """Loads, validates, and returns the configuration from a YAML file."""
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found at: {path}")

    with open(path, "r") as f:
        raw_config = yaml.safe_load(f)

    return Config(**raw_config)
