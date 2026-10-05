from __future__ import annotations

from io import StringIO
from pathlib import Path
import os
import sys
import time

import pandas as pd
import pyarrow.parquet as pq
import psycopg2
from dotenv import load_dotenv


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "synthetic"
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5433")),
    "dbname": os.getenv("DB_NAME", "railpartner360"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}

if not DB_CONFIG["password"]:
    raise RuntimeError(
        "DB_PASSWORD was not found in .env"
    )


# ============================================================
# INGESTION CONFIGURATION
# ============================================================

SCHEMA = "raw"

BATCH_SIZE = 200_000


# ============================================================
# RAW TABLE DEFINITIONS
# ============================================================

TABLES = {

    "dim_partner": {
        "file": "dim_partner.parquet",
        "columns": [
            "partner_id",
            "partner_name",
            "partner_type",
            "partner_segment",
            "service_tier",
            "headquarters_region",
            "acquisition_channel",
            "contract_start_date",
            "commission_rate",
            "active_flag",
        ],
        "ddl": """
            partner_id TEXT,
            partner_name TEXT,
            partner_type TEXT,
            partner_segment TEXT,
            service_tier TEXT,
            headquarters_region TEXT,
            acquisition_channel TEXT,
            contract_start_date TIMESTAMP,
            commission_rate DOUBLE PRECISION,
            active_flag BOOLEAN
        """,
    },

    "dim_customer": {
        "file": "dim_customer.parquet",
        "columns": [
            "customer_id",
            "signup_date",
            "customer_segment",
            "home_region",
            "loyalty_tier",
            "preferred_device",
            "acquisition_channel",
            "age_band",
            "business_traveller_flag",
            "marketing_opt_in",
        ],
        "ddl": """
            customer_id TEXT,
            signup_date TIMESTAMP,
            customer_segment TEXT,
            home_region TEXT,
            loyalty_tier TEXT,
            preferred_device TEXT,
            acquisition_channel TEXT,
            age_band TEXT,
            business_traveller_flag BOOLEAN,
            marketing_opt_in BOOLEAN
        """,
    },

    "dim_operator": {
        "file": "dim_operator.parquet",
        "columns": [
            "operator_id",
            "operator_name",
            "service_type",
            "synthetic_flag",
        ],
        "ddl": """
            operator_id TEXT,
            operator_name TEXT,
            service_type TEXT,
            synthetic_flag BOOLEAN
        """,
    },

    "dim_station": {
        "file": "dim_station.parquet",
        "columns": [
            "station_id",
            "station_code",
            "station_name",
            "region",
            "station_category",
            "annual_entries_estimate",
            "interchange_flag",
            "synthetic_flag",
        ],
        "ddl": """
            station_id TEXT,
            station_code TEXT,
            station_name TEXT,
            region TEXT,
            station_category TEXT,
            annual_entries_estimate BIGINT,
            interchange_flag BOOLEAN,
            synthetic_flag BOOLEAN
        """,
    },

    "dim_route": {
        "file": "dim_route.parquet",
        "columns": [
            "route_id",
            "origin_station_id",
            "destination_station_id",
            "primary_operator_id",
            "distance_km",
            "route_type",
            "planned_duration_minutes",
            "active_flag",
        ],
        "ddl": """
            route_id TEXT,
            origin_station_id TEXT,
            destination_station_id TEXT,
            primary_operator_id TEXT,
            distance_km DOUBLE PRECISION,
            route_type TEXT,
            planned_duration_minutes INTEGER,
            active_flag BOOLEAN
        """,
    },

    "dim_ticket": {
        "file": "dim_ticket.parquet",
        "columns": [
            "ticket_id",
            "ticket_name",
            "journey_type",
            "fare_category",
            "refundable_flag",
            "changeable_flag",
        ],
        "ddl": """
            ticket_id TEXT,
            ticket_name TEXT,
            journey_type TEXT,
            fare_category TEXT,
            refundable_flag BOOLEAN,
            changeable_flag BOOLEAN
        """,
    },

    "dim_date": {
        "file": "dim_date.parquet",
        "columns": [
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
        ],
        "ddl": """
            date_id INTEGER,
            date TIMESTAMP,
            year INTEGER,
            quarter TEXT,
            month_number INTEGER,
            month_name TEXT,
            year_month TEXT,
            week_number INTEGER,
            day_of_month INTEGER,
            day_name TEXT,
            day_of_week INTEGER,
            weekend_flag BOOLEAN,
            season TEXT
        """,
    },

    "fact_searches": {
        "file": "fact_searches.parquet",
        "columns": [
            "search_id",
            "customer_id",
            "partner_id",
            "route_id",
            "search_timestamp",
            "search_date",
            "travel_date",
            "booking_lead_days",
            "sales_channel",
            "customer_segment",
            "business_traveller_flag",
            "route_type",
            "distance_km",
            "result_count",
            "lowest_fare_gbp",
            "availability_flag",
            "converted_flag",
        ],
        "ddl": """
            search_id BIGINT,
            customer_id TEXT,
            partner_id TEXT,
            route_id TEXT,
            search_timestamp TIMESTAMP,
            search_date TIMESTAMP,
            travel_date TIMESTAMP,
            booking_lead_days INTEGER,
            sales_channel TEXT,
            customer_segment TEXT,
            business_traveller_flag BOOLEAN,
            route_type TEXT,
            distance_km DOUBLE PRECISION,
            result_count INTEGER,
            lowest_fare_gbp DOUBLE PRECISION,
            availability_flag BOOLEAN,
            converted_flag BOOLEAN
        """,
    },

    "fact_bookings": {
        "file": "fact_bookings.parquet",
        "columns": [
            "booking_id",
            "search_id",
            "customer_id",
            "partner_id",
            "route_id",
            "ticket_id",
            "booking_timestamp",
            "travel_date",
            "booking_lead_days",
            "sales_channel",
            "business_traveller_flag",
            "passenger_count",
            "booked_fare_gbp",
            "gross_booking_value_gbp",
            "discount_rate",
            "discount_amount_gbp",
            "net_ticket_value_gbp",
            "commission_rate",
            "commission_revenue_gbp",
            "service_fee_gbp",
            "platform_revenue_gbp",
            "payment_method",
            "promotion_used_flag",
            "booking_status",
        ],
        "ddl": """
            booking_id BIGINT,
            search_id BIGINT,
            customer_id TEXT,
            partner_id TEXT,
            route_id TEXT,
            ticket_id TEXT,
            booking_timestamp TIMESTAMP,
            travel_date TIMESTAMP,
            booking_lead_days INTEGER,
            sales_channel TEXT,
            business_traveller_flag BOOLEAN,
            passenger_count INTEGER,
            booked_fare_gbp DOUBLE PRECISION,
            gross_booking_value_gbp DOUBLE PRECISION,
            discount_rate DOUBLE PRECISION,
            discount_amount_gbp DOUBLE PRECISION,
            net_ticket_value_gbp DOUBLE PRECISION,
            commission_rate DOUBLE PRECISION,
            commission_revenue_gbp DOUBLE PRECISION,
            service_fee_gbp DOUBLE PRECISION,
            platform_revenue_gbp DOUBLE PRECISION,
            payment_method TEXT,
            promotion_used_flag BOOLEAN,
            booking_status TEXT
        """,
    },

    "fact_journeys": {
        "file": "fact_journeys.parquet",
        "columns": [
            "journey_id",
            "booking_id",
            "customer_id",
            "partner_id",
            "route_id",
            "operator_id",
            "ticket_id",
            "travel_date",
            "scheduled_departure",
            "scheduled_arrival",
            "actual_departure",
            "actual_arrival",
            "planned_duration_minutes",
            "distance_km",
            "route_type",
            "journey_status",
            "departure_delay_minutes",
            "arrival_delay_minutes",
            "delay_band",
            "within_3_minutes_flag",
            "within_15_minutes_flag",
            "severe_delay_flag",
            "operational_disruption_flag",
            "disruption_reason",
            "compensation_eligible_flag",
            "business_traveller_flag",
            "sales_channel",
        ],
        "ddl": """
            journey_id BIGINT,
            booking_id BIGINT,
            customer_id TEXT,
            partner_id TEXT,
            route_id TEXT,
            operator_id TEXT,
            ticket_id TEXT,
            travel_date TIMESTAMP,
            scheduled_departure TIMESTAMP,
            scheduled_arrival TIMESTAMP,
            actual_departure TIMESTAMP,
            actual_arrival TIMESTAMP,
            planned_duration_minutes INTEGER,
            distance_km DOUBLE PRECISION,
            route_type TEXT,
            journey_status TEXT,
            departure_delay_minutes INTEGER,
            arrival_delay_minutes INTEGER,
            delay_band TEXT,
            within_3_minutes_flag BOOLEAN,
            within_15_minutes_flag BOOLEAN,
            severe_delay_flag BOOLEAN,
            operational_disruption_flag BOOLEAN,
            disruption_reason TEXT,
            compensation_eligible_flag BOOLEAN,
            business_traveller_flag BOOLEAN,
            sales_channel TEXT
        """,
    },

    "fact_refunds": {
        "file": "fact_refunds.parquet",
        "columns": [
            "refund_id",
            "booking_id",
            "journey_id",
            "customer_id",
            "partner_id",
            "refund_type",
            "refund_reason",
            "refund_status",
            "refund_request_timestamp",
            "refund_processed_timestamp",
            "eligible_value_gbp",
            "refund_rate",
            "refund_amount_gbp",
            "commercial_value_at_risk_gbp",
            "processing_days",
            "business_traveller_flag",
            "sales_channel",
        ],
        "ddl": """
            refund_id BIGINT,
            booking_id BIGINT,
            journey_id BIGINT,
            customer_id TEXT,
            partner_id TEXT,
            refund_type TEXT,
            refund_reason TEXT,
            refund_status TEXT,
            refund_request_timestamp TIMESTAMP,
            refund_processed_timestamp TIMESTAMP,
            eligible_value_gbp DOUBLE PRECISION,
            refund_rate DOUBLE PRECISION,
            refund_amount_gbp DOUBLE PRECISION,
            commercial_value_at_risk_gbp DOUBLE PRECISION,
            processing_days INTEGER,
            business_traveller_flag BOOLEAN,
            sales_channel TEXT
        """,
    },
}


# ============================================================
# CONNECT
# ============================================================

def connect():

    conn = psycopg2.connect(
        **DB_CONFIG
    )

    conn.autocommit = False

    with conn.cursor() as cursor:

        cursor.execute(
            "SET synchronous_commit = OFF;"
        )

    conn.commit()

    return conn


# ============================================================
# VALIDATE SOURCE FILES
# ============================================================

def validate_source_files():

    print("\nChecking Parquet source files...")
    print("-" * 72)

    missing = []

    for table_name, config in TABLES.items():

        path = DATA_DIR / config["file"]

        if path.exists():

            parquet = pq.ParquetFile(path)

            rows = (
                parquet
                .metadata
                .num_rows
            )

            print(
                f"[OK] {table_name:<20} "
                f"{rows:>12,} rows"
            )

        else:

            print(
                f"[MISSING] {path.name}"
            )

            missing.append(
                str(path)
            )

    if missing:

        raise FileNotFoundError(
            "Required Parquet files are missing."
        )


# ============================================================
# CREATE RAW TABLE
# ============================================================

def create_table(
    conn,
    table_name,
    ddl,
):

    with conn.cursor() as cursor:

        cursor.execute(
            f'DROP TABLE IF EXISTS '
            f'"{SCHEMA}"."{table_name}" CASCADE;'
        )

        cursor.execute(
            f'''
            CREATE TABLE
            "{SCHEMA}"."{table_name}"
            (
                {ddl}
            );
            '''
        )

    conn.commit()


# ============================================================
# COPY PANDAS BATCH INTO POSTGRESQL
# ============================================================

def copy_dataframe(
    conn,
    table_name,
    columns,
    dataframe,
):

    buffer = StringIO()

    dataframe.to_csv(
        buffer,
        index=False,
        header=False,
        na_rep="\\N",
        lineterminator="\n",
    )

    buffer.seek(0)

    column_sql = ", ".join(
        f'"{column}"'
        for column in columns
    )

    copy_sql = f'''
        COPY "{SCHEMA}"."{table_name}"
        ({column_sql})
        FROM STDIN
        WITH (
            FORMAT CSV,
            NULL '\\N'
        )
    '''

    with conn.cursor() as cursor:

        cursor.copy_expert(
            copy_sql,
            buffer,
        )


# ============================================================
# LOAD PARQUET TABLE
# ============================================================

def load_table(
    conn,
    table_name,
    config,
):

    parquet_path = (
        DATA_DIR
        / config["file"]
    )

    expected_columns = (
        config["columns"]
    )

    parquet = pq.ParquetFile(
        parquet_path
    )

    source_columns = (
        parquet.schema.names
    )

    if source_columns != expected_columns:

        raise ValueError(
            f"\nColumn mismatch for {table_name}\n"
            f"Expected: {expected_columns}\n"
            f"Found:    {source_columns}"
        )

    total_rows = (
        parquet
        .metadata
        .num_rows
    )

    create_table(
        conn,
        table_name,
        config["ddl"],
    )

    loaded = 0

    batch_number = 0

    print(
        f"\nLoading raw.{table_name}"
    )

    print(
        f"Source rows: {total_rows:,}"
    )

    for batch in parquet.iter_batches(
        batch_size=BATCH_SIZE,
    ):

        batch_number += 1

        df = (
            batch
            .to_pandas()
            .loc[
                :,
                expected_columns
            ]
        )

        copy_dataframe(
            conn,
            table_name,
            expected_columns,
            df,
        )

        conn.commit()

        loaded += len(df)

        print(
            f"  Batch {batch_number:02d} | "
            f"{loaded:>10,}"
            f"/{total_rows:,}"
        )

        del df

    if loaded != total_rows:

        raise ValueError(
            f"{table_name}: "
            f"loaded {loaded:,} "
            f"but expected {total_rows:,}"
        )

    with conn.cursor() as cursor:

        cursor.execute(
            f'''
            ANALYZE
            "{SCHEMA}"."{table_name}";
            '''
        )

    conn.commit()

    print(
        f"[LOADED] raw.{table_name}: "
        f"{loaded:,} rows"
    )


# ============================================================
# DATABASE COUNT VALIDATION
# ============================================================

def validate_database_counts(
    conn,
):

    print(
        "\n"
        + "=" * 72
    )

    print(
        "POSTGRESQL ROW COUNT VALIDATION"
    )

    print(
        "=" * 72
    )

    all_valid = True

    results = []

    with conn.cursor() as cursor:

        for table_name, config in (
            TABLES.items()
        ):

            parquet = pq.ParquetFile(
                DATA_DIR
                / config["file"]
            )

            source_rows = (
                parquet
                .metadata
                .num_rows
            )

            cursor.execute(
                f'''
                SELECT COUNT(*)
                FROM "{SCHEMA}"."{table_name}";
                '''
            )

            database_rows = (
                cursor.fetchone()[0]
            )

            valid = (
                database_rows
                == source_rows
            )

            results.append(
                (
                    table_name,
                    source_rows,
                    database_rows,
                    valid,
                )
            )

            if not valid:
                all_valid = False

    for (
        table_name,
        source_rows,
        database_rows,
        valid,
    ) in results:

        status = (
            "[OK]"
            if valid
            else "[FAILED]"
        )

        print(
            f"{status} "
            f"{table_name:<20} "
            f"source={source_rows:>10,} "
            f"postgres={database_rows:>10,}"
        )

    if not all_valid:

        raise ValueError(
            "PostgreSQL row-count validation failed."
        )

    return results


# ============================================================
# WAREHOUSE SUMMARY
# ============================================================

def print_summary(
    results,
):

    total = sum(
        database_rows
        for (
            _,
            _,
            database_rows,
            _,
        ) in results
    )

    print(
        "\n"
        + "=" * 72
    )

    print(
        "RAILPARTNER 360 RAW WAREHOUSE"
    )

    print(
        "=" * 72
    )

    print(
        f"\nTables loaded: "
        f"{len(results)}"
    )

    print(
        f"Total PostgreSQL rows: "
        f"{total:,}"
    )

    print(
        "\nDatabase:"
        f" {DB_CONFIG['dbname']}"
    )

    print(
        f"Schema:"
        f" {SCHEMA}"
    )

    print(
        f"PostgreSQL port:"
        f" {DB_CONFIG['port']}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 72
    )

    print(
        "RAILPARTNER 360"
    )

    print(
        "PARQUET -> POSTGRESQL RAW WAREHOUSE"
    )

    print(
        "=" * 72
    )

    print(
        f"\nDatabase: "
        f"{DB_CONFIG['dbname']}"
    )

    print(
        f"Host:     "
        f"{DB_CONFIG['host']}"
    )

    print(
        f"Port:     "
        f"{DB_CONFIG['port']}"
    )

    validate_source_files()

    print(
        "\nConnecting to PostgreSQL..."
    )

    conn = connect()

    print(
        "[OK] PostgreSQL connection established"
    )

    try:

        with conn.cursor() as cursor:

            cursor.execute(
                f'''
                CREATE SCHEMA IF NOT EXISTS
                "{SCHEMA}";
                '''
            )

        conn.commit()

        for table_name, config in (
            TABLES.items()
        ):

            load_table(
                conn,
                table_name,
                config,
            )

        results = (
            validate_database_counts(
                conn
            )
        )

        print_summary(
            results
        )

    finally:

        conn.close()

    print(
        "\n"
        + "=" * 72
    )

    print(
        "STAGE 5C COMPLETE"
    )

    print(
        "POSTGRESQL RAW WAREHOUSE VALIDATED"
    )

    print(
        "=" * 72
    )


if __name__ == "__main__":

    try:

        main()

    except Exception as exc:

        print(
            "\n"
            + "=" * 72
        )

        print(
            "STAGE 5C FAILED"
        )

        print(
            "=" * 72
        )

        print(
            f"\n{type(exc).__name__}: "
            f"{exc}"
        )

        sys.exit(1)
