from pathlib import Path
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SQL_DIR = PROJECT_ROOT / "sql" / "business_analysis"
EXPORT_DIR = PROJECT_ROOT / "data" / "exports" / "stage7_business_analysis"

EXPORT_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(PROJECT_ROOT / ".env", override=True)


host = os.getenv("DB_HOST", "127.0.0.1").strip().lstrip("@")

if host.lower() == "localhost":
    host = "127.0.0.1"

port = int(os.getenv("DB_PORT", "5433"))
database = os.getenv("DB_NAME", "railpartner360")
user = os.getenv("DB_USER", "postgres")
password = os.getenv("DB_PASSWORD")


print("=" * 70)
print("RAILPARTNER 360 - STAGE 7")
print("=" * 70)

print(f"Host:     {host}")
print(f"Port:     {port}")
print(f"Database: {database}")
print(f"User:     {user}")


conn = psycopg2.connect(
    host=host,
    port=port,
    dbname=database,
    user=user,
    password=password,
)

print()
print("[OK] PostgreSQL connection successful")


sql_files = [
    "01_executive_kpis.sql",
    "02_partner_opportunity.sql",
    "03_conversion_funnel.sql",
    "04_customer_segments.sql",
    "05_route_opportunity.sql",
    "06_operator_performance.sql",
    "07_refund_impact.sql",
]


for filename in sql_files:

    sql_path = SQL_DIR / filename

    print()
    print(f"Running: {filename}")

    sql = sql_path.read_text(
        encoding="utf-8-sig"
    )

    with conn.cursor() as cursor:

        cursor.execute(sql)

        rows = cursor.fetchall()

        columns = [
            column.name
            for column in cursor.description
        ]

    df = pd.DataFrame(
        rows,
        columns=columns,
    )

    output_path = (
        EXPORT_DIR
        / filename.replace(".sql", ".csv")
    )

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    print(f"[OK] {len(df):,} rows")
    print(f"[SAVED] {output_path.name}")


conn.close()


print()
print("=" * 70)
print("STAGE 7 SQL ANALYSIS COMPLETE")
print("=" * 70)