from __future__ import annotations

from pathlib import Path
import hashlib
import json
import shutil


# ============================================================
# RAILPARTNER 360
# STAGE 8F-1 — EXECUTIVE OVERVIEW
# TITLE + SIX KPI CARDS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

REPORT_DIR = (
    ROOT
    / "powerbi"
    / "RailPartner_360.Report"
    / "definition"
)

PAGES_DIR = REPORT_DIR / "pages"

BACKUP_DIR = (
    ROOT
    / "powerbi"
    / "backups"
    / "stage8f_before_executive_visuals"
)

VISUAL_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/"
    "fabric/item/report/definition/"
    "visualContainer/2.9.0/schema.json"
)


# ============================================================
# HELPERS
# ============================================================

def write_json(path: Path, data: dict) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def visual_id(key: str) -> str:

    return hashlib.sha1(
        (
            "railpartner360::"
            + key
        ).encode("utf-8")
    ).hexdigest()[:20]


def find_page(display_name: str) -> Path:

    for folder in PAGES_DIR.iterdir():

        if not folder.is_dir():
            continue

        page_file = (
            folder
            / "page.json"
        )

        if not page_file.exists():
            continue

        page = json.loads(
            page_file.read_text(
                encoding="utf-8-sig"
            )
        )

        if (
            page.get("displayName")
            == display_name
        ):
            return folder

    raise RuntimeError(
        f"Page not found: {display_name}"
    )


def measure_expression(
    table: str,
    measure: str,
) -> dict:

    return {
        "Measure": {
            "Expression": {
                "SourceRef": {
                    "Entity": table
                }
            },
            "Property": measure,
        }
    }


def create_textbox(
    key: str,
    text: str,
    x: int,
    y: int,
    width: int,
    height: int,
    font_size: int,
    bold: bool = False,
) -> dict:

    name = visual_id(key)

    return {
        "$schema": VISUAL_SCHEMA,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": 1000,
            "height": height,
            "width": width,
            "tabOrder": 0,
        },
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {
                                            "value": text,
                                            "textStyle": {
                                                "fontFamily":
                                                    "Segoe UI",
                                                "fontSize":
                                                    f"{font_size}pt",
                                                "fontWeight":
                                                    (
                                                        "bold"
                                                        if bold
                                                        else "normal"
                                                    ),
                                                "color":
                                                    "#0F172A",
                                            },
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            },
        },
    }


def create_card(
    key: str,
    measure: str,
    x: int,
    y: int,
    width: int,
    height: int,
    z: int,
) -> dict:

    name = visual_id(key)

    field = measure_expression(
        "Executive KPIs",
        measure,
    )

    return {
        "$schema": VISUAL_SCHEMA,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "height": height,
            "width": width,
            "tabOrder": z,
        },
        "visual": {
            "visualType": "cardVisual",
            "query": {
                "queryState": {
                    "Data": {
                        "projections": [
                            {
                                "field": field,
                                "queryRef":
                                    f"Executive KPIs.{measure}",
                                "nativeQueryRef":
                                    measure,
                            }
                        ]
                    }
                }
            },
        },
    }


# ============================================================
# START
# ============================================================

print("=" * 76)
print("RAILPARTNER 360 — STAGE 8F-1")
print("EXECUTIVE OVERVIEW KPI BUILD")
print("=" * 76)


# ============================================================
# FIND EXECUTIVE PAGE
# ============================================================

page_folder = find_page(
    "Executive Overview"
)

visuals_dir = (
    page_folder
    / "visuals"
)

visuals_dir.mkdir(
    parents=True,
    exist_ok=True,
)

print()
print(
    "[OK] Executive Overview page:"
    f" {page_folder.name}"
)


# ============================================================
# BACKUP CURRENT REPORT
# ============================================================

if not BACKUP_DIR.exists():

    shutil.copytree(
        REPORT_DIR,
        BACKUP_DIR,
    )

    print(
        "[OK] Stage 8F backup created"
    )

else:

    print(
        "[OK] Stage 8F backup already exists"
    )


# ============================================================
# CLEAR EXECUTIVE PAGE VISUALS ONLY
# ============================================================

for child in visuals_dir.iterdir():

    if child.is_dir():

        shutil.rmtree(
            child
        )

    else:

        child.unlink()


# ============================================================
# TITLE
# ============================================================

title = create_textbox(
    key="overview-title",
    text="RailPartner 360",
    x=55,
    y=28,
    width=700,
    height=65,
    font_size=26,
    bold=True,
)

subtitle = create_textbox(
    key="overview-subtitle",
    text=(
        "Executive Commercial & "
        "Partner Intelligence"
    ),
    x=55,
    y=88,
    width=900,
    height=50,
    font_size=13,
    bold=False,
)


# ============================================================
# KPI CARDS
# ============================================================

cards = [
    (
        "card-searches",
        "Total Searches",
    ),
    (
        "card-bookings",
        "Total Bookings",
    ),
    (
        "card-conversion",
        "Conversion Rate %",
    ),
    (
        "card-gbv",
        "Gross Booking Value",
    ),
    (
        "card-revenue",
        "Platform Revenue",
    ),
    (
        "card-b2b",
        "B2B Booking Share %",
    ),
]


# 1920px canvas
left = 55
gap = 18
card_width = 286
card_height = 150
card_y = 175


visuals = [
    title,
    subtitle,
]


for index, (
    key,
    measure,
) in enumerate(cards):

    x = (
        left
        + index
        * (
            card_width
            + gap
        )
    )

    card = create_card(
        key=key,
        measure=measure,
        x=x,
        y=card_y,
        width=card_width,
        height=card_height,
        z=2000 + index,
    )

    visuals.append(
        card
    )


# ============================================================
# WRITE VISUAL FILES
# ============================================================

for visual in visuals:

    name = visual["name"]

    folder = (
        visuals_dir
        / name
    )

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_json(
        folder
        / "visual.json",
        visual,
    )


# ============================================================
# VALIDATION
# ============================================================

created = list(
    visuals_dir.glob(
        "*/visual.json"
    )
)

if len(created) != 8:

    raise RuntimeError(
        "Expected 8 visuals "
        f"but found {len(created)}"
    )


for file in created:

    data = json.loads(
        file.read_text(
            encoding="utf-8"
        )
    )

    if (
        data.get("$schema")
        != VISUAL_SCHEMA
    ):

        raise RuntimeError(
            f"Schema mismatch: {file}"
        )


print()
print("=" * 76)
print("STAGE 8F-1 VALIDATION")
print("=" * 76)

print("[OK] Executive Overview located")
print("[OK] Page title created")
print("[OK] Subtitle created")
print("[OK] Six KPI cards created")
print("[OK] cardVisual Data roles configured")
print("[OK] PBIR visual schema 2.9.0")
print("[OK] JSON files validated")

print()
print("=" * 76)
print("STAGE 8F-1 COMPLETE")
print("=" * 76)