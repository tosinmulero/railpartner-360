from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "synthetic"

BOOKINGS = DATA_DIR / "fact_bookings.parquet"

JOURNEYS = DATA_DIR / "fact_journeys.parquet"

REFUNDS = DATA_DIR / "fact_refunds.parquet"

OPERATORS = DATA_DIR / "dim_operator.parquet"


def validate_sequential(
    file_path,
    column,
    expected_rows,
):

    parquet = pq.ParquetFile(
        file_path
    )

    expected_id = 1

    total = 0

    for batch in parquet.iter_batches(
        columns=[column],
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
                f"{column} is not sequential."
            )

        expected_id += len(
            ids
        )

        total += len(
            ids
        )

    if total != expected_rows:

        raise ValueError(
            f"{column} row count mismatch."
        )

    print(
        f"[OK] {column}: "
        f"{total:,} sequential IDs"
    )


def main():

    print(
        "=" * 72
    )

    print(
        "RAILPARTNER 360 - "
        "STAGE 4 VALIDATION"
    )

    print(
        "=" * 72
    )

    booking_file = pq.ParquetFile(
        BOOKINGS
    )

    journey_file = pq.ParquetFile(
        JOURNEYS
    )

    refund_file = pq.ParquetFile(
        REFUNDS
    )

    booking_rows = (
        booking_file
        .metadata
        .num_rows
    )

    journey_rows = (
        journey_file
        .metadata
        .num_rows
    )

    refund_rows = (
        refund_file
        .metadata
        .num_rows
    )

    print(
        f"\nBookings: {booking_rows:,}"
    )

    print(
        f"Journeys: {journey_rows:,}"
    )

    print(
        f"Refunds:  {refund_rows:,}"
    )

    if journey_rows != booking_rows:

        raise ValueError(
            "Every booking must map to "
            "one journey record."
        )

    print(
        "\n[OK] Journey row count "
        "matches bookings"
    )

    validate_sequential(
        JOURNEYS,
        "journey_id",
        journey_rows,
    )

    validate_sequential(
        REFUNDS,
        "refund_id",
        refund_rows,
    )

    # --------------------------------------------------------
    # Validate booking relationship
    # --------------------------------------------------------

    previous = 0

    checked = 0

    for batch in journey_file.iter_batches(
        columns=["booking_id"],
        batch_size=250_000,
    ):

        values = (
            batch
            .column(0)
            .to_numpy()
        )

        if np.any(
            np.diff(values) <= 0
        ):

            raise ValueError(
                "Journey booking_id duplicates detected."
            )

        if previous:

            if values[0] <= previous:

                raise ValueError(
                    "Journey booking_id ordering failed."
                )

        previous = values[-1]

        checked += len(
            values
        )

    print(
        f"[OK] Journey → Booking FK: "
        f"{checked:,} records"
    )

    # --------------------------------------------------------
    # Validate operator IDs
    # --------------------------------------------------------

    valid_operators = set(
        pd.read_parquet(
            OPERATORS,
            columns=[
                "operator_id"
            ],
        )[
            "operator_id"
        ]
    )

    for batch in journey_file.iter_batches(
        columns=[
            "operator_id"
        ],
        batch_size=250_000,
    ):

        operators = set(
            batch
            .column(0)
            .to_pylist()
        )

        if not operators.issubset(
            valid_operators
        ):

            raise ValueError(
                "Invalid operator foreign key."
            )

    print(
        "[OK] Operator foreign keys"
    )

    # --------------------------------------------------------
    # Validate status logic
    # --------------------------------------------------------

    status_counts = {}

    disruption_count = 0

    compensation_count = 0

    for batch in journey_file.iter_batches(
        columns=[
            "journey_status",
            "operational_disruption_flag",
            "compensation_eligible_flag",
        ],
        batch_size=250_000,
    ):

        df = batch.to_pandas()

        counts = (
            df[
                "journey_status"
            ]
            .value_counts()
            .to_dict()
        )

        for key, value in counts.items():

            status_counts[key] = (
                status_counts.get(
                    key,
                    0,
                )
                + int(value)
            )

        disruption_count += int(
            df[
                "operational_disruption_flag"
            ]
            .sum()
        )

        compensation_count += int(
            df[
                "compensation_eligible_flag"
            ]
            .sum()
        )

    print(
        "\nJourney status:"
    )

    for status, count in (
        sorted(
            status_counts.items()
        )
    ):

        print(
            f"  {status:<22} "
            f"{count:>10,}"
        )

    print(
        f"\nOperational disruptions: "
        f"{disruption_count:,}"
    )

    print(
        f"Compensation eligible:    "
        f"{compensation_count:,}"
    )

    if refund_rows <= 0:

        raise ValueError(
            "No refund records created."
        )

    print(
        "\n[OK] Refund records created"
    )

    print(
        "\n"
        + "=" * 72
    )

    print(
        "STAGE 4 VALIDATION PASSED"
    )

    print(
        "=" * 72
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
