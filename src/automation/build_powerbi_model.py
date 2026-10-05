from __future__ import annotations

from pathlib import Path
import shutil

import pandas as pd


# ============================================================
# RAILPARTNER 360
# STAGE 8D — POWER BI SEMANTIC MODEL BUILDER
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

POWERBI_DIR = ROOT / "powerbi"
DATA_DIR = POWERBI_DIR / "data"

MODEL_DIR = (
    POWERBI_DIR
    / "RailPartner_360.SemanticModel"
)

DEFINITION_DIR = (
    MODEL_DIR
    / "definition"
)

TABLES_DIR = (
    DEFINITION_DIR
    / "tables"
)

BACKUP_DIR = (
    POWERBI_DIR
    / "backups"
    / "stage8d_native_semantic_model"
)


# ============================================================
# TABLE CONFIGURATION
# ============================================================

TABLES = {
    "Executive KPIs": "01_executive_kpis.csv",
    "Partner Performance": "02_partner_opportunity.csv",
    "Conversion Funnel": "03_conversion_funnel.csv",
    "Customer Segments": "04_customer_segments.csv",
    "Route Opportunity": "05_route_opportunity.csv",
    "Operator Performance": "06_operator_performance.csv",
    "Refund Impact": "07_refund_impact.csv",
}


# ============================================================
# EXECUTIVE KPI MEASURES
# ============================================================

EXECUTIVE_MEASURES = [
    (
        "Total Searches",
        "MAX('Executive KPIs'[total_searches])",
        "#,0",
    ),
    (
        "Total Bookings",
        "MAX('Executive KPIs'[total_bookings])",
        "#,0",
    ),
    (
        "Conversion Rate %",
        "MAX('Executive KPIs'[conversion_rate_pct])",
        "0.00",
    ),
    (
        "Gross Booking Value",
        "MAX('Executive KPIs'[gross_booking_value_gbp])",
        "£#,0.00",
    ),
    (
        "Platform Revenue",
        "MAX('Executive KPIs'[platform_revenue_gbp])",
        "£#,0.00",
    ),
    (
        "Average Booking Value",
        "MAX('Executive KPIs'[average_booking_value_gbp])",
        "£#,0.00",
    ),
    (
        "B2B Booking Share %",
        "MAX('Executive KPIs'[b2b_booking_share_pct])",
        "0.00",
    ),
    (
        "Total Journeys",
        "MAX('Executive KPIs'[total_journeys])",
        "#,0",
    ),
    (
        "Disruption Rate %",
        "MAX('Executive KPIs'[disruption_rate_pct])",
        "0.00",
    ),
    (
        "Cancellation Rate %",
        "MAX('Executive KPIs'[operator_cancellation_rate_pct])",
        "0.00",
    ),
    (
        "Within 3 Minutes %",
        "MAX('Executive KPIs'[within_3_minutes_pct])",
        "0.00",
    ),
    (
        "Refund Records",
        "MAX('Executive KPIs'[refund_records])",
        "#,0",
    ),
    (
        "Refund Amount",
        "MAX('Executive KPIs'[total_refund_amount_gbp])",
        "£#,0.00",
    ),
    (
        "Commercial Value at Risk",
        "MAX('Executive KPIs'[commercial_value_at_risk_gbp])",
        "£#,0.00",
    ),
]


PARTNER_MEASURES = [
    (
        "Partner Count",
        "DISTINCTCOUNT('Partner Performance'[partner_id])",
        "#,0",
    ),
    (
        "Partner Revenue",
        "SUM('Partner Performance'[platform_revenue_gbp])",
        "£#,0.00",
    ),
    (
        "Partner Bookings",
        "SUM('Partner Performance'[bookings])",
        "#,0",
    ),
    (
        "Average Partner Conversion %",
        "AVERAGE('Partner Performance'[conversion_rate_pct])",
        "0.00",
    ),
    (
        "Partner Value at Risk",
        "SUM('Partner Performance'[commercial_value_at_risk_gbp])",
        "£#,0.00",
    ),
]


REFUND_MEASURES = [
    (
        "Refund Analysis Records",
        "SUM('Refund Impact'[refund_records])",
        "#,0",
    ),
    (
        "Refund Analysis Amount",
        "SUM('Refund Impact'[refund_amount_gbp])",
        "£#,0.00",
    ),
    (
        "Refund Analysis Value at Risk",
        "SUM('Refund Impact'[commercial_value_at_risk_gbp])",
        "£#,0.00",
    ),
]


# ============================================================
# HELPERS
# ============================================================

def write_text(path: Path, content: str) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        content.rstrip() + "\n",
        encoding="utf-8",
    )


def tmdl_identifier(value: str) -> str:

    simple = (
        value.replace("_", "")
        .replace("-", "")
        .isalnum()
    )

    if simple and " " not in value:
        return value

    escaped = value.replace(
        "'",
        "''",
    )

    return f"'{escaped}'"


def m_escape(value: str) -> str:

    return (
        str(value)
        .replace('"', '""')
    )


def infer_type(series: pd.Series):

    if pd.api.types.is_bool_dtype(series):

        return (
            "boolean",
            "type logical",
        )

    if pd.api.types.is_integer_dtype(series):

        return (
            "int64",
            "Int64.Type",
        )

    if pd.api.types.is_float_dtype(series):

        return (
            "double",
            "type number",
        )

    if pd.api.types.is_datetime64_any_dtype(series):

        return (
            "dateTime",
            "type datetime",
        )

    return (
        "string",
        "type text",
    )


def measure_block(
    name: str,
    expression: str,
    format_string: str,
):

    return [
        f"\tmeasure {tmdl_identifier(name)} = {expression}",
        f"\t\tformatString: {format_string}",
        "",
    ]


# ============================================================
# START
# ============================================================

print("=" * 76)
print("RAILPARTNER 360 — STAGE 8D")
print("POWER BI SEMANTIC MODEL BUILD")
print("=" * 76)


# ============================================================
# VERIFY NATIVE POWER BI PROJECT
# ============================================================

model_tmdl = (
    DEFINITION_DIR
    / "model.tmdl"
)

if not model_tmdl.exists():

    raise FileNotFoundError(
        f"Native Power BI model.tmdl not found:\n"
        f"{model_tmdl}"
    )


for csv_name in TABLES.values():

    csv_path = (
        DATA_DIR
        / csv_name
    )

    if not csv_path.exists():

        raise FileNotFoundError(
            f"Missing Power BI CSV:\n"
            f"{csv_path}"
        )


print()
print("[OK] Native PBIP semantic model found")
print("[OK] Seven analytical CSV files found")


# ============================================================
# BACKUP NATIVE MODEL
# ============================================================

if not BACKUP_DIR.exists():

    shutil.copytree(
        DEFINITION_DIR,
        BACKUP_DIR,
    )

    print(
        "[OK] Native semantic model backup created"
    )

else:

    print(
        "[OK] Native semantic model backup already exists"
    )


# ============================================================
# TABLE DIRECTORY
# ============================================================

TABLES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# Remove only table files generated by this build.

for path in TABLES_DIR.glob("*.tmdl"):

    path.unlink()


# ============================================================
# BUILD MODEL.TMDL
# ============================================================

model_lines = [
    "model Model",
    "\tculture: en-GB",
    "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
    "\tsourceQueryCulture: en-GB",
    "\tvalueFilterBehavior: independent",
    "\tdataAccessOptions",
    "\t\tlegacyRedirects",
    "\t\treturnErrorValuesAsNull",
    "",
    "annotation __PBI_TimeIntelligenceEnabled = 1",
    "",
    'annotation PBI_ProTooling = ["DevMode"]',
    "",
]


for table_name in TABLES:

    model_lines.append(
        f"ref table {tmdl_identifier(table_name)}"
    )


model_lines.extend(
    [
        "",
        "ref cultureInfo en-GB",
        "",
    ]
)


write_text(
    model_tmdl,
    "\n".join(model_lines),
)

print(
    "[OK] model.tmdl updated with seven table references"
)


# ============================================================
# BUILD TABLE FILES
# ============================================================

for table_name, csv_name in TABLES.items():

    csv_path = (
        DATA_DIR
        / csv_name
    ).resolve()

    dataframe = pd.read_csv(
        csv_path,
        low_memory=False,
    )

    lines = [
        f"table {tmdl_identifier(table_name)}",
        "",
    ]


    # --------------------------------------------------------
    # DAX MEASURES
    # --------------------------------------------------------

    if table_name == "Executive KPIs":

        for (
            measure_name,
            expression,
            format_string,
        ) in EXECUTIVE_MEASURES:

            lines.extend(
                measure_block(
                    measure_name,
                    expression,
                    format_string,
                )
            )


    if table_name == "Partner Performance":

        for (
            measure_name,
            expression,
            format_string,
        ) in PARTNER_MEASURES:

            lines.extend(
                measure_block(
                    measure_name,
                    expression,
                    format_string,
                )
            )


    if table_name == "Refund Impact":

        for (
            measure_name,
            expression,
            format_string,
        ) in REFUND_MEASURES:

            lines.extend(
                measure_block(
                    measure_name,
                    expression,
                    format_string,
                )
            )


    # --------------------------------------------------------
    # COLUMNS
    # --------------------------------------------------------

    m_type_pairs = []

    for column in dataframe.columns:

        tmdl_type, m_type = infer_type(
            dataframe[column]
        )

        lines.extend(
            [
                f"\tcolumn {tmdl_identifier(column)}",
                f"\t\tdataType: {tmdl_type}",
                "\t\tsummarizeBy: none",
                f"\t\tsourceColumn: {column}",
                "",
                "\t\tannotation SummarizationSetBy = Automatic",
                "",
            ]
        )

        escaped_column = m_escape(
            column
        )

        m_type_pairs.append(
            f'{{"{escaped_column}", {m_type}}}'
        )


    # --------------------------------------------------------
    # POWER QUERY PARTITION
    # --------------------------------------------------------

    partition_name = (
        table_name
        .replace(" ", "")
        .replace("&", "And")
        .replace("-", "")
    )

    file_path = m_escape(
        str(csv_path)
    )

    type_definition = (
        ", ".join(
            m_type_pairs
        )
    )

    lines.extend(
        [
            (
                f"\tpartition "
                f"{tmdl_identifier(partition_name)} = m"
            ),
            "\t\tmode: import",
            "\t\tsource =",
            "\t\t\tlet",
            (
                "\t\t\t\tSource = "
                "Csv.Document("
                f'File.Contents("{file_path}"), '
                '[Delimiter=",", '
                "Encoding=65001, "
                "QuoteStyle=QuoteStyle.Csv]"
                "),"
            ),
            (
                '\t\t\t\t#"Promoted Headers" = '
                "Table.PromoteHeaders("
                "Source, "
                "[PromoteAllScalars=true]"
                "),"
            ),
            (
                '\t\t\t\t#"Changed Type" = '
                "Table.TransformColumnTypes("
                '#"Promoted Headers", '
                f"{{{type_definition}}}, "
                '"en-GB"'
                ")"
            ),
            "\t\t\tin",
            '\t\t\t\t#"Changed Type"',
            "",
        ]
    )


    table_path = (
        TABLES_DIR
        / f"{table_name}.tmdl"
    )

    write_text(
        table_path,
        "\n".join(lines),
    )

    print(
        f"[TABLE] {table_name:<24} "
        f"{len(dataframe):>6,} rows | "
        f"{len(dataframe.columns):>2} columns"
    )


# ============================================================
# UTF-8 BOM VALIDATION
# ============================================================

bom_files = []

for path in DEFINITION_DIR.rglob("*.tmdl"):

    if path.read_bytes().startswith(
        b"\xef\xbb\xbf"
    ):

        bom_files.append(path)


if bom_files:

    print()
    print("ERROR — UTF-8 BOM found:")

    for path in bom_files:

        print(path)

    raise SystemExit(1)


# ============================================================
# VALIDATE EXPECTED FILES
# ============================================================

generated_tables = list(
    TABLES_DIR.glob("*.tmdl")
)

if len(generated_tables) != 7:

    raise RuntimeError(
        "Expected 7 TMDL table files but found "
        f"{len(generated_tables)}"
    )


model_content = model_tmdl.read_text(
    encoding="utf-8"
)

for table_name in TABLES:

    expected = (
        f"ref table "
        f"{tmdl_identifier(table_name)}"
    )

    if expected not in model_content:

        raise RuntimeError(
            f"Missing model reference: "
            f"{table_name}"
        )


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 76)
print("STAGE 8D VALIDATION")
print("=" * 76)

print(
    "[OK] Seven TMDL tables created"
)

print(
    "[OK] Table references added to model.tmdl"
)

print(
    "[OK] Executive KPI measures created"
)

print(
    "[OK] Partner measures created"
)

print(
    "[OK] Refund risk measures created"
)

print(
    "[OK] Power Query CSV partitions created"
)

print(
    "[OK] Native Power BI project preserved"
)

print(
    "[OK] UTF-8 without BOM"
)

print()
print("=" * 76)
print("STAGE 8D SEMANTIC MODEL BUILD COMPLETE")
print("=" * 76)