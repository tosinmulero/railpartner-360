from __future__ import annotations

from pathlib import Path
import gc
import json

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import yaml


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_PATH = PROJECT_ROOT / "config.yaml"

DATA_DIR = PROJECT_ROOT / "data" / "synthetic"

BOOKING_FILE = DATA_DIR / "fact_bookings.parquet"

ROUTE_FILE = DATA_DIR / "dim_route.parquet"

TICKET_FILE = DATA_DIR / "dim_ticket.parquet"

OPERATOR_FILE = DATA_DIR / "dim_operator.parquet"

JOURNEY_OUTPUT = DATA_DIR / "fact_journeys.parquet"

REFUND_OUTPUT = DATA_DIR / "fact_refunds.parquet"

JOURNEY_SAMPLE = DATA_DIR / "fact_journeys_sample.csv"

REFUND_SAMPLE = DATA_DIR / "fact_refunds_sample.csv"

MANIFEST_OUTPUT = DATA_DIR / "operations_manifest.json"


# ============================================================
# CONFIGURATION
# ============================================================

with open(
    CONFIG_PATH,
    "r",
    encoding="utf-8",
) as file:
    CONFIG = yaml.safe_load(file)


BASE_SEED = int(
    CONFIG["data_generation"]["random_seed"]
)

RNG_SEED = BASE_SEED + 2000

rng = np.random.default_rng(
    RNG_SEED
)

BATCH_SIZE = 200_000


# ============================================================
# LOAD DIMENSION LOOKUPS
# ============================================================

def load_lookups():

    print("\nLoading operational lookups...")

    routes = pd.read_parquet(
        ROUTE_FILE
    )

    tickets = pd.read_parquet(
        TICKET_FILE
    )

    operators = pd.read_parquet(
        OPERATOR_FILE
    )

    route_lookup = (
        routes
        .set_index("route_id")
        [
            [
                "primary_operator_id",
                "planned_duration_minutes",
                "route_type",
                "distance_km",
            ]
        ]
    )

    ticket_lookup = (
        tickets
        .set_index("ticket_id")
        [
            [
                "refundable_flag",
                "changeable_flag",
                "fare_category",
            ]
        ]
    )

    operator_ids = set(
        operators["operator_id"]
    )

    print(
        f"[OK] Routes:    {len(routes):,}"
    )

    print(
        f"[OK] Tickets:   {len(tickets):,}"
    )

    print(
        f"[OK] Operators: {len(operators):,}"
    )

    return (
        route_lookup,
        ticket_lookup,
        operator_ids,
    )


# ============================================================
# SERVICE TIME PROFILE
# ============================================================

def generate_departure_times(n: int):

    hours = np.arange(
        5,
        24,
    )

    weights = np.array(
        [
            0.025,  # 05
            0.050,  # 06
            0.090,  # 07
            0.105,  # 08
            0.085,  # 09
            0.055,  # 10
            0.045,  # 11
            0.050,  # 12
            0.050,  # 13
            0.050,  # 14
            0.055,  # 15
            0.070,  # 16
            0.090,  # 17
            0.090,  # 18
            0.070,  # 19
            0.055,  # 20
            0.035,  # 21
            0.020,  # 22
            0.010,  # 23
        ],
        dtype=float,
    )

    weights = (
        weights
        / weights.sum()
    )

    departure_hours = rng.choice(
        hours,
        size=n,
        p=weights,
    )

    departure_minutes = rng.choice(
        [
            0,
            5,
            10,
            15,
            20,
            25,
            30,
            35,
            40,
            45,
            50,
            55,
        ],
        size=n,
    )

    return (
        departure_hours,
        departure_minutes,
    )


# ============================================================
# DELAY GENERATION
# ============================================================

def generate_delay_minutes(n: int):

    u = rng.random(n)

    delay = np.zeros(
        n,
        dtype=np.int16,
    )

    mask = u < 0.85

    delay[mask] = rng.integers(
        0,
        4,
        mask.sum(),
    )

    mask = (
        (u >= 0.85)
        & (u < 0.92)
    )

    delay[mask] = rng.integers(
        4,
        6,
        mask.sum(),
    )

    mask = (
        (u >= 0.92)
        & (u < 0.96)
    )

    delay[mask] = rng.integers(
        6,
        15,
        mask.sum(),
    )

    mask = (
        (u >= 0.96)
        & (u < 0.985)
    )

    delay[mask] = rng.integers(
        15,
        30,
        mask.sum(),
    )

    mask = (
        (u >= 0.985)
        & (u < 0.995)
    )

    delay[mask] = rng.integers(
        30,
        60,
        mask.sum(),
    )

    mask = u >= 0.995

    delay[mask] = rng.integers(
        60,
        181,
        mask.sum(),
    )

    return delay


# ============================================================
# DELAY BAND
# ============================================================

def create_delay_band(
    delay_minutes: np.ndarray,
    completed_mask: np.ndarray,
):

    bands = np.full(
        len(delay_minutes),
        "Not Applicable",
        dtype=object,
    )

    bands[
        completed_mask
        & (delay_minutes <= 3)
    ] = "0-3 min"

    bands[
        completed_mask
        & (delay_minutes >= 4)
        & (delay_minutes <= 5)
    ] = "4-5 min"

    bands[
        completed_mask
        & (delay_minutes >= 6)
        & (delay_minutes <= 14)
    ] = "6-14 min"

    bands[
        completed_mask
        & (delay_minutes >= 15)
        & (delay_minutes <= 29)
    ] = "15-29 min"

    bands[
        completed_mask
        & (delay_minutes >= 30)
        & (delay_minutes <= 59)
    ] = "30-59 min"

    bands[
        completed_mask
        & (delay_minutes >= 60)
    ] = "60+ min"

    return bands


# ============================================================
# DISRUPTION REASONS
# ============================================================

def generate_disruption_reasons(
    operator_cancelled: np.ndarray,
    delayed: np.ndarray,
):

    n = len(
        operator_cancelled
    )

    reasons = np.empty(
        n,
        dtype=object,
    )

    reasons[:] = None

    disruption_mask = (
        operator_cancelled
        | delayed
    )

    disruption_n = (
        disruption_mask.sum()
    )

    if disruption_n:

        reasons[
            disruption_mask
        ] = rng.choice(
            [
                "Infrastructure issue",
                "Train fault",
                "Crew availability",
                "Signal failure",
                "Network congestion",
                "Weather conditions",
                "Earlier service disruption",
                "Operational incident",
            ],
            size=disruption_n,
            p=[
                0.19,
                0.17,
                0.15,
                0.14,
                0.13,
                0.08,
                0.08,
                0.06,
            ],
        )

    return reasons


# ============================================================
# REFUND / COMPENSATION GENERATOR
# ============================================================

def generate_refund_rows(
    journey_df: pd.DataFrame,
    booking_df: pd.DataFrame,
    refundable_flags: np.ndarray,
    refund_id_start: int,
):

    journey_status = (
        journey_df["journey_status"]
        .to_numpy(copy=True)
    )

    delay_minutes = (
        journey_df[
            "arrival_delay_minutes"
        ]
        .fillna(-1)
        .to_numpy(copy=True)
    )

    operator_cancelled = (
        journey_status
        == "Operator Cancelled"
    )

    customer_cancelled = (
        journey_status
        == "Customer Cancelled"
    )

    completed = (
        journey_status
        == "Completed"
    )

    customer_refundable = (
        customer_cancelled
        & refundable_flags
    )

    delay_compensation = (
        completed
        & (delay_minutes >= 15)
    )

    eligible = (
        operator_cancelled
        | customer_refundable
        | delay_compensation
    )

    idx = np.flatnonzero(
        eligible
    )

    if len(idx) == 0:

        return (
            pd.DataFrame(),
            refund_id_start,
        )

    n = len(idx)

    refund_type = np.empty(
        n,
        dtype=object,
    )

    refund_reason = np.empty(
        n,
        dtype=object,
    )

    refund_rate = np.zeros(
        n,
        dtype=float,
    )

    selected_status = (
        journey_status[idx]
    )

    selected_delay = (
        delay_minutes[idx]
    )

    op_mask = (
        selected_status
        == "Operator Cancelled"
    )

    cust_mask = (
        selected_status
        == "Customer Cancelled"
    )

    delay_mask = (
        selected_status
        == "Completed"
    )

    # --------------------------------------------------------
    # Operator cancellations
    # --------------------------------------------------------

    refund_type[
        op_mask
    ] = "Full Refund"

    refund_reason[
        op_mask
    ] = "Operator Cancellation"

    refund_rate[
        op_mask
    ] = 1.00

    # --------------------------------------------------------
    # Customer cancellations
    # --------------------------------------------------------

    refund_type[
        cust_mask
    ] = "Customer Refund"

    refund_reason[
        cust_mask
    ] = "Customer Cancellation"

    if cust_mask.sum():

        refund_rate[
            cust_mask
        ] = rng.uniform(
            0.70,
            0.95,
            cust_mask.sum(),
        )

    # --------------------------------------------------------
    # Delay compensation
    # --------------------------------------------------------

    refund_type[
        delay_mask
    ] = "Delay Compensation"

    refund_reason[
        delay_mask
    ] = "Journey Delay"

    delay_values = (
        selected_delay[
            delay_mask
        ]
    )

    rates = np.select(
        [
            delay_values >= 60,
            delay_values >= 30,
            delay_values >= 15,
        ],
        [
            1.00,
            0.50,
            0.25,
        ],
        default=0.0,
    )

    refund_rate[
        delay_mask
    ] = rates

    # --------------------------------------------------------
    # Monetary values
    # --------------------------------------------------------

    net_ticket_value = (
        booking_df[
            "net_ticket_value_gbp"
        ]
        .to_numpy(copy=True)[idx]
    )

    platform_revenue = (
        booking_df[
            "platform_revenue_gbp"
        ]
        .to_numpy(copy=True)[idx]
    )

    eligible_value = (
        net_ticket_value
    )

    calculated_amount = (
        eligible_value
        * refund_rate
    )

    # --------------------------------------------------------
    # Refund workflow status
    # --------------------------------------------------------

    refund_status = rng.choice(
        [
            "Paid",
            "Pending",
            "Rejected",
        ],
        size=n,
        p=[
            0.94,
            0.045,
            0.015,
        ],
    )

    refund_amount = (
        calculated_amount.copy()
    )

    refund_amount[
        refund_status
        == "Rejected"
    ] = 0.0

    # --------------------------------------------------------
    # Event timestamps
    # --------------------------------------------------------

    booking_timestamp = pd.to_datetime(
        booking_df[
            "booking_timestamp"
        ]
        .iloc[idx]
        .reset_index(drop=True)
    )

    scheduled_departure = pd.to_datetime(
        journey_df[
            "scheduled_departure"
        ]
        .iloc[idx]
        .reset_index(drop=True)
    )

    event_timestamp = (
        scheduled_departure.copy()
    )

    cust_positions = np.flatnonzero(
        cust_mask
    )

    if len(
        cust_positions
    ):

        cancellation_offset = (
            rng.integers(
                1,
                72,
                size=len(
                    cust_positions
                ),
            )
        )

        event_timestamp.iloc[
            cust_positions
        ] = (
            booking_timestamp.iloc[
                cust_positions
            ]
            + pd.to_timedelta(
                cancellation_offset,
                unit="h",
            )
        )

    request_delay_days = (
        rng.integers(
            0,
            4,
            size=n,
        )
    )

    request_timestamp = (
        event_timestamp
        + pd.to_timedelta(
            request_delay_days,
            unit="D",
        )
    )

    processing_days = (
        rng.integers(
            0,
            11,
            size=n,
        )
    )

    processed_timestamp = (
        request_timestamp
        + pd.to_timedelta(
            processing_days,
            unit="D",
        )
    )

    processed_timestamp = pd.Series(
        processed_timestamp
    )

    processed_timestamp[
        refund_status
        == "Pending"
    ] = pd.NaT

    # --------------------------------------------------------
    # Commercial value at risk
    # --------------------------------------------------------

    cancellation_mask = (
        op_mask
        | cust_mask
    )

    commercial_value_at_risk = (
        refund_amount.copy()
    )

    commercial_value_at_risk[
        cancellation_mask
    ] += (
        platform_revenue[
            cancellation_mask
        ]
    )

    # --------------------------------------------------------
    # Refund IDs
    # --------------------------------------------------------

    refund_ids = np.arange(
        refund_id_start,
        refund_id_start + n,
        dtype=np.int64,
    )

    refund_df = pd.DataFrame(
        {
            "refund_id":
                refund_ids,

            "booking_id":
                booking_df[
                    "booking_id"
                ]
                .to_numpy(copy=True)[idx],

            "journey_id":
                journey_df[
                    "journey_id"
                ]
                .to_numpy(copy=True)[idx],

            "customer_id":
                booking_df[
                    "customer_id"
                ]
                .to_numpy(copy=True)[idx],

            "partner_id":
                booking_df[
                    "partner_id"
                ]
                .iloc[idx]
                .reset_index(drop=True),

            "refund_type":
                refund_type,

            "refund_reason":
                refund_reason,

            "refund_status":
                refund_status,

            "refund_request_timestamp":
                request_timestamp,

            "refund_processed_timestamp":
                processed_timestamp,

            "eligible_value_gbp":
                np.round(
                    eligible_value,
                    2,
                ),

            "refund_rate":
                np.round(
                    refund_rate,
                    4,
                ),

            "refund_amount_gbp":
                np.round(
                    refund_amount,
                    2,
                ),

            "commercial_value_at_risk_gbp":
                np.round(
                    commercial_value_at_risk,
                    2,
                ),

            "processing_days":
                processing_days,

            "business_traveller_flag":
                booking_df[
                    "business_traveller_flag"
                ]
                .to_numpy(copy=True)[idx],

            "sales_channel":
                booking_df[
                    "sales_channel"
                ]
                .to_numpy(copy=True)[idx],
        }
    )

    return (
        refund_df,
        refund_id_start + n,
    )


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    (
        route_lookup,
        ticket_lookup,
        operator_ids,
    ) = load_lookups()

    booking_parquet = pq.ParquetFile(
        BOOKING_FILE
    )

    total_bookings = (
        booking_parquet
        .metadata
        .num_rows
    )

    print(
        f"\nBooking records available: "
        f"{total_bookings:,}"
    )

    # Remove previous outputs if rerunning

    for path in [
        JOURNEY_OUTPUT,
        REFUND_OUTPUT,
        JOURNEY_SAMPLE,
        REFUND_SAMPLE,
        MANIFEST_OUTPUT,
    ]:

        if path.exists():
            path.unlink()

    journey_writer = None
    refund_writer = None

    journey_id_start = 1
    refund_id_start = 1

    total_journeys = 0
    total_refunds = 0

    journey_sample_saved = False
    refund_sample_saved = False

    batch_number = 0

    print(
        "\n"
        + "=" * 76
    )

    print(
        "OPERATIONAL DATA GENERATION STARTED"
    )

    print(
        "=" * 76
    )

    try:

        for batch in (
            booking_parquet
            .iter_batches(
                batch_size=BATCH_SIZE
            )
        ):

            batch_number += 1

            booking_df = (
                batch
                .to_pandas()
                .reset_index(
                    drop=True
                )
            )

            n = len(
                booking_df
            )

            # =================================================
            # ROUTE ATTRIBUTES
            # =================================================

            route_ids = (
                booking_df[
                    "route_id"
                ]
                .to_numpy(
                    copy=True
                )
            )

            operator_id = (
                booking_df[
                    "route_id"
                ]
                .map(
                    route_lookup[
                        "primary_operator_id"
                    ]
                )
                .to_numpy(
                    copy=True
                )
            )

            duration_minutes = (
                booking_df[
                    "route_id"
                ]
                .map(
                    route_lookup[
                        "planned_duration_minutes"
                    ]
                )
                .to_numpy(
                    copy=True
                )
                .astype(
                    np.int16
                )
            )

            route_type = (
                booking_df[
                    "route_id"
                ]
                .map(
                    route_lookup[
                        "route_type"
                    ]
                )
                .to_numpy(
                    copy=True
                )
            )

            distance_km = (
                booking_df[
                    "route_id"
                ]
                .map(
                    route_lookup[
                        "distance_km"
                    ]
                )
                .to_numpy(
                    copy=True
                )
                .astype(
                    float
                )
            )

            if pd.isna(
                operator_id
            ).any():

                raise ValueError(
                    "Missing operator mapping."
                )

            # =================================================
            # TICKET ATTRIBUTES
            # =================================================

            refundable_flags = (
                booking_df[
                    "ticket_id"
                ]
                .map(
                    ticket_lookup[
                        "refundable_flag"
                    ]
                )
                .fillna(
                    False
                )
                .to_numpy(
                    copy=True
                )
                .astype(
                    bool
                )
            )

            # =================================================
            # SCHEDULED TIMES
            # =================================================

            travel_date = pd.to_datetime(
                booking_df[
                    "travel_date"
                ]
            )

            (
                departure_hours,
                departure_minutes,
            ) = generate_departure_times(
                n
            )

            scheduled_departure = (
                travel_date
                + pd.to_timedelta(
                    departure_hours,
                    unit="h",
                )
                + pd.to_timedelta(
                    departure_minutes,
                    unit="m",
                )
            )

            scheduled_arrival = (
                scheduled_departure
                + pd.to_timedelta(
                    duration_minutes,
                    unit="m",
                )
            )

            # =================================================
            # JOURNEY STATUS
            # =================================================

            booking_status = (
                booking_df[
                    "booking_status"
                ]
                .to_numpy(
                    copy=True
                )
            )

            customer_cancelled = (
                booking_status
                == "Customer Cancelled"
            )

            weekend = (
                travel_date
                .dt.dayofweek
                .to_numpy()
                >= 5
            )

            cancellation_probability = (
                np.full(
                    n,
                    0.036,
                    dtype=float,
                )
            )

            cancellation_probability += np.where(
                route_type
                == "Regional",
                0.004,
                0.0,
            )

            cancellation_probability += np.where(
                route_type
                == "Intercity",
                -0.003,
                0.0,
            )

            cancellation_probability += np.where(
                weekend,
                0.003,
                0.0,
            )

            cancellation_probability = np.clip(
                cancellation_probability,
                0.020,
                0.060,
            )

            operator_cancelled = (
                (
                    rng.random(
                        n
                    )
                    < cancellation_probability
                )
                & ~customer_cancelled
            )

            completed = (
                ~customer_cancelled
                & ~operator_cancelled
            )

            journey_status = np.full(
                n,
                "Completed",
                dtype=object,
            )

            journey_status[
                customer_cancelled
            ] = "Customer Cancelled"

            journey_status[
                operator_cancelled
            ] = "Operator Cancelled"

            # =================================================
            # DELAYS
            # =================================================

            arrival_delay = (
                generate_delay_minutes(
                    n
                )
            )

            departure_delay = np.maximum(
                0,
                arrival_delay
                + rng.integers(
                    -4,
                    5,
                    size=n,
                ),
            ).astype(
                np.int16
            )

            arrival_delay[
                ~completed
            ] = 0

            departure_delay[
                ~completed
            ] = 0

            actual_departure = (
                scheduled_departure
                + pd.to_timedelta(
                    departure_delay,
                    unit="m",
                )
            )

            actual_arrival = (
                scheduled_arrival
                + pd.to_timedelta(
                    arrival_delay,
                    unit="m",
                )
            )

            actual_departure = pd.Series(
                actual_departure
            )

            actual_arrival = pd.Series(
                actual_arrival
            )

            actual_departure[
                ~completed
            ] = pd.NaT

            actual_arrival[
                ~completed
            ] = pd.NaT

            # Nullable delays

            departure_delay_series = pd.Series(
                departure_delay,
                dtype="Int16",
            )

            arrival_delay_series = pd.Series(
                arrival_delay,
                dtype="Int16",
            )

            departure_delay_series[
                ~completed
            ] = pd.NA

            arrival_delay_series[
                ~completed
            ] = pd.NA

            # =================================================
            # SERVICE PERFORMANCE
            # =================================================

            delayed_6_plus = (
                completed
                & (
                    arrival_delay
                    >= 6
                )
            )

            disruption_reason = (
                generate_disruption_reasons(
                    operator_cancelled,
                    delayed_6_plus,
                )
            )

            delay_band = (
                create_delay_band(
                    arrival_delay,
                    completed,
                )
            )

            within_3_minutes = (
                completed
                & (
                    arrival_delay
                    <= 3
                )
            )

            within_15_minutes = (
                completed
                & (
                    arrival_delay
                    < 15
                )
            )

            severe_delay = (
                completed
                & (
                    arrival_delay
                    >= 30
                )
            )

            compensation_eligible = (
                operator_cancelled
                | (
                    completed
                    & (
                        arrival_delay
                        >= 15
                    )
                )
            )

            operational_disruption = (
                operator_cancelled
                | delayed_6_plus
            )

            # =================================================
            # JOURNEY FACT
            # =================================================

            journey_ids = np.arange(
                journey_id_start,
                journey_id_start + n,
                dtype=np.int64,
            )

            journey_df = pd.DataFrame(
                {
                    "journey_id":
                        journey_ids,

                    "booking_id":
                        booking_df[
                            "booking_id"
                        ]
                        .to_numpy(
                            copy=True
                        ),

                    "customer_id":
                        booking_df[
                            "customer_id"
                        ]
                        .to_numpy(
                            copy=True
                        ),

                    "partner_id":
                        booking_df[
                            "partner_id"
                        ],

                    "route_id":
                        route_ids,

                    "operator_id":
                        operator_id,

                    "ticket_id":
                        booking_df[
                            "ticket_id"
                        ]
                        .to_numpy(
                            copy=True
                        ),

                    "travel_date":
                        travel_date,

                    "scheduled_departure":
                        scheduled_departure,

                    "scheduled_arrival":
                        scheduled_arrival,

                    "actual_departure":
                        actual_departure,

                    "actual_arrival":
                        actual_arrival,

                    "planned_duration_minutes":
                        duration_minutes,

                    "distance_km":
                        np.round(
                            distance_km,
                            1,
                        ),

                    "route_type":
                        route_type,

                    "journey_status":
                        journey_status,

                    "departure_delay_minutes":
                        departure_delay_series,

                    "arrival_delay_minutes":
                        arrival_delay_series,

                    "delay_band":
                        delay_band,

                    "within_3_minutes_flag":
                        within_3_minutes,

                    "within_15_minutes_flag":
                        within_15_minutes,

                    "severe_delay_flag":
                        severe_delay,

                    "operational_disruption_flag":
                        operational_disruption,

                    "disruption_reason":
                        disruption_reason,

                    "compensation_eligible_flag":
                        compensation_eligible,

                    "business_traveller_flag":
                        booking_df[
                            "business_traveller_flag"
                        ]
                        .to_numpy(
                            copy=True
                        ),

                    "sales_channel":
                        booking_df[
                            "sales_channel"
                        ]
                        .to_numpy(
                            copy=True
                        ),
                }
            )

            # =================================================
            # REFUNDS
            # =================================================

            (
                refund_df,
                next_refund_id,
            ) = generate_refund_rows(
                journey_df,
                booking_df,
                refundable_flags,
                refund_id_start,
            )

            # =================================================
            # WRITE JOURNEYS
            # =================================================

            journey_table = (
                pa.Table.from_pandas(
                    journey_df,
                    preserve_index=False,
                )
            )

            if journey_writer is None:

                journey_writer = (
                    pq.ParquetWriter(
                        JOURNEY_OUTPUT,
                        journey_table.schema,
                        compression="zstd",
                        use_dictionary=True,
                    )
                )

            journey_writer.write_table(
                journey_table
            )

            # =================================================
            # WRITE REFUNDS
            # =================================================

            if not refund_df.empty:

                refund_table = (
                    pa.Table.from_pandas(
                        refund_df,
                        preserve_index=False,
                    )
                )

                if refund_writer is None:

                    refund_writer = (
                        pq.ParquetWriter(
                            REFUND_OUTPUT,
                            refund_table.schema,
                            compression="zstd",
                            use_dictionary=True,
                        )
                    )

                refund_writer.write_table(
                    refund_table
                )

                if not refund_sample_saved:

                    refund_df.head(
                        25_000
                    ).to_csv(
                        REFUND_SAMPLE,
                        index=False,
                    )

                    refund_sample_saved = True

                total_refunds += len(
                    refund_df
                )

                refund_id_start = (
                    next_refund_id
                )

            # =================================================
            # SAMPLE JOURNEYS
            # =================================================

            if not journey_sample_saved:

                journey_df.head(
                    50_000
                ).to_csv(
                    JOURNEY_SAMPLE,
                    index=False,
                )

                journey_sample_saved = True

            # =================================================
            # COUNTERS
            # =================================================

            total_journeys += n

            journey_id_start += n

            completed_count = int(
                completed.sum()
            )

            operator_cancel_count = int(
                operator_cancelled.sum()
            )

            customer_cancel_count = int(
                customer_cancelled.sum()
            )

            disruption_count = int(
                operational_disruption.sum()
            )

            print(
                f"Batch {batch_number:02d} | "
                f"Journeys: "
                f"{total_journeys:>9,}"
                f"/{total_bookings:,} | "
                f"Refunds: "
                f"{total_refunds:>8,} | "
                f"Completed: "
                f"{completed_count:>7,} | "
                f"Operator cancelled: "
                f"{operator_cancel_count:>6,} | "
                f"Disrupted: "
                f"{disruption_count:>6,}"
            )

            del (
                booking_df,
                journey_df,
                journey_table,
                refund_df,
            )

            gc.collect()

    finally:

        if journey_writer is not None:
            journey_writer.close()

        if refund_writer is not None:
            refund_writer.close()

    # ========================================================
    # FINAL METADATA
    # ========================================================

    journey_file = pq.ParquetFile(
        JOURNEY_OUTPUT
    )

    journey_rows = (
        journey_file
        .metadata
        .num_rows
    )

    if journey_rows != total_bookings:

        raise ValueError(
            "Journey row count does not match "
            "booking row count."
        )

    if REFUND_OUTPUT.exists():

        refund_file = pq.ParquetFile(
            REFUND_OUTPUT
        )

        refund_rows = (
            refund_file
            .metadata
            .num_rows
        )

    else:

        refund_rows = 0

    manifest = {

        "fact_journeys": {

            "rows":
                int(
                    journey_rows
                ),

            "columns":
                int(
                    len(
                        journey_file
                        .schema
                        .names
                    )
                ),

            "size_mb":
                round(
                    JOURNEY_OUTPUT
                    .stat()
                    .st_size
                    / 1024
                    / 1024,
                    2,
                ),
        },

        "fact_refunds": {

            "rows":
                int(
                    refund_rows
                ),

            "size_mb":
                round(
                    REFUND_OUTPUT
                    .stat()
                    .st_size
                    / 1024
                    / 1024,
                    2,
                )
                if REFUND_OUTPUT.exists()
                else 0,
        },

        "random_seed":
            RNG_SEED,

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

    print(
        "\n"
        + "=" * 76
    )

    print(
        "OPERATIONAL DATA GENERATION COMPLETE"
    )

    print(
        "=" * 76
    )

    print(
        f"\nJourney rows: "
        f"{journey_rows:,}"
    )

    print(
        f"Refund rows:  "
        f"{refund_rows:,}"
    )

    print(
        f"\nJourney file:\n"
        f"{JOURNEY_OUTPUT}"
    )

    print(
        f"\nRefund file:\n"
        f"{REFUND_OUTPUT}"
    )


if __name__ == "__main__":

    main()
