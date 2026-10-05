from __future__ import annotations

from getpass import getpass
from pathlib import Path
import sys

import psycopg2
from psycopg2 import sql


HOST = "localhost"
PORT = 5433
ADMIN_USER = "postgres"
DATABASE = "railpartner360"

SCHEMAS = [
    "raw",
    "staging",
    "intermediate",
    "marts",
]


def main():

    print("=" * 70)
    print("RAILPARTNER 360 - POSTGRESQL DATABASE SETUP")
    print("=" * 70)

    print(f"\nServer: PostgreSQL 18")
    print(f"Host:   {HOST}")
    print(f"Port:   {PORT}")
    print(f"User:   {ADMIN_USER}")
    print(f"Target: {DATABASE}")

    password = getpass(
        "\nEnter your PostgreSQL 'postgres' password: "
    )

    # --------------------------------------------------------
    # CONNECT TO DEFAULT POSTGRES DATABASE
    # --------------------------------------------------------

    try:
        admin_conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            dbname="postgres",
            user=ADMIN_USER,
            password=password,
        )

        admin_conn.autocommit = True

        print("\n[OK] Connected to PostgreSQL 18")

    except Exception as exc:

        print(
            "\n[FAILED] Could not connect to PostgreSQL."
        )

        print(exc)

        sys.exit(1)

    # --------------------------------------------------------
    # CREATE DATABASE IF NECESSARY
    # --------------------------------------------------------

    with admin_conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT 1
            FROM pg_database
            WHERE datname = %s
            """,
            (DATABASE,),
        )

        exists = cursor.fetchone()

        if exists:

            print(
                f"[OK] Database '{DATABASE}' already exists"
            )

        else:

            cursor.execute(
                sql.SQL(
                    "CREATE DATABASE {}"
                ).format(
                    sql.Identifier(DATABASE)
                )
            )

            print(
                f"[CREATED] Database '{DATABASE}'"
            )

    admin_conn.close()

    # --------------------------------------------------------
    # CONNECT TO RAILPARTNER DATABASE
    # --------------------------------------------------------

    try:

        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            dbname=DATABASE,
            user=ADMIN_USER,
            password=password,
        )

        conn.autocommit = True

        print(
            f"[OK] Connected to '{DATABASE}'"
        )

    except Exception as exc:

        print(
            "\n[FAILED] Could not connect to RailPartner database."
        )

        print(exc)

        sys.exit(1)

    # --------------------------------------------------------
    # CREATE SCHEMAS
    # --------------------------------------------------------

    with conn.cursor() as cursor:

        for schema_name in SCHEMAS:

            cursor.execute(
                sql.SQL(
                    "CREATE SCHEMA IF NOT EXISTS {}"
                ).format(
                    sql.Identifier(
                        schema_name
                    )
                )
            )

            print(
                f"[OK] Schema: {schema_name}"
            )

    # --------------------------------------------------------
    # DATABASE INFORMATION
    # --------------------------------------------------------

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                current_database(),
                current_user,
                version()
            """
        )

        database_name, user_name, version = (
            cursor.fetchone()
        )

        print("\nDATABASE CONNECTION")
        print("-" * 70)

        print(
            f"Database: {database_name}"
        )

        print(
            f"User:     {user_name}"
        )

        print(
            f"Version:  {version.split(',')[0]}"
        )

        cursor.execute(
            """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name IN (
                'raw',
                'staging',
                'intermediate',
                'marts'
            )
            ORDER BY schema_name
            """
        )

        schemas = [
            row[0]
            for row in cursor.fetchall()
        ]

    print("\nANALYTICS SCHEMAS")
    print("-" * 70)

    for schema_name in schemas:

        print(
            f"[OK] {schema_name}"
        )

    # --------------------------------------------------------
    # WRITE LOCAL ENVIRONMENT FILE
    # --------------------------------------------------------

    env_path = (
        Path(__file__).resolve().parents[2]
        / ".env"
    )

    env_content = (
        f"DB_HOST={HOST}\n"
        f"DB_PORT={PORT}\n"
        f"DB_NAME={DATABASE}\n"
        f"DB_USER={ADMIN_USER}\n"
        f"DB_PASSWORD={password}\n"
    )

    env_path.write_text(
        env_content,
        encoding="utf-8",
    )

    print(
        "\n[OK] Local .env configuration created"
    )

    print(
        "[OK] .env is excluded from Git by .gitignore"
    )

    conn.close()

    print(
        "\n"
        + "=" * 70
    )

    print(
        "POSTGRESQL DATABASE SETUP COMPLETE"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()
