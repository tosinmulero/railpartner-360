from __future__ import annotations

from pathlib import Path
import hashlib
import json
import uuid

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

POWERBI = ROOT / "powerbi"
DATA_DIR = POWERBI / "data"

PROJECT_NAME = "RailPartner_360"

REPORT_DIR = POWERBI / f"{PROJECT_NAME}.Report"
SEMANTIC_DIR = POWERBI / f"{PROJECT_NAME}.SemanticModel"

REPORT_DEFINITION = REPORT_DIR / "definition"
PAGES_DIR = REPORT_DEFINITION / "pages"

MODEL_DEFINITION = SEMANTIC_DIR / "definition"
TABLES_DIR = MODEL_DEFINITION / "tables"


# ============================================================
# SOURCE TABLES
# ============================================================

TABLES = {
    "01_executive_kpis.csv": "Executive KPIs",
    "02_partner_opportunity.csv": "Partner Performance",
    "03_conversion_funnel.csv": "Conversion Funnel",
    "04_customer_segments.csv": "Customer Segments",
    "05_route_opportunity.csv": "Route Opportunity",
    "06_operator_performance.csv": "Operator Performance",
    "07_refund_impact.csv": "Refund Impact",
}


PAGES = [
    "Executive Overview",
    "Partner Performance",
    "Customer & Conversion",
    "Routes & Operations",
    "Refund & Commercial Risk",
]


# ============================================================
# HELPERS
# ============================================================

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        text,
        encoding="utf-8",
        newline="\n",
    )


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def tmdl_identifier(name: str) -> str:

    if (
        name.replace("_", "").isalnum()
        and not name[0].isdigit()
        and " " not in name
    ):
        return name

    return "'" + name.replace("'", "''") + "'"


def page_id(name: str) -> str:
    return hashlib.sha1(
        name.encode("utf-8")
    ).hexdigest()[:20]


def infer_type(series: pd.Series):

    if pd.api.types.is_bool_dtype(series):
        return "boolean", "type logical"

    if pd.api.types.is_integer_dtype(series):
        return "int64", "Int64.Type"

    if pd.api.types.is_float_dtype(series):
        return "double", "type number"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "dateTime", "type datetime"

    return "string", "type text"


# ============================================================
# CHECK INPUT DATA
# ============================================================

print("=" * 72)
print("RAILPARTNER 360 — POWER BI PROJECT BUILD")
print("=" * 72)

missing = []

for csv_name in TABLES:

    csv_path = DATA_DIR / csv_name

    if not csv_path.exists():
        missing.append(str(csv_path))

if missing:

    print()
    print("ERROR: Missing Power BI input files:")

    for item in missing:
        print(item)

    raise SystemExit(1)

print()
print("[OK] All seven CSV input files exist.")


# ============================================================
# CREATE DIRECTORIES
# ============================================================

REPORT_DEFINITION.mkdir(
    parents=True,
    exist_ok=True,
)

PAGES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

TABLES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# PBIP PROJECT SHORTCUT
# ============================================================

pbip = {
    "$schema":
        "https://developer.microsoft.com/json-schemas/"
        "fabric/pbip/pbipProperties/1.0.0/schema.json",

    "version": "1.0",

    "artifacts": [
        {
            "report": {
                "path": f"{PROJECT_NAME}.Report"
            }
        }
    ],

    "settings": {
        "enableAutoRecovery": True
    },
}

write_json(
    POWERBI / f"{PROJECT_NAME}.pbip",
    pbip,
)


# ============================================================
# REPORT → SEMANTIC MODEL LINK
# ============================================================

definition_pbir = {
    "$schema":
        "https://developer.microsoft.com/json-schemas/"
        "fabric/item/report/definitionProperties/2.0.0/schema.json",

    "version": "4.0",

    "datasetReference": {
        "byPath": {
            "path": f"../{PROJECT_NAME}.SemanticModel"
        }
    },
}

write_json(
    REPORT_DIR / "definition.pbir",
    definition_pbir,
)


# ============================================================
# PBIR VERSION
# ============================================================

write_json(
    REPORT_DEFINITION / "version.json",
    {
        "$schema":
            "https://developer.microsoft.com/json-schemas/"
            "fabric/item/report/definition/"
            "versionMetadata/1.0.0/schema.json",

        "version": "2.0.0",
    },
)


# ============================================================
# REPORT DEFINITION
# ============================================================

write_json(
    REPORT_DEFINITION / "report.json",
    {
        "$schema":
            "https://developer.microsoft.com/json-schemas/"
            "fabric/item/report/definition/"
            "report/3.3.0/schema.json",

        "themeCollection": {},
    },
)


# ============================================================
# FIVE REPORT PAGES
# ============================================================

page_ids = []

for display_name in PAGES:

    pid = page_id(display_name)

    page_ids.append(pid)

    page_folder = PAGES_DIR / pid

    page_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        page_folder
        / "visuals"
    ).mkdir(
        parents=True,
        exist_ok=True,
    )

    page_definition = {
        "$schema":
            "https://developer.microsoft.com/json-schemas/"
            "fabric/item/report/definition/"
            "page/2.1.0/schema.json",

        "name": pid,
        "displayName": display_name,
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280,
    }

    write_json(
        page_folder / "page.json",
        page_definition,
    )

    print(
        f"[PAGE] {display_name}"
    )


write_json(
    PAGES_DIR / "pages.json",
    {
        "$schema":
            "https://developer.microsoft.com/json-schemas/"
            "fabric/item/report/definition/"
            "pagesMetadata/1.0.0/schema.json",

        "pageOrder": page_ids,
        "activePageName": page_ids[0],
    },
)


# ============================================================
# SEMANTIC MODEL DEFINITION
# ============================================================

write_json(
    SEMANTIC_DIR / "definition.pbism",
    {
        "$schema":
            "https://developer.microsoft.com/json-schemas/"
            "fabric/item/semanticModel/"
            "definitionProperties/1.0.0/schema.json",

        "version": "4.2",

        "settings": {
            "qnaEnabled": False
        },
    },
)


# ============================================================
# DATABASE.TMDL
# ============================================================

database_tmdl = """database RailPartner_360
\tcompatibilityLevel: 1702
\tcompatibilityMode: powerBI
\tlanguage: 2057
"""

write_text(
    MODEL_DEFINITION / "database.tmdl",
    database_tmdl,
)


# ============================================================
# MODEL.TMDL
# ============================================================

model_lines = [
    "model Model",
    "\tculture: en-GB",
    "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
    "\tsourceQueryCulture: en-GB",
    "",
    "\tdataAccessOptions",
    "\t\tlegacyRedirects",
    "\t\treturnErrorValuesAsNull",
    "",
    '\tannotation PBI_ProTooling = ["DevMode"]',
    "",
]

for table_name in TABLES.values():

    model_lines.append(
        f"ref table {tmdl_identifier(table_name)}"
    )

model_lines.append("")

write_text(
    MODEL_DEFINITION / "model.tmdl",
    "\n".join(model_lines),
)


# ============================================================
# CREATE SEVEN TMDL TABLES
# ============================================================

for csv_name, table_name in TABLES.items():

    csv_path = (
        DATA_DIR
        / csv_name
    ).resolve()

    df = pd.read_csv(
        csv_path,
        low_memory=False,
    )

    column_lines = []
    m_type_pairs = []

    for column in df.columns:

        tmdl_type, m_type = infer_type(
            df[column]
        )

        column_lines.extend(
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

        escaped_column = (
            str(column)
            .replace('"', '""')
        )

        m_type_pairs.append(
            f'{{"{escaped_column}", {m_type}}}'
        )

    absolute_path = (
        str(csv_path)
        .replace('"', '""')
    )

    column_count = len(df.columns)

    m_types = ", ".join(
        m_type_pairs
    )

    table_text = [
        f"table {tmdl_identifier(table_name)}",
        "",
        *column_lines,
        f"\tpartition {tmdl_identifier(table_name)} = m",
        "\t\tmode: import",
        "\t\tsource =",
        "\t\t\t\tlet",
        (
            "\t\t\t\t\tSource = "
            "Csv.Document("
            f'File.Contents("{absolute_path}"), '
            "[Delimiter=\",\", "
            f"Columns={column_count}, "
            "Encoding=65001, "
            "QuoteStyle=QuoteStyle.Csv]"
            "),"
        ),
        (
            '\t\t\t\t\t#"Promoted Headers" = '
            "Table.PromoteHeaders("
            "Source, "
            "[PromoteAllScalars=true]"
            "),"
        ),
        (
            '\t\t\t\t\t#"Changed Type" = '
            "Table.TransformColumnTypes("
            '#"Promoted Headers", '
            f"{{{m_types}}}, "
            '"en-GB"'
            ")"
        ),
        "\t\t\t\tin",
        '\t\t\t\t\t#"Changed Type"',
        "",
        "\tannotation PBI_NavigationStepName = Navigation",
        "\tannotation PBI_ResultType = Table",
        "",
    ]

    write_text(
        TABLES_DIR
        / f"{table_name}.tmdl",
        "\n".join(table_text),
    )

    print(
        f"[MODEL] {table_name}: "
        f"{len(df.columns)} columns"
    )


# ============================================================
# GIT IGNORE
# ============================================================

gitignore = ROOT / ".gitignore"

existing = ""

if gitignore.exists():
    existing = gitignore.read_text(
        encoding="utf-8-sig"
    )

required = [
    "**/.pbi/localSettings.json",
    "**/.pbi/cache.abf",
]

new_lines = []

for item in required:

    if item not in existing:
        new_lines.append(item)

if new_lines:

    with gitignore.open(
        "a",
        encoding="utf-8",
    ) as handle:

        if existing and not existing.endswith("\n"):
            handle.write("\n")

        handle.write(
            "\n".join(new_lines)
            + "\n"
        )


# ============================================================
# VALIDATION
# ============================================================

required_files = [
    POWERBI / f"{PROJECT_NAME}.pbip",

    REPORT_DIR
    / "definition.pbir",

    REPORT_DEFINITION
    / "version.json",

    REPORT_DEFINITION
    / "report.json",

    PAGES_DIR
    / "pages.json",

    SEMANTIC_DIR
    / "definition.pbism",

    MODEL_DEFINITION
    / "database.tmdl",

    MODEL_DEFINITION
    / "model.tmdl",
]


errors = []

for path in required_files:

    if not path.exists():

        errors.append(
            f"Missing: {path}"
        )


# Validate JSON files

json_files = list(
    REPORT_DIR.rglob("*.json")
)

json_files += list(
    SEMANTIC_DIR.rglob("*.json")
)

json_files += [
    POWERBI
    / f"{PROJECT_NAME}.pbip"
]

for path in json_files:

    try:

        json.loads(
            path.read_text(
                encoding="utf-8-sig"
            )
        )

    except Exception as exc:

        errors.append(
            f"Invalid JSON: "
            f"{path}: {exc}"
        )


# Check UTF-8 BOM

text_files = list(
    POWERBI.rglob("*.json")
)

text_files += list(
    POWERBI.rglob("*.pbip")
)

text_files += list(
    POWERBI.rglob("*.pbir")
)

text_files += list(
    POWERBI.rglob("*.pbism")
)

text_files += list(
    POWERBI.rglob("*.tmdl")
)

bom_files = []

for path in text_files:

    if path.read_bytes().startswith(
        b"\xef\xbb\xbf"
    ):
        bom_files.append(path)

if bom_files:

    for path in bom_files:

        errors.append(
            f"UTF-8 BOM detected: {path}"
        )


# ============================================================
# RESULT
# ============================================================

print()
print("=" * 72)
print("POWER BI SCAFFOLD VALIDATION")
print("=" * 72)

if errors:

    for error in errors:
        print(f"[ERROR] {error}")

    raise SystemExit(1)

print("[OK] PBIP shortcut")
print("[OK] PBIR report definition")
print("[OK] Five report pages")
print("[OK] TMDL semantic model")
print("[OK] Seven model tables")
print("[OK] JSON validation")
print("[OK] UTF-8 BOM validation")

print()
print(
    f"PBIP: "
    f"{POWERBI / (PROJECT_NAME + '.pbip')}"
)

print()
print("=" * 72)
print("STAGE 8C SCAFFOLD COMPLETE")
print("=" * 72)