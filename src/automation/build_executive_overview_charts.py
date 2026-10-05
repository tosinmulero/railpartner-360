from __future__ import annotations

from pathlib import Path
import hashlib
import json
import shutil


# ============================================================
# RAILPARTNER 360
# STAGE 8G-1 — PARTNER PERFORMANCE
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

PAGES_DIR = (
    ROOT
    / "powerbi"
    / "RailPartner_360.Report"
    / "definition"
    / "pages"
)

BACKUP_DIR = (
    ROOT
    / "powerbi"
    / "backups"
    / "stage8g_before_partner_visuals"
)

SCHEMA = (
    "https://developer.microsoft.com/json-schemas/"
    "fabric/item/report/definition/"
    "visualContainer/2.9.0/schema.json"
)


# ============================================================
# HELPERS
# ============================================================

def write_json(path: Path, data: dict):

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


def vid(key: str) -> str:

    return hashlib.sha1(
        (
            "railpartner360::partner::"
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

        data = json.loads(
            page_file.read_text(
                encoding="utf-8-sig"
            )
        )

        if (
            data.get("displayName")
            == display_name
        ):
            return folder

    raise RuntimeError(
        f"Page not found: {display_name}"
    )


def measure(
    table: str,
    field: str,
):

    return {
        "Measure": {
            "Expression": {
                "SourceRef": {
                    "Entity": table
                }
            },
            "Property": field,
        }
    }


def column(
    table: str,
    field: str,
):

    return {
        "Column": {
            "Expression": {
                "SourceRef": {
                    "Entity": table
                }
            },
            "Property": field,
        }
    }


def aggregation(
    table: str,
    field: str,
    function: int = 0,
):

    return {
        "Aggregation": {
            "Expression": column(
                table,
                field,
            ),
            "Function": function,
        }
    }


# ============================================================
# TEXTBOX
# ============================================================

def create_textbox(
    key,
    text,
    x,
    y,
    width,
    height,
    size,
    bold=False,
):

    name = vid(key)

    return {
        "$schema": SCHEMA,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": 1000,
            "height": height,
            "width": width,
            "tabOrder": 1000,
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
                                                    f"{size}pt",
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


# ============================================================
# CARD
# ============================================================

def create_card(
    key,
    measure_name,
    x,
    y,
    width,
    height,
    z,
):

    field = measure(
        "Partner Performance",
        measure_name,
    )

    return {
        "$schema": SCHEMA,
        "name": vid(key),
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
                                    f"Partner Performance.{measure_name}",
                                "nativeQueryRef":
                                    measure_name,
                            }
                        ]
                    }
                }
            },
        },
        "filterConfig": {
            "filters": []
        },
    }


# ============================================================
# BAR CHART
# ============================================================

def create_bar_chart(
    key,
    title,
    value_field,
    x,
    y,
    width,
    height,
    z,
):

    category = column(
        "Partner Performance",
        "partner_name",
    )

    value = aggregation(
        "Partner Performance",
        value_field,
        0,
    )

    return {
        "$schema": SCHEMA,
        "name": vid(key),
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "height": height,
            "width": width,
            "tabOrder": z,
        },
        "visual": {
            "visualType":
                "clusteredBarChart",

            "query": {
                "queryState": {

                    "Category": {
                        "projections": [
                            {
                                "field":
                                    category,
                                "queryRef":
                                    "Partner Performance.partner_name",
                                "nativeQueryRef":
                                    "partner_name",
                                "active": True,
                            }
                        ]
                    },

                    "Y": {
                        "projections": [
                            {
                                "field":
                                    value,
                                "queryRef":
                                    f"Sum(Partner Performance.{value_field})",
                                "nativeQueryRef":
                                    value_field,
                            }
                        ]
                    },
                },

                "sortDefinition": {
                    "sort": [
                        {
                            "field":
                                value,
                            "direction":
                                "Descending",
                        }
                    ],
                    "isDefaultSort":
                        True,
                },
            },

            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value":
                                            "true"
                                    }
                                }
                            },

                            "text": {
                                "expr": {
                                    "Literal": {
                                        "Value":
                                            f"'{title}'"
                                    }
                                }
                            },

                            "fontSize": {
                                "expr": {
                                    "Literal": {
                                        "Value":
                                            "15D"
                                    }
                                }
                            },

                            "bold": {
                                "expr": {
                                    "Literal": {
                                        "Value":
                                            "true"
                                    }
                                }
                            },
                        }
                    }
                ]
            },

            "drillFilterOtherVisuals":
                True,
        },

        "filterConfig": {
            "filters": []
        },
    }


# ============================================================
# START
# ============================================================

print("=" * 76)
print("RAILPARTNER 360 — STAGE 8G-1")
print("PARTNER PERFORMANCE BUILD")
print("=" * 76)


page = find_page(
    "Partner Performance"
)

visuals_dir = (
    page
    / "visuals"
)

visuals_dir.mkdir(
    parents=True,
    exist_ok=True,
)

print()
print(
    "[OK] Partner Performance page:"
    f" {page.name}"
)


# ============================================================
# BACKUP
# ============================================================

report_definition = (
    ROOT
    / "powerbi"
    / "RailPartner_360.Report"
    / "definition"
)

if not BACKUP_DIR.exists():

    shutil.copytree(
        report_definition,
        BACKUP_DIR,
    )

    print(
        "[OK] Stage 8G backup created"
    )

else:

    print(
        "[OK] Stage 8G backup already exists"
    )


# ============================================================
# CLEAR ONLY THIS PAGE
# ============================================================

for child in list(
    visuals_dir.iterdir()
):

    if child.is_dir():

        shutil.rmtree(
            child
        )

    else:

        child.unlink()


# ============================================================
# TITLE
# ============================================================

visuals = [
    create_textbox(
        "title",
        "Partner Performance",
        55,
        28,
        750,
        65,
        26,
        True,
    ),

    create_textbox(
        "subtitle",
        (
            "B2B partner contribution, "
            "conversion, revenue and commercial risk"
        ),
        55,
        88,
        1100,
        45,
        13,
        False,
    ),
]


# ============================================================
# KPI CARDS
# ============================================================

card_specs = [
    (
        "partners",
        "Partner Count",
    ),
    (
        "revenue",
        "Partner Revenue",
    ),
    (
        "bookings",
        "Partner Bookings",
    ),
    (
        "conversion",
        "Average Partner Conversion %",
    ),
    (
        "risk",
        "Partner Value at Risk",
    ),
]


left = 55
gap = 20
card_width = 350
card_height = 155
card_y = 165


for index, (
    key,
    measure_name,
) in enumerate(
    card_specs
):

    x = (
        left
        + index
        * (
            card_width
            + gap
        )
    )

    visuals.append(
        create_card(
            key=f"card-{key}",
            measure_name=
                measure_name,
            x=x,
            y=card_y,
            width=card_width,
            height=card_height,
            z=2000 + index,
        )
    )


# ============================================================
# CHARTS
# ============================================================

visuals.append(
    create_bar_chart(
        key="revenue-ranking",
        title="Partner Revenue Ranking",
        value_field=
            "platform_revenue_gbp",
        x=55,
        y=385,
        width=885,
        height=610,
        z=4000,
    )
)

visuals.append(
    create_bar_chart(
        key="risk-ranking",
        title="Commercial Value at Risk by Partner",
        value_field=
            "commercial_value_at_risk_gbp",
        x=980,
        y=385,
        width=885,
        height=610,
        z=5000,
    )
)


# ============================================================
# WRITE FILES
# ============================================================

for visual in visuals:

    folder = (
        visuals_dir
        / visual["name"]
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

expected = 9

if len(created) != expected:

    raise RuntimeError(
        f"Expected {expected} visuals "
        f"but found {len(created)}"
    )


for file in created:

    json.loads(
        file.read_text(
            encoding="utf-8"
        )
    )


print()
print("=" * 76)
print("STAGE 8G-1 VALIDATION")
print("=" * 76)

print(
    "[OK] Partner page located"
)

print(
    "[OK] Title and subtitle created"
)

print(
    "[OK] Five partner KPI cards created"
)

print(
    "[OK] Revenue ranking chart created"
)

print(
    "[OK] Commercial-risk ranking created"
)

print(
    "[OK] Nine PBIR visual files validated"
)

print()
print("=" * 76)
print("STAGE 8G-1 COMPLETE")
print("=" * 76)