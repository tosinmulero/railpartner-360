from __future__ import annotations

from pathlib import Path
import json
import gc

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import yaml


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_PATH = PROJECT_ROOT / "config.yaml"

INPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
)

OUTPUT_DIR = INPUT_DIR

SEARCH_OUTPUT = (
    OUTPUT_DIR
    / "fact_searches.parquet"
)

BOOKING_OUTPUT = (
    OUTPUT_DIR
    / "fact_bookings.parquet"
)

SEARCH_SAMPLE_OUTPUT = (
    OUTPUT_DIR
    / "fact_searches_sample.csv"
)

BOOKING_SAMPLE_OUTPUT = (
    OUTPUT_DIR
    / "fact_bookings_sample.csv"
)

MANIFEST_OUTPUT = (
    OUTPUT_DIR
    / "transaction_manifest.json"
)


def load_config() -> dict:

    with open(
        CONFIG_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        return yaml.safe_load(file)


CONFIG = load_config()

SEED = int(
    CONFIG["data_generation"]["random_seed"]
)

TOTAL_SEARCHES = int(
    CONFIG["data_generation"]["searches"]
)

TOTAL_BOOKINGS = int(
    CONFIG["data_generation"]["bookings"]
)

CHUNK_SIZE = 200_000

rng = np.random.default_rng(SEED + 1000)


# ============================================================
# LOAD DIMENSIONS
# ============================================================

def load_dimensions():

    print("\nLoading dimension tables...")

    customers = pd.read_parquet(
        INPUT_DIR / "dim_customer.parquet"
    )

    partners = pd.read_parquet(
        INPUT_DIR / "dim_partner.parquet"
    )

    routes = pd.read_parquet(
        INPUT_DIR / "dim_route.parquet"
    )

    stations = pd.read_parquet(
        INPUT_DIR / "dim_station.parquet"
    )

    tickets = pd.read_parquet(
        INPUT_DIR / "dim_ticket.parquet"
    )

    dates = pd.read_parquet(
        INPUT_DIR / "dim_date.parquet"
    )

    print(
        f"[OK] Customers: {len(customers):,}"
    )

    print(
        f"[OK] Partners: {len(partners):,}"
    )

    print(
        f"[OK] Routes: {len(routes):,}"
    )

    print(
        f"[OK] Stations: {len(stations):,}"
    )

    print(
        f"[OK] Tickets: {len(tickets):,}"
    )

    print(
        f"[OK] Dates: {len(dates):,}"
    )

    return (
        customers,
        partners,
        routes,
        stations,
        tickets,
        dates,
    )


# ============================================================
# CUSTOMER SEARCH WEIGHTS
# ============================================================

def create_customer_weights(
    customers: pd.DataFrame,
) -> np.ndarray:

    segment_weights = {
        "Frequent Business": 3.20,
        "Occasional Business": 1.45,
        "Leisure Frequent": 2.20,
        "Leisure Occasional": 0.80,
        "Mixed Traveller": 1.75,
    }

    loyalty_multiplier = {
        "Bronze": 0.90,
        "Silver": 1.05,
        "Gold": 1.25,
        "Platinum": 1.50,
    }

    weights = (
        customers["customer_segment"]
        .map(segment_weights)
        .astype(float)
        .to_numpy(copy=True)
    )

    weights *= (
        customers["loyalty_tier"]
        .map(loyalty_multiplier)
        .astype(float)
        .to_numpy(copy=True)
    )

    weights /= weights.sum()

    return weights


# ============================================================
# PARTNER WEIGHTS
# ============================================================

def create_partner_weights(
    partners: pd.DataFrame,
) -> np.ndarray:

    segment_weights = {
        "Enterprise": 5.00,
        "Mid-Market": 2.50,
        "SMB": 1.00,
    }

    tier_weights = {
        "Strategic": 1.60,
        "Premium": 1.25,
        "Standard": 1.00,
    }

    weights = (
        partners["partner_segment"]
        .map(segment_weights)
        .astype(float)
        .to_numpy(copy=True)
    )

    weights *= (
        partners["service_tier"]
        .map(tier_weights)
        .astype(float)
        .to_numpy(copy=True)
    )

    weights *= np.where(
        partners["active_flag"].to_numpy(copy=True),
        1.0,
        0.05,
    )

    weights /= weights.sum()

    return weights


# ============================================================
# ROUTE WEIGHTS
# ============================================================

def create_route_weights(
    routes: pd.DataFrame,
    stations: pd.DataFrame,
) -> np.ndarray:

    station_usage = (
        stations
        .set_index("station_id")
        ["annual_entries_estimate"]
        .to_dict()
    )

    origin_usage = (
        routes["origin_station_id"]
        .map(station_usage)
        .astype(float)
        .to_numpy(copy=True)
    )

    destination_usage = (
        routes["destination_station_id"]
        .map(station_usage)
        .astype(float)
        .to_numpy(copy=True)
    )

    popularity = np.sqrt(
        origin_usage
        * destination_usage
    )

    weights = np.log1p(
        popularity
    )

    route_type_multiplier = (
        routes["route_type"]
        .map(
            {
                "Commuter": 1.15,
                "Regional": 1.00,
                "Intercity": 1.20,
            }
        )
        .astype(float)
        .to_numpy(copy=True)
    )

    weights *= route_type_multiplier

    weights *= np.where(
        routes["active_flag"].to_numpy(copy=True),
        1.0,
        0.01,
    )

    weights /= weights.sum()

    return weights


# ============================================================
# DATE / SEASONAL WEIGHTS
# ============================================================

def create_date_weights(
    dates: pd.DataFrame,
) -> np.ndarray:

    month_multiplier = {
        1: 0.88,
        2: 0.91,
        3: 0.98,
        4: 1.02,
        5: 1.06,
        6: 1.10,
        7: 1.13,
        8: 1.09,
        9: 1.08,
        10: 1.03,
        11: 0.96,
        12: 1.08,
    }

    weights = (
        dates["month_number"]
        .map(month_multiplier)
        .astype(float)
        .to_numpy(copy=True)
    )

    weekday_factor = np.where(
        dates["day_of_week"]
        .to_numpy(copy=True)
        <= 5,
        1.05,
        0.88,
    )

    weights *= weekday_factor

    weights /= weights.sum()

    return weights


# ============================================================
# SEARCH HOUR PROFILE
# ============================================================

def create_hour_distribution():

    hours = np.arange(24)

    weights = np.array(
        [
            0.005,
            0.003,
            0.002,
            0.002,
            0.003,
            0.010,
            0.035,
            0.075,
            0.090,
            0.075,
            0.060,
            0.055,
            0.055,
            0.050,
            0.050,
            0.055,
            0.065,
            0.080,
            0.085,
            0.070,
            0.050,
            0.035,
            0.020,
            0.010,
        ],
        dtype=float,
    )

    weights /= weights.sum()

    return hours, weights


# ============================================================
# PASSENGER COUNT
# ============================================================

def generate_passenger_count(
    business_flags: np.ndarray,
) -> np.ndarray:

    n = len(business_flags)

    passenger_count = np.ones(
        n,
        dtype=np.int8,
    )

    leisure_mask = ~business_flags

    leisure_n = leisure_mask.sum()

    if leisure_n:

        passenger_count[
            leisure_mask
        ] = rng.choice(
            [1, 2, 3, 4],
            size=leisure_n,
            p=[
                0.70,
                0.21,
                0.065,
                0.025,
            ],
        )

    business_mask = business_flags

    business_n = business_mask.sum()

    if business_n:

        passenger_count[
            business_mask
        ] = rng.choice(
            [1, 2, 3],
            size=business_n,
            p=[
                0.91,
                0.075,
                0.015,
            ],
        )

    return passenger_count


# ============================================================
# TICKET SELECTION
# ============================================================

def generate_ticket_ids(
    business_flags: np.ndarray,
) -> np.ndarray:

    n = len(business_flags)

    ticket_ids = np.empty(
        n,
        dtype=object,
    )

    business_mask = business_flags

    leisure_mask = ~business_mask

    if business_mask.sum():

        ticket_ids[
            business_mask
        ] = rng.choice(
            [
                "T002",
                "T003",
                "T005",
                "T007",
                "T008",
            ],
            size=business_mask.sum(),
            p=[
                0.18,
                0.12,
                0.14,
                0.34,
                0.22,
            ],
        )

    if leisure_mask.sum():

        ticket_ids[
            leisure_mask
        ] = rng.choice(
            [
                "T001",
                "T002",
                "T003",
                "T004",
                "T006",
            ],
            size=leisure_mask.sum(),
            p=[
                0.31,
                0.10,
                0.27,
                0.18,
                0.14,
            ],
        )

    return ticket_ids


# ============================================================
# PAYMENT METHOD
# ============================================================

def generate_payment_method(
    b2b_flags: np.ndarray,
) -> np.ndarray:

    n = len(b2b_flags)

    methods = np.empty(
        n,
        dtype=object,
    )

    b2b_mask = b2b_flags

    direct_mask = ~b2b_mask

    if b2b_mask.sum():

        methods[
            b2b_mask
        ] = rng.choice(
            [
                "Corporate Account",
                "Payment Card",
                "Digital Wallet",
            ],
            size=b2b_mask.sum(),
            p=[
                0.66,
                0.29,
                0.05,
            ],
        )

    if direct_mask.sum():

        methods[
            direct_mask
        ] = rng.choice(
            [
                "Payment Card",
                "Digital Wallet",
                "Pay Later",
            ],
            size=direct_mask.sum(),
            p=[
                0.58,
                0.35,
                0.07,
            ],
        )

    return methods


# ============================================================
# MAIN TRANSACTION GENERATOR
# ============================================================

def generate_transactions():

    (
        customers,
        partners,
        routes,
        stations,
        tickets,
        dates,
    ) = load_dimensions()

    if TOTAL_BOOKINGS > TOTAL_SEARCHES:

        raise ValueError(
            "Bookings cannot exceed searches."
        )

    print("\nCreating sampling weights...")

    customer_weights = (
        create_customer_weights(
            customers
        )
    )

    partner_weights = (
        create_partner_weights(
            partners
        )
    )

    route_weights = (
        create_route_weights(
            routes,
            stations,
        )
    )

    date_weights = (
        create_date_weights(
            dates
        )
    )

    hours, hour_weights = (
        create_hour_distribution()
    )

    print("[OK] Sampling weights created")

    # --------------------------------------------------------
    # Dimension arrays
    # --------------------------------------------------------

    customer_ids = (
        customers["customer_id"]
        .to_numpy(copy=True)
    )

    customer_segments = (
        customers["customer_segment"]
        .to_numpy(copy=True)
    )

    customer_business = (
        customers["business_traveller_flag"]
        .to_numpy(dtype=bool)
    )

    customer_loyalty = (
        customers["loyalty_tier"]
        .to_numpy(copy=True)
    )

    preferred_device = (
        customers["preferred_device"]
        .to_numpy(copy=True)
    )

    partner_ids = (
        partners["partner_id"]
        .to_numpy(copy=True)
    )

    partner_commission_map = (
        partners
        .set_index("partner_id")
        ["commission_rate"]
        .to_dict()
    )

    route_ids = (
        routes["route_id"]
        .to_numpy(copy=True)
    )

    route_distance = (
        routes["distance_km"]
        .to_numpy(dtype=float)
    )

    route_types = (
        routes["route_type"]
        .to_numpy(copy=True)
    )

    date_values = (
        pd.to_datetime(
            dates["date"]
        )
        .to_numpy(copy=True)
    )

    # --------------------------------------------------------
    # Remove previous fact files
    # --------------------------------------------------------

    for path in [
        SEARCH_OUTPUT,
        BOOKING_OUTPUT,
        SEARCH_SAMPLE_OUTPUT,
        BOOKING_SAMPLE_OUTPUT,
        MANIFEST_OUTPUT,
    ]:

        if path.exists():
            path.unlink()

    search_writer = None
    booking_writer = None

    current_search_id = 1
    current_booking_id = 1

    generated_searches = 0
    generated_bookings = 0

    remaining_searches = TOTAL_SEARCHES
    remaining_bookings = TOTAL_BOOKINGS

    chunk_number = 0

    search_sample_saved = False
    booking_sample_saved = False

    print("\n" + "=" * 76)
    print("TRANSACTION GENERATION STARTED")
    print("=" * 76)

    try:

        while remaining_searches > 0:

            chunk_number += 1

            n = min(
                CHUNK_SIZE,
                remaining_searches,
            )

            if n == remaining_searches:

                target_bookings = (
                    remaining_bookings
                )

            else:

                target_bookings = int(
                    round(
                        n
                        * remaining_bookings
                        / remaining_searches
                    )
                )

            target_bookings = min(
                target_bookings,
                n,
            )

            # =================================================
            # SAMPLE CUSTOMERS
            # =================================================

            customer_index = rng.choice(
                len(customers),
                size=n,
                p=customer_weights,
            )

            chunk_customer_ids = (
                customer_ids[
                    customer_index
                ]
            )

            chunk_segments = (
                customer_segments[
                    customer_index
                ]
            )

            chunk_business = (
                customer_business[
                    customer_index
                ]
            )

            chunk_loyalty = (
                customer_loyalty[
                    customer_index
                ]
            )

            chunk_preferred_device = (
                preferred_device[
                    customer_index
                ]
            )

            # =================================================
            # SAMPLE ROUTES
            # =================================================

            route_index = rng.choice(
                len(routes),
                size=n,
                p=route_weights,
            )

            chunk_route_ids = (
                route_ids[
                    route_index
                ]
            )

            chunk_distances = (
                route_distance[
                    route_index
                ]
            )

            chunk_route_types = (
                route_types[
                    route_index
                ]
            )

            # =================================================
            # SEARCH DATES
            # =================================================

            date_index = rng.choice(
                len(dates),
                size=n,
                p=date_weights,
            )

            search_dates = pd.to_datetime(
                date_values[
                    date_index
                ]
            )

            search_hours = rng.choice(
                hours,
                size=n,
                p=hour_weights,
            )

            search_minutes = rng.integers(
                0,
                60,
                size=n,
            )

            search_seconds = rng.integers(
                0,
                60,
                size=n,
            )

            search_timestamp = (
                search_dates
                + pd.to_timedelta(
                    search_hours,
                    unit="h",
                )
                + pd.to_timedelta(
                    search_minutes,
                    unit="m",
                )
                + pd.to_timedelta(
                    search_seconds,
                    unit="s",
                )
            )

            # =================================================
            # B2B PARTNER ASSIGNMENT
            # =================================================

            b2b_probability = np.where(
                chunk_business,
                0.72,
                0.18,
            )

            is_b2b = (
                rng.random(n)
                < b2b_probability
            )

            chunk_partner_ids = np.empty(
                n,
                dtype=object,
            )

            chunk_partner_ids[:] = None

            b2b_count = is_b2b.sum()

            if b2b_count:

                chunk_partner_ids[
                    is_b2b
                ] = rng.choice(
                    partner_ids,
                    size=b2b_count,
                    p=partner_weights,
                )

            # =================================================
            # SALES CHANNEL
            # =================================================

            sales_channel = (
                chunk_preferred_device
                .astype(object)
                .copy()
            )

            sales_channel[
                is_b2b
            ] = "B2B Partner"

            # =================================================
            # BOOKING LEAD TIME
            # =================================================

            business_lead = rng.gamma(
                shape=1.7,
                scale=3.4,
                size=n,
            )

            leisure_lead = rng.gamma(
                shape=2.3,
                scale=5.5,
                size=n,
            )

            lead_days = np.where(
                chunk_business,
                business_lead,
                leisure_lead,
            )

            lead_days = np.clip(
                np.rint(lead_days),
                0,
                60,
            ).astype(np.int16)

            travel_dates = (
                search_dates
                + pd.to_timedelta(
                    lead_days,
                    unit="D",
                )
            )

            # =================================================
            # SEARCH FARES
            # =================================================

            fare_rate = np.select(
                [
                    chunk_route_types
                    == "Commuter",

                    chunk_route_types
                    == "Regional",

                    chunk_route_types
                    == "Intercity",
                ],
                [
                    0.16,
                    0.19,
                    0.23,
                ],
                default=0.18,
            )

            base_fare = (
                3.50
                + chunk_distances
                * fare_rate
            )

            lead_multiplier = np.select(
                [
                    lead_days >= 21,
                    lead_days >= 14,
                    lead_days <= 1,
                ],
                [
                    0.84,
                    0.91,
                    1.18,
                ],
                default=1.00,
            )

            fare_noise = rng.lognormal(
                mean=0.0,
                sigma=0.17,
                size=n,
            )

            lowest_fare = (
                base_fare
                * lead_multiplier
                * fare_noise
            )

            lowest_fare = np.clip(
                lowest_fare,
                4.50,
                350.00,
            )

            lowest_fare = np.round(
                lowest_fare,
                2,
            )

            # =================================================
            # AVAILABILITY
            # =================================================

            availability_flag = (
                rng.random(n)
                > 0.012
            )

            result_count = rng.poisson(
                lam=15,
                size=n,
            )

            result_count = np.clip(
                result_count,
                1,
                60,
            )

            result_count = np.where(
                availability_flag,
                result_count,
                0,
            ).astype(np.int16)

            displayed_fare = (
                lowest_fare.copy()
            )

            displayed_fare[
                ~availability_flag
            ] = np.nan

            # =================================================
            # SEARCH IDs
            # =================================================

            search_ids = np.arange(
                current_search_id,
                current_search_id + n,
                dtype=np.int64,
            )

            # =================================================
            # CONVERSION PROPENSITY
            # =================================================

            score = np.zeros(
                n,
                dtype=float,
            )

            score += np.where(
                is_b2b,
                0.72,
                0.0,
            )

            score += np.where(
                chunk_segments
                == "Frequent Business",
                0.58,
                0.0,
            )

            score += np.where(
                chunk_segments
                == "Leisure Frequent",
                0.31,
                0.0,
            )

            score += np.where(
                chunk_loyalty
                == "Gold",
                0.20,
                0.0,
            )

            score += np.where(
                chunk_loyalty
                == "Platinum",
                0.34,
                0.0,
            )

            score += np.where(
                sales_channel
                == "Mobile App",
                0.18,
                0.0,
            )

            score += np.where(
                lead_days <= 7,
                0.16,
                0.0,
            )

            score -= np.where(
                lowest_fare > 120,
                0.24,
                0.0,
            )

            score -= np.where(
                lowest_fare > 200,
                0.24,
                0.0,
            )

            score += rng.logistic(
                loc=0.0,
                scale=1.0,
                size=n,
            )

            score[
                ~availability_flag
            ] = -999.0

            # Exact number of conversions for this chunk

            converted_index = np.argpartition(
                score,
                -target_bookings,
            )[
                -target_bookings:
            ]

            converted_index = np.sort(
                converted_index
            )

            converted_flag = np.zeros(
                n,
                dtype=bool,
            )

            converted_flag[
                converted_index
            ] = True

            # =================================================
            # CREATE SEARCH FACT TABLE
            # =================================================

            search_df = pd.DataFrame(
                {
                    "search_id": search_ids,

                    "customer_id":
                        chunk_customer_ids,

                    "partner_id":
                        pd.array(
                            chunk_partner_ids,
                            dtype="string",
                        ),

                    "route_id":
                        chunk_route_ids,

                    "search_timestamp":
                        search_timestamp,

                    "search_date":
                        search_dates,

                    "travel_date":
                        travel_dates,

                    "booking_lead_days":
                        lead_days,

                    "sales_channel":
                        sales_channel,

                    "customer_segment":
                        chunk_segments,

                    "business_traveller_flag":
                        chunk_business,

                    "route_type":
                        chunk_route_types,

                    "distance_km":
                        np.round(
                            chunk_distances,
                            1,
                        ),

                    "result_count":
                        result_count,

                    "lowest_fare_gbp":
                        displayed_fare,

                    "availability_flag":
                        availability_flag,

                    "converted_flag":
                        converted_flag,
                }
            )

            # =================================================
            # CREATE BOOKINGS
            # =================================================

            idx = converted_index

            booking_n = len(idx)

            booking_ids = np.arange(
                current_booking_id,
                current_booking_id
                + booking_n,
                dtype=np.int64,
            )

            booked_business = (
                chunk_business[
                    idx
                ]
            )

            booked_b2b = (
                is_b2b[
                    idx
                ]
            )

            booked_partner_ids = (
                chunk_partner_ids[
                    idx
                ]
            )

            booked_loyalty = (
                chunk_loyalty[
                    idx
                ]
            )

            ticket_ids = (
                generate_ticket_ids(
                    booked_business
                )
            )

            passenger_count = (
                generate_passenger_count(
                    booked_business
                )
            )

            ticket_multiplier_map = {
                "T001": 1.00,
                "T002": 1.34,
                "T003": 1.10,
                "T004": 1.78,
                "T005": 2.18,
                "T006": 1.86,
                "T007": 1.52,
                "T008": 2.42,
            }

            ticket_multiplier = np.array(
                [
                    ticket_multiplier_map[
                        ticket
                    ]
                    for ticket in ticket_ids
                ],
                dtype=float,
            )

            booked_fare = (
                lowest_fare[
                    idx
                ]
                * ticket_multiplier
            )

            booked_fare *= rng.normal(
                loc=1.0,
                scale=0.025,
                size=booking_n,
            )

            booked_fare = np.clip(
                booked_fare,
                4.50,
                650.00,
            )

            booked_fare = np.round(
                booked_fare,
                2,
            )

            gross_booking_value = (
                booked_fare
                * passenger_count
            )

            loyalty_discount = np.select(
                [
                    booked_loyalty
                    == "Silver",

                    booked_loyalty
                    == "Gold",

                    booked_loyalty
                    == "Platinum",
                ],
                [
                    0.015,
                    0.030,
                    0.050,
                ],
                default=0.0,
            )

            b2b_discount = np.where(
                booked_b2b,
                0.020,
                0.0,
            )

            promo_flag = (
                rng.random(
                    booking_n
                )
                < 0.11
            )

            promo_discount = np.where(
                promo_flag,
                0.04,
                0.0,
            )

            discount_rate = (
                loyalty_discount
                + b2b_discount
                + promo_discount
            )

            discount_rate = np.clip(
                discount_rate,
                0.0,
                0.12,
            )

            discount_amount = (
                gross_booking_value
                * discount_rate
            )

            net_ticket_value = (
                gross_booking_value
                - discount_amount
            )

            commission_rate = np.array(
                [
                    (
                        partner_commission_map[
                            partner_id
                        ]
                        if partner_id is not None
                        else 0.060
                    )
                    for partner_id
                    in booked_partner_ids
                ],
                dtype=float,
            )

            service_fee = np.where(
                booked_b2b,
                rng.uniform(
                    0.25,
                    1.50,
                    booking_n,
                ),
                rng.uniform(
                    0.75,
                    2.75,
                    booking_n,
                ),
            )

            commission_revenue = (
                net_ticket_value
                * commission_rate
            )

            platform_revenue = (
                commission_revenue
                + service_fee
            )

            minutes_to_booking = np.clip(
                rng.exponential(
                    scale=17,
                    size=booking_n,
                ),
                1,
                180,
            ).astype(int)

            booking_timestamp = (
                search_timestamp[
                    idx
                ]
                + pd.to_timedelta(
                    minutes_to_booking,
                    unit="m",
                )
            )

            payment_method = (
                generate_payment_method(
                    booked_b2b
                )
            )

            booking_status = rng.choice(
                [
                    "Confirmed",
                    "Customer Cancelled",
                ],
                size=booking_n,
                p=[
                    0.973,
                    0.027,
                ],
            )

            booking_df = pd.DataFrame(
                {
                    "booking_id":
                        booking_ids,

                    "search_id":
                        search_ids[
                            idx
                        ],

                    "customer_id":
                        chunk_customer_ids[
                            idx
                        ],

                    "partner_id":
                        pd.array(
                            booked_partner_ids,
                            dtype="string",
                        ),

                    "route_id":
                        chunk_route_ids[
                            idx
                        ],

                    "ticket_id":
                        ticket_ids,

                    "booking_timestamp":
                        booking_timestamp,

                    "travel_date":
                        travel_dates[
                            idx
                        ],

                    "booking_lead_days":
                        lead_days[
                            idx
                        ],

                    "sales_channel":
                        sales_channel[
                            idx
                        ],

                    "business_traveller_flag":
                        booked_business,

                    "passenger_count":
                        passenger_count,

                    "booked_fare_gbp":
                        booked_fare,

                    "gross_booking_value_gbp":
                        np.round(
                            gross_booking_value,
                            2,
                        ),

                    "discount_rate":
                        np.round(
                            discount_rate,
                            4,
                        ),

                    "discount_amount_gbp":
                        np.round(
                            discount_amount,
                            2,
                        ),

                    "net_ticket_value_gbp":
                        np.round(
                            net_ticket_value,
                            2,
                        ),

                    "commission_rate":
                        np.round(
                            commission_rate,
                            4,
                        ),

                    "commission_revenue_gbp":
                        np.round(
                            commission_revenue,
                            2,
                        ),

                    "service_fee_gbp":
                        np.round(
                            service_fee,
                            2,
                        ),

                    "platform_revenue_gbp":
                        np.round(
                            platform_revenue,
                            2,
                        ),

                    "payment_method":
                        payment_method,

                    "promotion_used_flag":
                        promo_flag,

                    "booking_status":
                        booking_status,
                }
            )

            # =================================================
            # WRITE SEARCH PARQUET
            # =================================================

            search_table = (
                pa.Table.from_pandas(
                    search_df,
                    preserve_index=False,
                )
            )

            if search_writer is None:

                search_writer = (
                    pq.ParquetWriter(
                        SEARCH_OUTPUT,
                        search_table.schema,
                        compression="zstd",
                        use_dictionary=True,
                    )
                )

            search_writer.write_table(
                search_table
            )

            # =================================================
            # WRITE BOOKING PARQUET
            # =================================================

            booking_table = (
                pa.Table.from_pandas(
                    booking_df,
                    preserve_index=False,
                )
            )

            if booking_writer is None:

                booking_writer = (
                    pq.ParquetWriter(
                        BOOKING_OUTPUT,
                        booking_table.schema,
                        compression="zstd",
                        use_dictionary=True,
                    )
                )

            booking_writer.write_table(
                booking_table
            )

            # =================================================
            # SAVE SMALL CSV SAMPLES
            # =================================================

            if not search_sample_saved:

                search_df.head(
                    50_000
                ).to_csv(
                    SEARCH_SAMPLE_OUTPUT,
                    index=False,
                )

                search_sample_saved = True

            if not booking_sample_saved:

                booking_df.head(
                    25_000
                ).to_csv(
                    BOOKING_SAMPLE_OUTPUT,
                    index=False,
                )

                booking_sample_saved = True

            # =================================================
            # UPDATE COUNTERS
            # =================================================

            generated_searches += n
            generated_bookings += booking_n

            remaining_searches -= n
            remaining_bookings -= booking_n

            current_search_id += n
            current_booking_id += booking_n

            conversion = (
                generated_bookings
                / generated_searches
            )

            print(
                f"Chunk {chunk_number:02d} | "
                f"Searches: "
                f"{generated_searches:>9,}"
                f"/{TOTAL_SEARCHES:,} | "
                f"Bookings: "
                f"{generated_bookings:>9,}"
                f"/{TOTAL_BOOKINGS:,} | "
                f"Conversion: "
                f"{conversion:.2%}"
            )

            del (
                search_df,
                booking_df,
                search_table,
                booking_table,
            )

            gc.collect()

    finally:

        if search_writer is not None:
            search_writer.close()

        if booking_writer is not None:
            booking_writer.close()

    # ========================================================
    # FINAL ASSERTIONS
    # ========================================================

    assert (
        generated_searches
        == TOTAL_SEARCHES
    )

    assert (
        generated_bookings
        == TOTAL_BOOKINGS
    )

    # ========================================================
    # PARQUET METADATA
    # ========================================================

    search_meta = (
        pq.ParquetFile(
            SEARCH_OUTPUT
        )
    )

    booking_meta = (
        pq.ParquetFile(
            BOOKING_OUTPUT
        )
    )

    search_rows = (
        search_meta
        .metadata
        .num_rows
    )

    booking_rows = (
        booking_meta
        .metadata
        .num_rows
    )

    if search_rows != TOTAL_SEARCHES:

        raise ValueError(
            "Search parquet row count "
            "does not match target."
        )

    if booking_rows != TOTAL_BOOKINGS:

        raise ValueError(
            "Booking parquet row count "
            "does not match target."
        )

    conversion_rate = (
        booking_rows
        / search_rows
    )

    manifest = {

        "fact_searches": {
            "rows": int(
                search_rows
            ),

            "columns": int(
                len(
                    search_meta.schema.names
                )
            ),

            "file":
                SEARCH_OUTPUT.name,

            "size_mb":
                round(
                    SEARCH_OUTPUT
                    .stat()
                    .st_size
                    / 1024
                    / 1024,
                    2,
                ),
        },

        "fact_bookings": {
            "rows": int(
                booking_rows
            ),

            "columns": int(
                len(
                    booking_meta.schema.names
                )
            ),

            "file":
                BOOKING_OUTPUT.name,

            "size_mb":
                round(
                    BOOKING_OUTPUT
                    .stat()
                    .st_size
                    / 1024
                    / 1024,
                    2,
                ),
        },

        "overall_conversion_rate":
            round(
                conversion_rate,
                6,
            ),

        "random_seed":
            SEED,

        "chunk_size":
            CHUNK_SIZE,

        "data_classification":
            "Synthetic portfolio data",
    }

    with open(
        MANIFEST_OUTPUT,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            manifest,
            file,
            indent=4,
        )

    print("\n" + "=" * 76)
    print("TRANSACTION GENERATION COMPLETE")
    print("=" * 76)

    print(
        f"\nSearch rows:  "
        f"{search_rows:,}"
    )

    print(
        f"Booking rows: "
        f"{booking_rows:,}"
    )

    print(
        f"Conversion:   "
        f"{conversion_rate:.2%}"
    )

    print(
        f"\nSearch parquet:  "
        f"{SEARCH_OUTPUT}"
    )

    print(
        f"Booking parquet: "
        f"{BOOKING_OUTPUT}"
    )


if __name__ == "__main__":

    generate_transactions()
