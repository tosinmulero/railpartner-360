from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
)

CONFIG_PATH = (
    PROJECT_ROOT
    / "config.yaml"
)


def load_config():

    with open(
        CONFIG_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        return yaml.safe_load(file)


def validate_sequential_ids(
    parquet_path: Path,
    column_name: str,
    expected_rows: int,
):

    parquet_file = pq.ParquetFile(
        parquet_path
    )

    expected_id = 1
    total = 0

    for batch in parquet_file.iter_batches(
        columns=[
            column_name
        ],
        batch_size=250_000,
    ):

        ids = (
            batch
            .column(0)
            .to_numpy()
        )

        expected = np.arange(
            expected_id,
            expected_id + len(ids),
            dtype=np.int64,
        )

        if not np.array_equal(
            ids,
            expected,
        ):

            raise ValueError(
                f"{column_name} "
                "is not sequential "
                "or contains duplicates."
            )

        total += len(ids)
        expected_id += len(ids)

    if total != expected_rows:

        raise ValueError(
            f"{column_name} row count "
            "validation failed."
        )

    print(
        f"[OK] {column_name}: "
        f"{total:,} sequential IDs"
    )


def validate_booking_search_ids(
    booking_path: Path,
    max_search_id: int,
):

    parquet_file = pq.ParquetFile(
        booking_path
    )

    previous_max = 0
    total = 0

    for batch in parquet_file.iter_batches(
        columns=[
            "search_id"
        ],
        batch_size=250_000,
    ):

        ids = (
            batch
            .column(0)
            .to_numpy()
        )

        if ids.min() < 1:

            raise ValueError(
                "Invalid search_id "
                "in fact_bookings."
            )

        if ids.max() > max_search_id:

            raise ValueError(
                "Booking references "
                "search_id outside "
                "fact_searches."
            )

        if len(ids) > 1:

            if np.any(
                np.diff(ids) <= 0
            ):

                raise ValueError(
                    "Duplicate or "
                    "unordered booking "
                    "search_id detected."
                )

        if previous_max:

            if ids[0] <= previous_max:

                raise ValueError(
                    "Duplicate booking "
                    "search_id across "
                    "parquet batches."
                )

        previous_max = ids[-1]

        total += len(ids)

    print(
        f"[OK] Booking → Search FK: "
        f"{total:,} records"
    )


def validate_sample_foreign_keys():

    customers = set(
        pd.read_parquet(
            DATA_DIR
            / "dim_customer.parquet",
            columns=[
                "customer_id"
            ],
        )[
            "customer_id"
        ]
    )

    routes = set(
        pd.read_parquet(
            DATA_DIR
            / "dim_route.parquet",
            columns=[
                "route_id"
            ],
        )[
            "route_id"
        ]
    )

    partners = set(
        pd.read_parquet(
            DATA_DIR
            / "dim_partner.parquet",
            columns=[
                "partner_id"
            ],
        )[
            "partner_id"
        ]
    )

    tickets = set(
        pd.read_parquet(
            DATA_DIR
            / "dim_ticket.parquet",
            columns=[
                "ticket_id"
            ],
        )[
            "ticket_id"
        ]
    )

    search_sample = pd.read_csv(
        DATA_DIR
        / "fact_searches_sample.csv"
    )

    booking_sample = pd.read_csv(
        DATA_DIR
        / "fact_bookings_sample.csv"
    )

    if not set(
        search_sample[
            "customer_id"
        ]
    ).issubset(
        customers
    ):

        raise ValueError(
            "Invalid customer FK "
            "in searches."
        )

    if not set(
        search_sample[
            "route_id"
        ]
    ).issubset(
        routes
    ):

        raise ValueError(
            "Invalid route FK "
            "in searches."
        )

    search_partners = set(
        search_sample[
            "partner_id"
        ]
        .dropna()
    )

    if not search_partners.issubset(
        partners
    ):

        raise ValueError(
            "Invalid partner FK "
            "in searches."
        )

    if not set(
        booking_sample[
            "customer_id"
        ]
    ).issubset(
        customers
    ):

        raise ValueError(
            "Invalid customer FK "
            "in bookings."
        )

    if not set(
        booking_sample[
            "route_id"
        ]
    ).issubset(
        routes
    ):

        raise ValueError(
            "Invalid route FK "
            "in bookings."
        )

    if not set(
        booking_sample[
            "ticket_id"
        ]
    ).issubset(
        tickets
    ):

        raise ValueError(
            "Invalid ticket FK "
            "in bookings."
        )

    print(
        "[OK] Sample foreign-key "
        "validation passed"
    )


def main():

    config = load_config()

    expected_searches = int(
        config[
            "data_generation"
        ][
            "searches"
        ]
    )

    expected_bookings = int(
        config[
            "data_generation"
        ][
            "bookings"
        ]
    )

    search_path = (
        DATA_DIR
        / "fact_searches.parquet"
    )

    booking_path = (
        DATA_DIR
        / "fact_bookings.parquet"
    )

    print(
        "=" * 72
    )

    print(
        "RAILPARTNER 360 - "
        "TRANSACTION VALIDATION"
    )

    print(
        "=" * 72
    )

    search_file = pq.ParquetFile(
        search_path
    )

    booking_file = pq.ParquetFile(
        booking_path
    )

    search_rows = (
        search_file
        .metadata
        .num_rows
    )

    booking_rows = (
        booking_file
        .metadata
        .num_rows
    )

    print(
        f"\nSearch rows:  "
        f"{search_rows:,}"
    )

    print(
        f"Booking rows: "
        f"{booking_rows:,}"
    )

    if search_rows != expected_searches:

        raise ValueError(
            "Incorrect number "
            "of searches."
        )

    if booking_rows != expected_bookings:

        raise ValueError(
            "Incorrect number "
            "of bookings."
        )

    print(
        "\n[OK] Row counts"
    )

    validate_sequential_ids(
        search_path,
        "search_id",
        expected_searches,
    )

    validate_sequential_ids(
        booking_path,
        "booking_id",
        expected_bookings,
    )

    validate_booking_search_ids(
        booking_path,
        expected_searches,
    )

    validate_sample_foreign_keys()

    conversion_rate = (
        booking_rows
        / search_rows
    )

    print(
        "\n" + "=" * 72
    )

    print(
        "TRANSACTION VALIDATION PASSED"
    )

    print(
        "=" * 72
    )

    print(
        f"\nConversion rate: "
        f"{conversion_rate:.2%}"
    )

    print(
        "\nSTAGE 3 VALIDATION COMPLETE"
    )


if __name__ == "__main__":

    try:

        main()

    except Exception as exc:

        print(
            f"\nVALIDATION FAILED: "
            f"{exc}"
        )

        sys.exit(1)
