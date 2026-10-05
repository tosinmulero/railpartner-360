from __future__ import annotations

from pathlib import Path
from datetime import timedelta
import json

import numpy as np
import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.yaml"
OUTPUT_DIR = PROJECT_ROOT / "data" / "synthetic"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


CONFIG = load_config()

SEED = int(CONFIG["data_generation"]["random_seed"])
N_CUSTOMERS = int(CONFIG["data_generation"]["customers"])
N_PARTNERS = int(CONFIG["data_generation"]["partners"])
START_DATE = pd.Timestamp(CONFIG["data_generation"]["start_date"])
END_DATE = pd.Timestamp(CONFIG["data_generation"]["end_date"])

rng = np.random.default_rng(SEED)


# ============================================================
# HELPERS
# ============================================================

def save_table(df: pd.DataFrame, name: str) -> None:
    parquet_path = OUTPUT_DIR / f"{name}.parquet"
    csv_path = OUTPUT_DIR / f"{name}.csv"

    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False)

    print(
        f"[SAVED] {name:<20} "
        f"rows={len(df):>10,} "
        f"columns={len(df.columns):>3}"
    )


def random_dates(start: pd.Timestamp, end: pd.Timestamp, n: int) -> pd.Series:
    total_days = (end - start).days

    offsets = rng.integers(
        low=0,
        high=total_days + 1,
        size=n,
    )

    return pd.Series(start + pd.to_timedelta(offsets, unit="D"))


# ============================================================
# DIM PARTNER
# ============================================================

def generate_partners() -> pd.DataFrame:

    partner_types = np.array([
        "Corporate Travel Platform",
        "Online Travel Agency",
        "Expense Management Platform",
        "Rail Retail Partner",
        "Business Travel Agency",
        "Mobility Platform",
    ])

    segments = np.array([
        "Enterprise",
        "Mid-Market",
        "SMB",
    ])

    service_tiers = np.array([
        "Strategic",
        "Premium",
        "Standard",
    ])

    regions = np.array([
        "United Kingdom",
        "France",
        "Germany",
        "Spain",
        "Italy",
        "Netherlands",
        "Belgium",
        "Ireland",
    ])

    acquisition_channels = np.array([
        "Direct Sales",
        "Strategic Partnership",
        "Inbound",
        "Referral",
        "Industry Partnership",
    ])

    partner_type_values = rng.choice(
        partner_types,
        N_PARTNERS,
        p=[0.22, 0.16, 0.16, 0.20, 0.16, 0.10],
    )

    segment_values = rng.choice(
        segments,
        N_PARTNERS,
        p=[0.30, 0.42, 0.28],
    )

    service_values = []

    for segment in segment_values:
        if segment == "Enterprise":
            service_values.append(
                rng.choice(
                    service_tiers,
                    p=[0.60, 0.30, 0.10],
                )
            )
        elif segment == "Mid-Market":
            service_values.append(
                rng.choice(
                    service_tiers,
                    p=[0.18, 0.52, 0.30],
                )
            )
        else:
            service_values.append(
                rng.choice(
                    service_tiers,
                    p=[0.05, 0.25, 0.70],
                )
            )

    contract_dates = random_dates(
        pd.Timestamp("2019-01-01"),
        pd.Timestamp("2026-01-01"),
        N_PARTNERS,
    )

    commission_rates = []

    for segment in segment_values:
        if segment == "Enterprise":
            value = rng.uniform(0.025, 0.055)
        elif segment == "Mid-Market":
            value = rng.uniform(0.035, 0.070)
        else:
            value = rng.uniform(0.045, 0.085)

        commission_rates.append(round(value, 4))

    partners = pd.DataFrame({
        "partner_id": [
            f"P{i:04d}"
            for i in range(1, N_PARTNERS + 1)
        ],
        "partner_name": [
            f"Rail Commerce Partner {i:03d}"
            for i in range(1, N_PARTNERS + 1)
        ],
        "partner_type": partner_type_values,
        "partner_segment": segment_values,
        "service_tier": service_values,
        "headquarters_region": rng.choice(
            regions,
            N_PARTNERS,
            p=[
                0.44,
                0.10,
                0.10,
                0.08,
                0.08,
                0.07,
                0.06,
                0.07,
            ],
        ),
        "acquisition_channel": rng.choice(
            acquisition_channels,
            N_PARTNERS,
            p=[0.32, 0.27, 0.15, 0.10, 0.16],
        ),
        "contract_start_date": contract_dates,
        "commission_rate": commission_rates,
        "active_flag": rng.choice(
            [True, False],
            N_PARTNERS,
            p=[0.94, 0.06],
        ),
    })

    return partners.sort_values("partner_id").reset_index(drop=True)


# ============================================================
# DIM CUSTOMER
# ============================================================

def generate_customers() -> pd.DataFrame:

    regions = np.array([
        "London",
        "South East",
        "North West",
        "West Midlands",
        "Yorkshire",
        "East of England",
        "South West",
        "Scotland",
        "Wales",
        "North East",
    ])

    customer_segments = np.array([
        "Frequent Business",
        "Occasional Business",
        "Leisure Frequent",
        "Leisure Occasional",
        "Mixed Traveller",
    ])

    loyalty_tiers = np.array([
        "Bronze",
        "Silver",
        "Gold",
        "Platinum",
    ])

    devices = np.array([
        "Mobile App",
        "Desktop Web",
        "Mobile Web",
        "Tablet",
    ])

    acquisition_channels = np.array([
        "Organic Search",
        "Paid Search",
        "Partner Referral",
        "Direct",
        "Social",
        "Email",
    ])

    age_bands = np.array([
        "18-24",
        "25-34",
        "35-44",
        "45-54",
        "55-64",
        "65+",
    ])

    customer_segment_values = rng.choice(
        customer_segments,
        N_CUSTOMERS,
        p=[0.17, 0.20, 0.19, 0.27, 0.17],
    )

    loyalty_values = []

    for segment in customer_segment_values:

        if segment == "Frequent Business":
            loyalty_values.append(
                rng.choice(
                    loyalty_tiers,
                    p=[0.10, 0.30, 0.38, 0.22],
                )
            )

        elif segment == "Leisure Frequent":
            loyalty_values.append(
                rng.choice(
                    loyalty_tiers,
                    p=[0.18, 0.37, 0.32, 0.13],
                )
            )

        else:
            loyalty_values.append(
                rng.choice(
                    loyalty_tiers,
                    p=[0.48, 0.32, 0.16, 0.04],
                )
            )

    business_flag = np.isin(
        customer_segment_values,
        [
            "Frequent Business",
            "Occasional Business",
            "Mixed Traveller",
        ],
    )

    customers = pd.DataFrame({
        "customer_id": [
            f"C{i:07d}"
            for i in range(1, N_CUSTOMERS + 1)
        ],
        "signup_date": random_dates(
            pd.Timestamp("2018-01-01"),
            END_DATE,
            N_CUSTOMERS,
        ),
        "customer_segment": customer_segment_values,
        "home_region": rng.choice(
            regions,
            N_CUSTOMERS,
            p=[
                0.24,
                0.14,
                0.11,
                0.09,
                0.09,
                0.08,
                0.08,
                0.07,
                0.05,
                0.05,
            ],
        ),
        "loyalty_tier": loyalty_values,
        "preferred_device": rng.choice(
            devices,
            N_CUSTOMERS,
            p=[0.59, 0.22, 0.15, 0.04],
        ),
        "acquisition_channel": rng.choice(
            acquisition_channels,
            N_CUSTOMERS,
            p=[0.25, 0.18, 0.19, 0.20, 0.08, 0.10],
        ),
        "age_band": rng.choice(
            age_bands,
            N_CUSTOMERS,
            p=[0.09, 0.29, 0.25, 0.18, 0.12, 0.07],
        ),
        "business_traveller_flag": business_flag,
        "marketing_opt_in": rng.choice(
            [True, False],
            N_CUSTOMERS,
            p=[0.61, 0.39],
        ),
    })

    return customers


# ============================================================
# DIM OPERATOR
# ============================================================

def generate_operators() -> pd.DataFrame:

    operator_names = [
        "Northern Connect Rail",
        "Capital Intercity",
        "Western Express",
        "Midlands Railways",
        "Coastal Link",
        "Highland Connect",
        "Eastern Regional",
        "Central Metro Rail",
        "CrossCountry Connect",
        "Anglia Rail Services",
        "Welsh Regional Rail",
        "Southern Coast Rail",
    ]

    service_types = [
        "Regional",
        "Intercity",
        "Intercity",
        "Regional",
        "Regional",
        "Regional",
        "Regional",
        "Commuter",
        "Intercity",
        "Regional",
        "Regional",
        "Commuter",
    ]

    operators = pd.DataFrame({
        "operator_id": [
            f"O{i:03d}"
            for i in range(1, len(operator_names) + 1)
        ],
        "operator_name": operator_names,
        "service_type": service_types,
        "synthetic_flag": True,
    })

    return operators


# ============================================================
# DIM STATION
# ============================================================

def generate_stations(n_stations: int = 250) -> pd.DataFrame:

    regions = np.array([
        "London",
        "South East",
        "North West",
        "West Midlands",
        "Yorkshire",
        "East of England",
        "South West",
        "Scotland",
        "Wales",
        "North East",
    ])

    region_probs = np.array([
        0.18,
        0.14,
        0.12,
        0.10,
        0.10,
        0.09,
        0.09,
        0.08,
        0.05,
        0.05,
    ])

    station_categories = np.array([
        "Major Hub",
        "Large",
        "Medium",
        "Local",
    ])

    category_probs = np.array([
        0.05,
        0.15,
        0.35,
        0.45,
    ])

    selected_regions = rng.choice(
        regions,
        n_stations,
        p=region_probs,
    )

    selected_categories = rng.choice(
        station_categories,
        n_stations,
        p=category_probs,
    )

    annual_entries = []

    for category in selected_categories:

        if category == "Major Hub":
            value = rng.integers(20_000_000, 75_000_000)

        elif category == "Large":
            value = rng.integers(5_000_000, 20_000_000)

        elif category == "Medium":
            value = rng.integers(800_000, 5_000_000)

        else:
            value = rng.integers(40_000, 800_000)

        annual_entries.append(int(value))

    stations = pd.DataFrame({
        "station_id": [
            f"S{i:04d}"
            for i in range(1, n_stations + 1)
        ],
        "station_code": [
            f"RP{i:03d}"
            for i in range(1, n_stations + 1)
        ],
        "station_name": [
            f"RailPartner Station {i:03d}"
            for i in range(1, n_stations + 1)
        ],
        "region": selected_regions,
        "station_category": selected_categories,
        "annual_entries_estimate": annual_entries,
        "interchange_flag": [
            category in ["Major Hub", "Large"]
            or rng.random() < 0.14
            for category in selected_categories
        ],
        "synthetic_flag": True,
    })

    return stations


# ============================================================
# DIM ROUTE
# ============================================================

def generate_routes(
    stations: pd.DataFrame,
    operators: pd.DataFrame,
    n_routes: int = 1200,
) -> pd.DataFrame:

    station_ids = stations["station_id"].to_numpy()
    operator_ids = operators["operator_id"].to_numpy()

    route_pairs = set()

    while len(route_pairs) < n_routes:

        origin = rng.choice(station_ids)
        destination = rng.choice(station_ids)

        if origin == destination:
            continue

        pair = (origin, destination)

        if pair not in route_pairs:
            route_pairs.add(pair)

    route_pairs = list(route_pairs)

    distances = np.round(
        rng.gamma(
            shape=2.3,
            scale=62,
            size=n_routes,
        ) + 8,
        1,
    )

    distances = np.clip(distances, 8, 720)

    route_types = []

    planned_minutes = []

    for distance in distances:

        if distance >= 220:
            route_type = "Intercity"
            speed = rng.uniform(85, 120)

        elif distance >= 80:
            route_type = "Regional"
            speed = rng.uniform(60, 90)

        else:
            route_type = "Commuter"
            speed = rng.uniform(40, 70)

        duration = max(
            12,
            round((distance / speed) * 60 + rng.uniform(4, 22)),
        )

        route_types.append(route_type)
        planned_minutes.append(duration)

    routes = pd.DataFrame({
        "route_id": [
            f"R{i:05d}"
            for i in range(1, n_routes + 1)
        ],
        "origin_station_id": [
            pair[0]
            for pair in route_pairs
        ],
        "destination_station_id": [
            pair[1]
            for pair in route_pairs
        ],
        "primary_operator_id": rng.choice(
            operator_ids,
            n_routes,
        ),
        "distance_km": distances,
        "route_type": route_types,
        "planned_duration_minutes": planned_minutes,
        "active_flag": rng.choice(
            [True, False],
            n_routes,
            p=[0.985, 0.015],
        ),
    })

    return routes


# ============================================================
# DIM TICKET
# ============================================================

def generate_tickets() -> pd.DataFrame:

    ticket_data = [
        (
            "T001",
            "Advance Single",
            "Single",
            "Advance",
            False,
            False,
        ),
        (
            "T002",
            "Anytime Single",
            "Single",
            "Anytime",
            True,
            True,
        ),
        (
            "T003",
            "Off-Peak Single",
            "Single",
            "Off-Peak",
            True,
            True,
        ),
        (
            "T004",
            "Advance Return",
            "Return",
            "Advance",
            False,
            False,
        ),
        (
            "T005",
            "Anytime Return",
            "Return",
            "Anytime",
            True,
            True,
        ),
        (
            "T006",
            "Off-Peak Return",
            "Return",
            "Off-Peak",
            True,
            True,
        ),
        (
            "T007",
            "Business Flexible",
            "Single",
            "Flexible",
            True,
            True,
        ),
        (
            "T008",
            "Business Return",
            "Return",
            "Flexible",
            True,
            True,
        ),
    ]

    tickets = pd.DataFrame(
        ticket_data,
        columns=[
            "ticket_id",
            "ticket_name",
            "journey_type",
            "fare_category",
            "refundable_flag",
            "changeable_flag",
        ],
    )

    return tickets


# ============================================================
# DIM DATE
# ============================================================

def generate_date_dimension() -> pd.DataFrame:

    dates = pd.date_range(
        START_DATE,
        END_DATE,
        freq="D",
    )

    df = pd.DataFrame({
        "date": dates,
    })

    df["date_id"] = (
        df["date"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    df["year"] = df["date"].dt.year
    df["quarter"] = "Q" + df["date"].dt.quarter.astype(str)
    df["month_number"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.month_name()
    df["year_month"] = df["date"].dt.strftime("%Y-%m")
    df["week_number"] = df["date"].dt.isocalendar().week.astype(int)
    df["day_of_month"] = df["date"].dt.day
    df["day_name"] = df["date"].dt.day_name()
    df["day_of_week"] = df["date"].dt.dayofweek + 1
    df["weekend_flag"] = df["date"].dt.dayofweek >= 5

    df["season"] = np.select(
        [
            df["month_number"].isin([12, 1, 2]),
            df["month_number"].isin([3, 4, 5]),
            df["month_number"].isin([6, 7, 8]),
        ],
        [
            "Winter",
            "Spring",
            "Summer",
        ],
        default="Autumn",
    )

    columns = [
        "date_id",
        "date",
        "year",
        "quarter",
        "month_number",
        "month_name",
        "year_month",
        "week_number",
        "day_of_month",
        "day_name",
        "day_of_week",
        "weekend_flag",
        "season",
    ]

    return df[columns]


# ============================================================
# VALIDATION
# ============================================================

def validate_unique_key(
    df: pd.DataFrame,
    key: str,
    table_name: str,
) -> None:

    if df[key].isna().any():
        raise ValueError(
            f"{table_name}.{key} contains NULL values."
        )

    if df[key].duplicated().any():
        raise ValueError(
            f"{table_name}.{key} contains duplicate values."
        )


def validate_foreign_key(
    fact_df: pd.DataFrame,
    fact_key: str,
    dimension_df: pd.DataFrame,
    dimension_key: str,
    description: str,
) -> None:

    missing = (
        set(fact_df[fact_key])
        - set(dimension_df[dimension_key])
    )

    if missing:
        raise ValueError(
            f"Foreign-key validation failed: {description}"
        )


def validate_dimensions(
    partners: pd.DataFrame,
    customers: pd.DataFrame,
    operators: pd.DataFrame,
    stations: pd.DataFrame,
    routes: pd.DataFrame,
    tickets: pd.DataFrame,
    dates: pd.DataFrame,
) -> None:

    validate_unique_key(
        partners,
        "partner_id",
        "dim_partner",
    )

    validate_unique_key(
        customers,
        "customer_id",
        "dim_customer",
    )

    validate_unique_key(
        operators,
        "operator_id",
        "dim_operator",
    )

    validate_unique_key(
        stations,
        "station_id",
        "dim_station",
    )

    validate_unique_key(
        routes,
        "route_id",
        "dim_route",
    )

    validate_unique_key(
        tickets,
        "ticket_id",
        "dim_ticket",
    )

    validate_unique_key(
        dates,
        "date_id",
        "dim_date",
    )

    validate_foreign_key(
        routes,
        "origin_station_id",
        stations,
        "station_id",
        "route origin",
    )

    validate_foreign_key(
        routes,
        "destination_station_id",
        stations,
        "station_id",
        "route destination",
    )

    validate_foreign_key(
        routes,
        "primary_operator_id",
        operators,
        "operator_id",
        "route operator",
    )

    if (
        routes["origin_station_id"]
        == routes["destination_station_id"]
    ).any():

        raise ValueError(
            "Route origin and destination cannot be identical."
        )

    print("\n[OK] Primary-key validation passed")
    print("[OK] Foreign-key validation passed")
    print("[OK] Route validation passed")


# ============================================================
# DATA PROFILE
# ============================================================

def create_manifest(tables: dict[str, pd.DataFrame]) -> None:

    manifest = {}

    for name, df in tables.items():

        manifest[name] = {
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "column_names": list(df.columns),
        }

    manifest_path = OUTPUT_DIR / "dimension_manifest.json"

    with open(
        manifest_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            manifest,
            file,
            indent=4,
            default=str,
        )

    print(
        f"\n[SAVED] dimension_manifest.json"
    )


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    print("=" * 72)
    print("RAILPARTNER 360")
    print("SYNTHETIC DIMENSION GENERATION")
    print("=" * 72)

    print(f"\nRandom seed: {SEED}")
    print(f"Customers: {N_CUSTOMERS:,}")
    print(f"Partners: {N_PARTNERS:,}")
    print(f"Analysis period: {START_DATE.date()} to {END_DATE.date()}")

    print("\nGenerating dimensions...")

    partners = generate_partners()
    customers = generate_customers()
    operators = generate_operators()
    stations = generate_stations()
    routes = generate_routes(
        stations,
        operators,
    )
    tickets = generate_tickets()
    dates = generate_date_dimension()

    print("\nValidating dimensions...")

    validate_dimensions(
        partners,
        customers,
        operators,
        stations,
        routes,
        tickets,
        dates,
    )

    tables = {
        "dim_partner": partners,
        "dim_customer": customers,
        "dim_operator": operators,
        "dim_station": stations,
        "dim_route": routes,
        "dim_ticket": tickets,
        "dim_date": dates,
    }

    print("\nSaving datasets...")
    print("-" * 72)

    for name, dataframe in tables.items():
        save_table(
            dataframe,
            name,
        )

    create_manifest(tables)

    print("\n" + "=" * 72)
    print("DIMENSION GENERATION COMPLETE")
    print("=" * 72)

    print("\nTABLE SUMMARY")
    print("-" * 72)

    for name, dataframe in tables.items():
        print(
            f"{name:<20} "
            f"{len(dataframe):>12,} rows"
        )

    print("\nTOTAL DIMENSION ROWS:")
    print(
        f"{sum(len(df) for df in tables.values()):,}"
    )

    print("\nOutput location:")
    print(OUTPUT_DIR)

    print("\nSTAGE 2 COMPLETE")


if __name__ == "__main__":
    main()
