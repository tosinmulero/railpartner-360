from __future__ import annotations

from pathlib import Path
import hashlib
import json
import shutil


# ============================================================
# RAILPARTNER 360
# STAGE 9C — COLOUR HIERARCHY + PAGE NAVIGATION
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

REPORT_DEFINITION = (
    ROOT
    / "powerbi"
    / "RailPartner_360.Report"
    / "definition"
)

PAGES_DIR = (
    REPORT_DEFINITION
    / "pages"
)

BACKUP_DIR = (
    ROOT
    / "powerbi"
    / "backups"
    / "stage9c_before_navigation"
)

VISUAL_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/"
    "fabric/item/report/definition/"
    "visualContainer/2.9.0/schema.json"
)


# ============================================================
# PAGE COLOUR SYSTEM
# ============================================================

PAGE_STYLES = {

    "Executive Overview": {
        "accent": "#2563EB",
        "tint": "#EFF6FF",
        "border": "#BFDBFE",
    },

    "Partner Performance": {
        "accent": "#0F9F82",
        "tint": "#ECFDF5",
        "border": "#A7F3D0",
    },

    "Customer & Conversion": {
        "accent": "#7C3AED",
        "tint": "#F5F3FF",
        "border": "#DDD6FE",
    },

    "Routes & Operations": {
        "accent": "#D97706",
        "tint": "#FFFBEB",
        "border": "#FDE68A",
    },

    "Refund & Commercial Risk": {
        "accent": "#DC2626",
        "tint": "#FEF2F2",
        "border": "#FECACA",
    },
}


NAVY = "#0F172A"
WHITE = "#FFFFFF"
SLATE = "#475569"


# ============================================================
# HELPERS
# ============================================================

def read_json(path: Path):

    return json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )


def write_json(path: Path, data):

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
                "Value": f"{value}D"
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


def nav_id(page_id: str):

    return hashlib.sha1(
        (
            "railpartner360::navigation::"
            + page_id
        ).encode("utf-8")
    ).hexdigest()[:20]


# ============================================================
# BACKUP
# ============================================================

print("=" * 76)
print("RAILPARTNER 360 — STAGE 9C")
print("COLOUR HIERARCHY + NAVIGATION")
print("=" * 76)
print()


if not BACKUP_DIR.exists():

    shutil.copytree(
        REPORT_DEFINITION,
        BACKUP_DIR,
    )

    print(
        "[OK] Stage 9C backup created"
    )

else:

    print(
        "[OK] Stage 9C backup already exists"
    )


# ============================================================
# TEXTBOX COLOUR
# ============================================================

def style_textbox(
    visual: dict,
    position: dict,
    accent: str,
):

    y = position.get(
        "y",
        9999,
    )

    general = (
        visual
        .get("objects", {})
        .get("general", [])
    )

    for item in general:

        paragraphs = (
            item
            .get("properties", {})
            .get("paragraphs", [])
        )

        for paragraph in paragraphs:

            runs = paragraph.get(
                "textRuns",
                []
            )

            for run in runs:

                style = run.setdefault(
                    "textStyle",
                    {}
                )

                if y < 80:

                    style["color"] = accent

                    style[
                        "fontFamily"
                    ] = (
                        "Segoe UI Semibold"
                    )

                elif y < 150:

                    style["color"] = SLATE

                else:

                    style["color"] = NAVY


# ============================================================
# CARD COLOUR
# ============================================================

def style_card(
    visual: dict,
    tint: str,
    border: str,
):

    vco = visual.setdefault(
        "visualContainerObjects",
        {}
    )

    vco["background"] = [
        {
            "properties": {

                "show":
                    expr_bool(True),

                "color":
                    fill(tint),

                "transparency":
                    expr_num(0),
            }
        }
    ]

    vco["border"] = [
        {
            "properties": {

                "show":
                    expr_bool(True),

                "color":
                    fill(border),

                "width":
                    expr_num(1),

                "radius":
                    expr_num(14),
            }
        }
    ]


# ============================================================
# CHART / TABLE ACCENT
# ============================================================

def style_analytical_visual(
    visual: dict,
    border: str,
):

    vco = visual.setdefault(
        "visualContainerObjects",
        {}
    )

    vco["background"] = [
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
    ]

    vco["border"] = [
        {
            "properties": {

                "show":
                    expr_bool(True),

                "color":
                    fill(border),

                "width":
                    expr_num(1),

                "radius":
                    expr_num(12),
            }
        }
    ]


# ============================================================
# PAGE NAVIGATOR
# ============================================================

def create_page_navigator(
    page_id: str,
):

    name = nav_id(
        page_id
    )

    return {

        "$schema":
            VISUAL_SCHEMA,

        "name":
            name,

        "position": {

            "x": 55,
            "y": 1040,

            "z": 20000,

            "height": 32,
            "width": 1810,

            "tabOrder": 20000,
        },

        "visual": {

            "visualType":
                "pageNavigator",

            "visualContainerObjects": {

                "title": [
                    {
                        "properties": {
                            "show":
                                expr_bool(False)
                        }
                    }
                ],

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
                                fill("#E2E8F0"),

                            "width":
                                expr_num(1),

                            "radius":
                                expr_num(10),
                        }
                    }
                ],

                "visualHeader": [
                    {
                        "properties": {
                            "show":
                                expr_bool(False)
                        }
                    }
                ],

                "padding": [
                    {
                        "properties": {

                            "top":
                                expr_num(2),

                            "bottom":
                                expr_num(2),

                            "left":
                                expr_num(4),

                            "right":
                                expr_num(4),
                        }
                    }
                ],
            },
        },

        "filterConfig": {
            "filters": []
        },
    }


# ============================================================
# PROCESS PAGES
# ============================================================

page_count = 0
styled_visuals = 0
navigators = 0


for page_folder in PAGES_DIR.iterdir():

    if not page_folder.is_dir():
        continue

    page_file = (
        page_folder
        / "page.json"
    )

    if not page_file.exists():
        continue

    page = read_json(
        page_file
    )

    page_name = page.get(
        "displayName"
    )

    if page_name not in PAGE_STYLES:

        print(
            f"[SKIP] Unknown page: {page_name}"
        )

        continue

    style = PAGE_STYLES[
        page_name
    ]

    accent = style[
        "accent"
    ]

    tint = style[
        "tint"
    ]

    border = style[
        "border"
    ]

    page_id = page.get(
        "name",
        page_folder.name,
    )

    visuals_dir = (
        page_folder
        / "visuals"
    )

    visuals_dir.mkdir(
        parents=True,
        exist_ok=True,
    )


    # --------------------------------------------------------
    # STYLE EXISTING VISUALS
    # --------------------------------------------------------

    for visual_file in (
        visuals_dir.glob(
            "*/visual.json"
        )
    ):

        data = read_json(
            visual_file
        )

        visual = data.get(
            "visual",
            {}
        )

        visual_type = visual.get(
            "visualType",
            ""
        )

        position = data.get(
            "position",
            {}
        )


        if visual_type == "textbox":

            style_textbox(
                visual,
                position,
                accent,
            )


        elif visual_type == "cardVisual":

            style_card(
                visual,
                tint,
                border,
            )


        elif visual_type in {

            "clusteredBarChart",
            "stackedBarChart",
            "scatterChart",
            "tableEx",

        }:

            style_analytical_visual(
                visual,
                border,
            )


        write_json(
            visual_file,
            data,
        )

        styled_visuals += 1


    # --------------------------------------------------------
    # CREATE NAVIGATION
    # --------------------------------------------------------

    navigator = (
        create_page_navigator(
            page_id
        )
    )

    navigator_file = (
        visuals_dir
        / navigator["name"]
        / "visual.json"
    )

    write_json(
        navigator_file,
        navigator,
    )

    navigators += 1
    page_count += 1

    print(
        f"[OK] Finished: {page_name}"
    )


# ============================================================
# VALIDATION
# ============================================================

navigation_count = 0

for page_folder in PAGES_DIR.iterdir():

    if not page_folder.is_dir():
        continue

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

        data = read_json(
            visual_file
        )

        visual_type = (
            data
            .get("visual", {})
            .get("visualType")
        )

        if visual_type == "pageNavigator":

            navigation_count += 1


if navigation_count != 5:

    raise RuntimeError(
        "Expected 5 page navigators, "
        f"found {navigation_count}"
    )


print()
print("=" * 76)
print("STAGE 9C VALIDATION")
print("=" * 76)

print(
    f"[OK] Pages finished: {page_count}"
)

print(
    f"[OK] Existing visuals processed: "
    f"{styled_visuals}"
)

print(
    f"[OK] Page navigators created: "
    f"{navigation_count}"
)

print(
    "[OK] Executive page accent: Blue"
)

print(
    "[OK] Partner page accent: Teal"
)

print(
    "[OK] Customer page accent: Purple"
)

print(
    "[OK] Operations page accent: Amber"
)

print(
    "[OK] Commercial-risk page accent: Red"
)

print()
print("=" * 76)
print("STAGE 9C COMPLETE")
print("=" * 76)