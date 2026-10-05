from __future__ import annotations

from pathlib import Path
import hashlib
import json


# ============================================================
# RAILPARTNER 360
# STAGE 8J — REFUND & COMMERCIAL RISK
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

PAGES_DIR = (
    ROOT
    / "powerbi"
    / "RailPartner_360.Report"
    / "definition"
    / "pages"
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
            "railpartner360::refund::"
            + key
        ).encode("utf-8")
    ).hexdigest()[:20]


def find_page(display_name: str) -> Path:

    for folder in PAGES_DIR.iterdir():

        if not folder.is_dir():
            continue

        page_file = folder / "page.json"

        if not page_file.exists():
            continue

        data = json.loads(
            page_file.read_text(
                encoding="utf-8-sig"
            )
        )

        if data.get("displayName") == display_name:
            return folder

    raise RuntimeError(
        f"Page not found: {display_name}"
    )


def column(table: str, field: str):

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


def measure(table: str, field: str):

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


def aggregation(
    table: str,
    field: str,
    function: int,
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


def title_object(text: str):

    return {
        "title": [
            {
                "properties": {

                    "show": {
                        "expr": {
                            "Literal": {
                                "Value": "true"
                            }
                        }
                    },

                    "text": {
                        "expr": {
                            "Literal": {
                                "Value":
                                    f"'{text}'"
                            }
                        }
                    },

                    "fontSize": {
                        "expr": {
                            "Literal": {
                                "Value": "14D"
                            }
                        }
                    },

                    "bold": {
                        "expr": {
                            "Literal": {
                                "Value": "true"
                            }
                        }
                    },
                }
            }
        ]
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

    return {
        "$schema": SCHEMA,

        "name": vid(key),

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
# KPI CARD
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
        "Refund Impact",
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

            "visualType":
                "cardVisual",

            "query": {

                "queryState": {

                    "Data": {

                        "projections": [
                            {
                                "field":
                                    field,

                                "queryRef":
                                    f"Refund Impact.{measure_name}",

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
# RISK BY REFUND REASON
# ============================================================

def risk_reason_chart():

    reason = column(
        "Refund Impact",
        "refund_reason",
    )

    risk = aggregation(
        "Refund Impact",
        "commercial_value_at_risk_gbp",
        0,
    )

    return {

        "$schema": SCHEMA,

        "name": vid(
            "risk-by-reason"
        ),

        "position": {
            "x": 55,
            "y": 360,
            "z": 4000,
            "height": 340,
            "width": 885,
            "tabOrder": 4000,
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
                                    reason,

                                "queryRef":
                                    "Refund Impact.refund_reason",

                                "nativeQueryRef":
                                    "refund_reason",

                                "active": True,
                            }
                        ]
                    },

                    "Y": {
                        "projections": [
                            {
                                "field":
                                    risk,

                                "queryRef":
                                    "Sum(Refund Impact.commercial_value_at_risk_gbp)",

                                "nativeQueryRef":
                                    "commercial_value_at_risk_gbp",
                            }
                        ]
                    },
                },

                "sortDefinition": {

                    "sort": [
                        {
                            "field":
                                risk,

                            "direction":
                                "Descending",
                        }
                    ],

                    "isDefaultSort":
                        True,
                },
            },

            "visualContainerObjects":
                title_object(
                    "Commercial Value at Risk by Refund Reason"
                ),

            "drillFilterOtherVisuals":
                True,
        },

        "filterConfig": {
            "filters": []
        },
    }


# ============================================================
# REFUND TYPE / CHANNEL
# ============================================================

def refund_channel_chart():

    refund_type = column(
        "Refund Impact",
        "refund_type",
    )

    refund_amount = aggregation(
        "Refund Impact",
        "refund_amount_gbp",
        0,
    )

    channel = column(
        "Refund Impact",
        "sales_channel",
    )

    return {

        "$schema": SCHEMA,

        "name": vid(
            "refund-channel"
        ),

        "position": {
            "x": 980,
            "y": 360,
            "z": 5000,
            "height": 340,
            "width": 885,
            "tabOrder": 5000,
        },

        "visual": {

            "visualType":
                "stackedBarChart",

            "query": {

                "queryState": {

                    "Category": {
                        "projections": [
                            {
                                "field":
                                    refund_type,

                                "queryRef":
                                    "Refund Impact.refund_type",

                                "nativeQueryRef":
                                    "refund_type",

                                "active": True,
                            }
                        ]
                    },

                    "Y": {
                        "projections": [
                            {
                                "field":
                                    refund_amount,

                                "queryRef":
                                    "Sum(Refund Impact.refund_amount_gbp)",

                                "nativeQueryRef":
                                    "refund_amount_gbp",
                            }
                        ]
                    },

                    "Series": {
                        "projections": [
                            {
                                "field":
                                    channel,

                                "queryRef":
                                    "Refund Impact.sales_channel",

                                "nativeQueryRef":
                                    "sales_channel",

                                "active": True,
                            }
                        ]
                    },
                }
            },

            "visualContainerObjects":
                title_object(
                    "Refund Exposure by Type and Channel"
                ),

            "drillFilterOtherVisuals":
                True,
        },

        "filterConfig": {
            "filters": []
        },
    }


# ============================================================
# PROCESSING VS EXPOSURE SCATTER
# ============================================================

def processing_scatter():

    reason = column(
        "Refund Impact",
        "refund_reason",
    )

    processing = aggregation(
        "Refund Impact",
        "average_processing_days",
        1,
    )

    risk = aggregation(
        "Refund Impact",
        "commercial_value_at_risk_gbp",
        0,
    )

    records = aggregation(
        "Refund Impact",
        "refund_records",
        0,
    )

    refund_type = column(
        "Refund Impact",
        "refund_type",
    )

    return {

        "$schema": SCHEMA,

        "name": vid(
            "processing-risk-scatter"
        ),

        "position": {
            "x": 55,
            "y": 735,
            "z": 6000,
            "height": 290,
            "width": 725,
            "tabOrder": 6000,
        },

        "visual": {

            "visualType":
                "scatterChart",

            "query": {

                "queryState": {

                    "Category": {
                        "projections": [
                            {
                                "field":
                                    reason,

                                "queryRef":
                                    "Refund Impact.refund_reason",

                                "nativeQueryRef":
                                    "refund_reason",

                                "active": True,
                            }
                        ]
                    },

                    "X": {
                        "projections": [
                            {
                                "field":
                                    processing,

                                "queryRef":
                                    "Average(Refund Impact.average_processing_days)",

                                "nativeQueryRef":
                                    "average_processing_days",
                            }
                        ]
                    },

                    "Y": {
                        "projections": [
                            {
                                "field":
                                    risk,

                                "queryRef":
                                    "Sum(Refund Impact.commercial_value_at_risk_gbp)",

                                "nativeQueryRef":
                                    "commercial_value_at_risk_gbp",
                            }
                        ]
                    },

                    "Size": {
                        "projections": [
                            {
                                "field":
                                    records,

                                "queryRef":
                                    "Sum(Refund Impact.refund_records)",

                                "nativeQueryRef":
                                    "refund_records",
                            }
                        ]
                    },

                    "Series": {
                        "projections": [
                            {
                                "field":
                                    refund_type,

                                "queryRef":
                                    "Refund Impact.refund_type",

                                "nativeQueryRef":
                                    "refund_type",

                                "active": True,
                            }
                        ]
                    },
                }
            },

            "visualContainerObjects":
                title_object(
                    "Processing Time vs Commercial Exposure"
                ),

            "drillFilterOtherVisuals":
                True,
        },

        "filterConfig": {
            "filters": []
        },
    }


# ============================================================
# REFUND DETAIL TABLE
# ============================================================

def refund_table():

    fields = [
        "refund_type",
        "refund_reason",
        "sales_channel",
        "business_traveller_flag",
        "refund_records",
        "eligible_value_gbp",
        "refund_amount_gbp",
        "commercial_value_at_risk_gbp",
        "average_processing_days",
    ]

    projections = []

    for field_name in fields:

        projections.append(
            {
                "field":
                    column(
                        "Refund Impact",
                        field_name,
                    ),

                "queryRef":
                    f"Refund Impact.{field_name}",

                "nativeQueryRef":
                    field_name,
            }
        )

    return {

        "$schema": SCHEMA,

        "name": vid(
            "refund-detail-table"
        ),

        "position": {
            "x": 815,
            "y": 735,
            "z": 7000,
            "height": 290,
            "width": 1050,
            "tabOrder": 7000,
        },

        "visual": {

            "visualType":
                "tableEx",

            "query": {

                "queryState": {

                    "Values": {
                        "projections":
                            projections
                    }
                }
            },

            "objects": {

                "columnHeaders": [
                    {
                        "properties": {

                            "autoSizeColumnWidth": {
                                "expr": {
                                    "Literal": {
                                        "Value":
                                            "true"
                                    }
                                }
                            }
                        }
                    }
                ]
            },

            "visualContainerObjects":
                title_object(
                    "Refund & Commercial Risk Detail"
                ),

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
print("RAILPARTNER 360 — STAGE 8J")
print("REFUND & COMMERCIAL RISK BUILD")
print("=" * 76)


page = find_page(
    "Refund & Commercial Risk"
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
    "[OK] Refund & Commercial Risk page:"
    f" {page.name}"
)


# ============================================================
# PAGE CONTENT
# ============================================================

visuals = [

    create_textbox(
        "title",
        "Refund & Commercial Risk",
        55,
        28,
        950,
        65,
        26,
        True,
    ),

    create_textbox(
        "subtitle",
        (
            "Refund exposure, processing performance "
            "and commercial value at risk"
        ),
        55,
        88,
        1200,
        45,
        13,
        False,
    ),
]


# ============================================================
# KPI CARDS
# ============================================================

cards = [
    (
        "refund-records",
        "Refund Analysis Records",
    ),
    (
        "refund-amount",
        "Refund Analysis Amount",
    ),
    (
        "risk",
        "Refund Analysis Value at Risk",
    ),
]


left = 55
gap = 30
card_width = 585
card_height = 145
card_y = 165


for index, (
    key,
    measure_name,
) in enumerate(cards):

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

visuals.extend(
    [
        risk_reason_chart(),
        refund_channel_chart(),
        processing_scatter(),
        refund_table(),
    ]
)


# ============================================================
# WRITE VISUAL FILES
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
# VALIDATE
# ============================================================

for visual in visuals:

    path = (
        visuals_dir
        / visual["name"]
        / "visual.json"
    )

    if not path.exists():

        raise RuntimeError(
            f"Missing visual: {path}"
        )

    json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


print()
print("=" * 76)
print("STAGE 8J VALIDATION")
print("=" * 76)

print(
    "[OK] Title and subtitle created"
)

print(
    "[OK] Three refund-risk KPI cards created"
)

print(
    "[OK] Commercial-risk reason chart created"
)

print(
    "[OK] Refund type/channel chart created"
)

print(
    "[OK] Processing/exposure scatter created"
)

print(
    "[OK] Refund detail table created"
)

print()
print("=" * 76)
print("STAGE 8J COMPLETE")
print("=" * 76)