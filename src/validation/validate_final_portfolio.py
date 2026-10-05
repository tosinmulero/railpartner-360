from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]

POWERBI = ROOT / "powerbi"

PBIP = POWERBI / "RailPartner_360.pbip"

REPORT = (
    POWERBI
    / "RailPartner_360.Report"
)

SEMANTIC = (
    POWERBI
    / "RailPartner_360.SemanticModel"
)

REPORT_DEFINITION = (
    REPORT
    / "definition"
)

MODEL_DEFINITION = (
    SEMANTIC
    / "definition"
)

PAGES_DIR = (
    REPORT_DEFINITION
    / "pages"
)

TABLES_DIR = (
    MODEL_DEFINITION
    / "tables"
)

EXPORT_DIR = (
    ROOT
    / "data"
    / "exports"
    / "stage7_business_analysis"
)


EXPECTED_PAGES = {
    "Executive Overview",
    "Partner Performance",
    "Customer & Conversion",
    "Routes & Operations",
    "Refund & Commercial Risk",
}


EXPECTED_TABLES = {
    "Executive KPIs.tmdl",
    "Partner Performance.tmdl",
    "Conversion Funnel.tmdl",
    "Customer Segments.tmdl",
    "Route Opportunity.tmdl",
    "Operator Performance.tmdl",
    "Refund Impact.tmdl",
}


EXPECTED_EXPORTS = {
    "01_executive_kpis.csv",
    "02_partner_opportunity.csv",
    "03_conversion_funnel.csv",
    "04_customer_segments.csv",
    "05_route_opportunity.csv",
    "06_operator_performance.csv",
    "07_refund_impact.csv",
}


errors = []
warnings = []


def ok(message):
    print(f"[OK] {message}")


def fail(message):
    errors.append(message)
    print(f"[ERROR] {message}")


print("=" * 76)
print("RAILPARTNER 360")
print("FINAL PORTFOLIO VALIDATION")
print("=" * 76)
print()


# ============================================================
# PBIP
# ============================================================

if PBIP.exists():
    ok("PBIP project exists")
else:
    fail("PBIP project missing")


# ============================================================
# SEMANTIC MODEL
# ============================================================

required_model_files = [
    SEMANTIC / "definition.pbism",
    MODEL_DEFINITION / "model.tmdl",
]

for path in required_model_files:

    if path.exists():
        ok(f"Semantic model file: {path.name}")
    else:
        fail(f"Missing semantic model file: {path}")


# ============================================================
# TABLES
# ============================================================

actual_tables = {
    p.name
    for p in TABLES_DIR.glob("*.tmdl")
}

missing_tables = (
    EXPECTED_TABLES
    - actual_tables
)

if missing_tables:

    for table in sorted(missing_tables):
        fail(f"Missing TMDL table: {table}")

else:
    ok("All seven semantic-model tables exist")


# ============================================================
# REPORT FILES
# ============================================================

required_report_files = [
    REPORT / "definition.pbir",
    REPORT_DEFINITION / "report.json",
    REPORT_DEFINITION / "version.json",
    PAGES_DIR / "pages.json",
]

for path in required_report_files:

    if path.exists():
        ok(f"Report file: {path.name}")
    else:
        fail(f"Missing report file: {path}")


# ============================================================
# PAGE VALIDATION
# ============================================================

page_names = set()
visual_count = 0

for folder in PAGES_DIR.iterdir():

    if not folder.is_dir():
        continue

    page_file = (
        folder
        / "page.json"
    )

    if not page_file.exists():
        continue

    try:

        page = json.loads(
            page_file.read_text(
                encoding="utf-8-sig"
            )
        )

    except Exception as exc:

        fail(
            f"Invalid page JSON: "
            f"{page_file}: {exc}"
        )

        continue

    display_name = page.get(
        "displayName"
    )

    if display_name:

        page_names.add(
            display_name
        )

    visuals_dir = (
        folder
        / "visuals"
    )

    if visuals_dir.exists():

        visuals = list(
            visuals_dir.glob(
                "*/visual.json"
            )
        )

        visual_count += len(
            visuals
        )

        print(
            f"[PAGE] "
            f"{display_name:<26} "
            f"{len(visuals):>2} visuals"
        )

        for visual_file in visuals:

            try:

                json.loads(
                    visual_file.read_text(
                        encoding="utf-8-sig"
                    )
                )

            except Exception as exc:

                fail(
                    f"Invalid visual JSON: "
                    f"{visual_file}: {exc}"
                )


missing_pages = (
    EXPECTED_PAGES
    - page_names
)

if missing_pages:

    for page in sorted(
        missing_pages
    ):
        fail(
            f"Missing report page: "
            f"{page}"
        )

else:
    ok("All five dashboard pages exist")


if visual_count > 0:

    ok(
        f"{visual_count} report visuals validated"
    )

else:

    fail(
        "No report visuals found"
    )


# ============================================================
# STAGE 7 EXPORTS
# ============================================================

actual_exports = {
    p.name
    for p in EXPORT_DIR.glob(
        "*.csv"
    )
}

missing_exports = (
    EXPECTED_EXPORTS
    - actual_exports
)

if missing_exports:

    for filename in sorted(
        missing_exports
    ):
        fail(
            f"Missing analytical export: "
            f"{filename}"
        )

else:

    ok(
        "All seven Stage 7 analytical exports exist"
    )


# ============================================================
# EXECUTIVE REPORT
# ============================================================

executive_report = (
    ROOT
    / "reports"
    / "executive"
    / "railpartner360_executive_analysis.md"
)

if executive_report.exists():

    ok(
        "Executive analysis report exists"
    )

else:

    fail(
        "Executive analysis report missing"
    )


# ============================================================
# BOM CHECK
# ============================================================

bom_files = []

extensions = {
    ".json",
    ".tmdl",
    ".pbip",
    ".pbir",
    ".pbism",
    ".py",
}

for path in ROOT.rglob("*"):

    if (
        path.is_file()
        and path.suffix.lower()
        in extensions
    ):

        try:

            if (
                path
                .read_bytes()
                .startswith(
                    b"\xef\xbb\xbf"
                )
            ):

                bom_files.append(
                    path
                )

        except OSError:
            pass


if bom_files:

    for path in bom_files:

        warnings.append(
            f"UTF-8 BOM: {path}"
        )

        print(
            f"[WARNING] UTF-8 BOM: "
            f"{path}"
        )

else:

    ok(
        "No UTF-8 BOM detected "
        "in project code/model files"
    )


# ============================================================
# FINAL RESULT
# ============================================================

print()
print("=" * 76)
print("VALIDATION SUMMARY")
print("=" * 76)

print(
    f"Pages:    "
    f"{len(page_names)}"
)

print(
    f"Visuals:  "
    f"{visual_count}"
)

print(
    f"Tables:   "
    f"{len(actual_tables)}"
)

print(
    f"Exports:  "
    f"{len(actual_exports)}"
)

print(
    f"Errors:   "
    f"{len(errors)}"
)

print(
    f"Warnings: "
    f"{len(warnings)}"
)

print()

if errors:

    print(
        "FINAL VALIDATION: FAILED"
    )

    sys.exit(1)

else:

    print(
        "FINAL VALIDATION: PASSED"
    )

    print()
    print(
        "RailPartner 360 is technically "
        "ready for the portfolio finishing pass."
    )

print("=" * 76)