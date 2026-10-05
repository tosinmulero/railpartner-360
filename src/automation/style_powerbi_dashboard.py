from __future__ import annotations

from pathlib import Path
import json
import shutil


# ============================================================
# RAILPARTNER 360
# STAGE 9B — GLOBAL POWER BI STYLING
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

REPORT_DEFINITION = (
    ROOT
    / "powerbi"
    / "RailPartner_360.Report"
    / "definition"
)

PAGES_DIR = REPORT_DEFINITION / "pages"

BACKUP_DIR = (
    ROOT
    / "powerbi"
    / "backups"
    / "stage9b_before_global_styling"
)


# ============================================================
# DESIGN SYSTEM
# ============================================================

NAVY = "#0F172A"
SLATE = "#475569"

BLUE = "#2563EB"
LIGHT_BLUE = "#EFF6FF"
BLUE_BORDER = "#BFDBFE"

CANVAS = "#F8FAFC"
OUTSPACE = "#E2E8F0"

WHITE = "#FFFFFF"
BORDER = "#E2E8F0"


# ============================================================
# PBIR EXPRESSION HELPERS
# ============================================================

def expr_bool(value: bool):

    return {
        "expr": {
            "Literal": {
                "Value":
                    "true"
                    if value
                    else "false"
            }
        }
    }


def expr_num(value):

    return {
        "expr": {
            "Literal": {
                "Value":
                    f"{value}D"
            }
        }
    }


def expr_string(value: str):

    return {
        "expr": {
            "Literal": {
                "Value":
                    f"'{value}'"
            }
        }
    }


def fill(color: str):

    return {
        "solid": {
            "color": {
                "expr": {
                    "Literal": {
                        "Value":
                            f"'{color}'"
                    }
                }
            }
        }
    }


# ============================================================
# JSON HELPERS
# ============================================================

def read_json(path: Path):

    return json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )


def write_json(path: Path, data):

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


# ============================================================
# BACKUP
# ============================================================

print("=" * 76)
print("RAILPARTNER 360 — STAGE 9B")
print("GLOBAL DASHBOARD STYLING")
print("=" * 76)
print()


if not BACKUP_DIR.exists():

    shutil.copytree(
        REPORT_DEFINITION,
        BACKUP_DIR,
    )

    print(
        "[OK] Pre-styling backup created"
    )

else:

    print(
        "[OK] Pre-styling backup already exists"
    )


# ============================================================
# PAGE BACKGROUND
# ============================================================

def style_page(page_file: Path):

    page = read_json(
        page_file
    )

    objects = page.setdefault(
        "objects",
        {},
    )

    objects["background"] = [
        {
            "properties": {

                "color":
                    fill(CANVAS),

                "transparency":
                    expr_num(0),
            }
        }
    ]

    objects["outspace"] = [
        {
            "properties": {

                "color":
                    fill(OUTSPACE),

                "transparency":
                    expr_num(0),
            }
        }
    ]

    write_json(
        page_file,
        page,
    )


# ============================================================
# STANDARD VISUAL CONTAINER
# ============================================================

def standard_container():

    return {

        "background": [
            {
                "properties": {

                    "show":
                        expr_bool(True),

                    "color":
                        fill(WHITE),

                    "transparency":
                        expr_num(0),
                }
            }
        ],

        "border": [
            {
                "properties": {

                    "show":
                        expr_bool(True),

                    "color":
                        fill(BORDER),

                    "radius":
                        expr_num(12),

                    "width":
                        expr_num(1),
                }
            }
        ],

        "padding": [
            {
                "properties": {

                    "top":
                        expr_num(10),

                    "bottom":
                        expr_num(10),

                    "left":
                        expr_num(12),

                    "right":
                        expr_num(12),
                }
            }
        ],

        "visualHeader": [
            {
                "properties": {

                    "show":
                        expr_bool(False),
                }
            }
        ],

        "subTitle": [
            {
                "properties": {

                    "show":
                        expr_bool(False),
                }
            }
        ],
    }


# ============================================================
# HEADER TEXTBOX CONTAINER
# ============================================================

def transparent_container():

    return {

        "background": [
            {
                "properties": {

                    "show":
                        expr_bool(False),
                }
            }
        ],

        "border": [
            {
                "properties": {

                    "show":
                        expr_bool(False),
                }
            }
        ],

        "padding": [
            {
                "properties": {

                    "top":
                        expr_num(0),

                    "bottom":
                        expr_num(0),

                    "left":
                        expr_num(0),

                    "right":
                        expr_num(0),
                }
            }
        ],

        "visualHeader": [
            {
                "properties": {

                    "show":
                        expr_bool(False),
                }
            }
        ],
    }


# ============================================================
# INSIGHT CALLOUT
# ============================================================

def insight_container():

    return {

        "background": [
            {
                "properties": {

                    "show":
                        expr_bool(True),

                    "color":
                        fill(LIGHT_BLUE),

                    "transparency":
                        expr_num(0),
                }
            }
        ],

        "border": [
            {
                "properties": {

                    "show":
                        expr_bool(True),

                    "color":
                        fill(BLUE_BORDER),

                    "radius":
                        expr_num(12),

                    "width":
                        expr_num(1),
                }
            }
        ],

        "padding": [
            {
                "properties": {

                    "top":
                        expr_num(12),

                    "bottom":
                        expr_num(12),

                    "left":
                        expr_num(14),

                    "right":
                        expr_num(14),
                }
            }
        ],

        "visualHeader": [
            {
                "properties": {

                    "show":
                        expr_bool(False),
                }
            }
        ],
    }


# ============================================================
# STYLE CHART TITLE
# ============================================================

def style_existing_title(vco):

    title_entries = vco.get(
        "title"
    )

    if not title_entries:
        return

    for entry in title_entries:

        props = entry.setdefault(
            "properties",
            {},
        )

        props["show"] = (
            expr_bool(True)
        )

        props["fontColor"] = (
            fill(NAVY)
        )

        props["fontSize"] = (
            expr_num(14)
        )

        props["fontFamily"] = (
            expr_string(
                "Segoe UI Semibold"
            )
        )

        props["bold"] = (
            expr_bool(True)
        )


# ============================================================
# STYLE TEXTBOX CONTENT
# ============================================================

def style_textbox_text(
    visual,
    position,
):

    objects = (
        visual
        .get("objects", {})
    )

    general = objects.get(
        "general",
        [],
    )

    y = position.get(
        "y",
        9999,
    )

    for item in general:

        paragraphs = (
            item
            .get("properties", {})
            .get(
                "paragraphs",
                [],
            )
        )

        for paragraph in paragraphs:

            runs = paragraph.get(
                "textRuns",
                [],
            )

            for run in runs:

                style = run.setdefault(
                    "textStyle",
                    {},
                )

                if y < 75:

                    style[
                        "fontFamily"
                    ] = (
                        "Segoe UI Semibold"
                    )

                    style[
                        "color"
                    ] = NAVY

                elif y < 150:

                    style[
                        "fontFamily"
                    ] = (
                        "Segoe UI"
                    )

                    style[
                        "color"
                    ] = SLATE

                else:

                    style[
                        "fontFamily"
                    ] = (
                        "Segoe UI"
                    )

                    style[
                        "color"
                    ] = NAVY


# ============================================================
# STYLE VISUAL
# ============================================================

def style_visual(
    visual_file: Path,
):

    data = read_json(
        visual_file
    )

    visual = data.get(
        "visual",
        {},
    )

    visual_type = visual.get(
        "visualType",
        "",
    )

    position = data.get(
        "position",
        {},
    )

    y = position.get(
        "y",
        9999,
    )

    existing_vco = (
        visual.setdefault(
            "visualContainerObjects",
            {},
        )
    )


    # --------------------------------------------------------
    # TEXTBOX
    # --------------------------------------------------------

    if visual_type == "textbox":

        style_textbox_text(
            visual,
            position,
        )

        if y < 160:

            replacement = (
                transparent_container()
            )

        else:

            replacement = (
                insight_container()
            )

        existing_vco.update(
            replacement
        )

        write_json(
            visual_file,
            data,
        )

        return


    # --------------------------------------------------------
    # CHART / TABLE / CARD
    # --------------------------------------------------------

    replacement = (
        standard_container()
    )

    existing_vco.update(
        replacement
    )

    style_existing_title(
        existing_vco
    )


    # --------------------------------------------------------
    # TABLES
    # --------------------------------------------------------

    if visual_type == "tableEx":

        existing_vco[
            "stylePreset"
        ] = [
            {
                "properties": {

                    "name":
                        expr_string(
                            "None"
                        )
                }
            }
        ]


    write_json(
        visual_file,
        data,
    )


# ============================================================
# PROCESS REPORT
# ============================================================

page_count = 0
visual_count = 0


for page_folder in PAGES_DIR.iterdir():

    if not page_folder.is_dir():
        continue

    page_file = (
        page_folder
        / "page.json"
    )

    if not page_file.exists():
        continue

    style_page(
        page_file
    )

    page_count += 1

    visuals_dir = (
        page_folder
        / "visuals"
    )

    if not visuals_dir.exists():
        continue

    for visual_file in (
        visuals_dir.glob(
            "*/visual.json"
        )
    ):

        style_visual(
            visual_file
        )

        visual_count += 1


# ============================================================
# JSON VALIDATION
# ============================================================

for page_folder in PAGES_DIR.iterdir():

    if not page_folder.is_dir():
        continue

    page_file = (
        page_folder
        / "page.json"
    )

    if page_file.exists():

        read_json(
            page_file
        )

    visuals_dir = (
        page_folder
        / "visuals"
    )

    if visuals_dir.exists():

        for visual_file in (
            visuals_dir.glob(
                "*/visual.json"
            )
        ):

            read_json(
                visual_file
            )


print()
print("=" * 76)
print("STAGE 9B VALIDATION")
print("=" * 76)

print(
    f"[OK] Pages styled: {page_count}"
)

print(
    f"[OK] Visuals styled: {visual_count}"
)

print(
    "[OK] Light-grey report canvas applied"
)

print(
    "[OK] White professional visual cards applied"
)

print(
    "[OK] Rounded borders applied"
)

print(
    "[OK] Chart titles standardised"
)

print(
    "[OK] Page titles and subtitles standardised"
)

print(
    "[OK] Executive insight callout styled"
)

print(
    "[OK] Table style presets normalised"
)

print(
    "[OK] PBIR JSON validated"
)

print()
print("=" * 76)
print("STAGE 9B COMPLETE")
print("=" * 76)