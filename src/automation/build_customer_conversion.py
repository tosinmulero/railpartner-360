from __future__ import annotations

from pathlib import Path
import hashlib
import json


# ============================================================
# RAILPARTNER 360
# STAGE 8H — CUSTOMER & CONVERSION PAGE
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
            "railpartner360::customer::"
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
# CONVERSION BY CHANNEL
# ============================================================

def conversion_chart():

    category = column(
        "Conversion Funnel",
        "sales_channel",
    )

    value = aggregation(
        "Conversion Funnel",
        "conversion_rate_pct",
        1,
    )

    series = column(
        "Conversion Funnel",
        "customer_segment",
    )

    return {

        "$schema": SCHEMA,

        "name": vid(
            "conversion-by-channel"
        ),

        "position": {
            "x": 55,
            "y": 170,
            "z": 3000,
            "height": 390,
            "width": 885,
            "tabOrder": 3000,
        },

        "visual": {

            "visualType":
                "clusteredBarChart",

            "query": {

                "queryState": {

                    "Category": {
                        "projections": [
                            {
                                "field": category,

                                "queryRef":
                                    "Conversion Funnel.sales_channel",

                                "nativeQueryRef":
                                    "sales_channel",

                                "active": True,
                            }
                        ]
                    },

                    "Y": {
                        "projections": [
                            {
                                "field": value,

                                "queryRef":
                                    "Average(Conversion Funnel.conversion_rate_pct)",

                                "nativeQueryRef":
                                    "conversion_rate_pct",
                            }
                        ]
                    },

                    "Series": {
                        "projections": [
                            {
                                "field": series,

                                "queryRef":
                                    "Conversion Funnel.customer_segment",

                                "nativeQueryRef":
                                    "customer_segment",

                                "active": True,
                            }
                        ]
                    },
                }
            },

            "visualContainerObjects":
                title_object(
                    "Conversion Rate by Sales Channel"
                ),

            "drillFilterOtherVisuals":
                True,
        },

        "filterConfig": {
            "filters": []
        },
    }


# ============================================================
# REVENUE BY CUSTOMER SEGMENT
# ============================================================

def revenue_chart():

    category = column(
        "Customer Segments",
        "customer_segment",
    )

    value = aggregation(
        "Customer Segments",
        "platform_revenue_gbp",
        0,
    )

    series = column(
        "Customer Segments",
        "loyalty_tier",
    )

    return {

        "$schema": SCHEMA,

        "name": vid(
            "revenue-by-segment"
        ),

        "position": {
            "x": 980,
            "y": 170,
            "z": 4000,
            "height": 390,
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
                                "field": category,

                                "queryRef":
                                    "Customer Segments.customer_segment",

                                "nativeQueryRef":
                                    "customer_segment",

                                "active": True,
                            }
                        ]
                    },

                    "Y": {
                        "projections": [
                            {
                                "field": value,

                                "queryRef":
                                    "Sum(Customer Segments.platform_revenue_gbp)",

                                "nativeQueryRef":
                                    "platform_revenue_gbp",
                            }
                        ]
                    },

                    "Series": {
                        "projections": [
                            {
                                "field": series,

                                "queryRef":
                                    "Customer Segments.loyalty_tier",

                                "nativeQueryRef":
                                    "loyalty_tier",

                                "active": True,
                            }
                        ]
                    },
                }
            },

            "visualContainerObjects":
                title_object(
                    "Customer Segments by Platform Revenue"
                ),

            "drillFilterOtherVisuals":
                True,
        },

        "filterConfig": {
            "filters": []
        },
    }


# ============================================================
# CUSTOMER VALUE SCATTER
# ============================================================

def customer_scatter():

    category = column(
        "Customer Segments",
        "customer_segment",
    )

    conversion = aggregation(
        "Customer Segments",
        "conversion_rate_pct",
        1,
    )

    revenue = aggregation(
        "Customer Segments",
        "platform_revenue_gbp",
        0,
    )

    bookings = aggregation(
        "Customer Segments",
        "bookings",
        0,
    )

    loyalty = column(
        "Customer Segments",
        "loyalty_tier",
    )

    return {

        "$schema": SCHEMA,

        "name": vid(
            "segment-value-scatter"
        ),

        "position": {
            "x": 55,
            "y": 600,
            "z": 5000,
            "height": 410,
            "width": 750,
            "tabOrder": 5000,
        },

        "visual": {

            "visualType":
                "scatterChart",

            "query": {

                "queryState": {

                    "Category": {
                        "projections": [
                            {
                                "field": category,

                                "queryRef":
                                    "Customer Segments.customer_segment",

                                "nativeQueryRef":
                                    "customer_segment",

                                "active": True,
                            }
                        ]
                    },

                    "X": {
                        "projections": [
                            {
                                "field": conversion,

                                "queryRef":
                                    "Average(Customer Segments.conversion_rate_pct)",

                                "nativeQueryRef":
                                    "conversion_rate_pct",
                            }
                        ]
                    },

                    "Y": {
                        "projections": [
                            {
                                "field": revenue,

                                "queryRef":
                                    "Sum(Customer Segments.platform_revenue_gbp)",

                                "nativeQueryRef":
                                    "platform_revenue_gbp",
                            }
                        ]
                    },

                    "Size": {
                        "projections": [
                            {
                                "field": bookings,

                                "queryRef":
                                    "Sum(Customer Segments.bookings)",

                                "nativeQueryRef":
                                    "bookings",
                            }
                        ]
                    },

                    "Series": {
                        "projections": [
                            {
                                "field": loyalty,

                                "queryRef":
                                    "Customer Segments.loyalty_tier",

                                "nativeQueryRef":
                                    "loyalty_tier",

                                "active": True,
                            }
                        ]
                    },
                }
            },

            "visualContainerObjects":
                title_object(
                    "Customer Value vs Conversion"
                ),

            "drillFilterOtherVisuals":
                True,
        },

        "filterConfig": {
            "filters": []
        },
    }


# ============================================================
# CONVERSION OPPORTUNITY TABLE
# ============================================================

def opportunity_table():

    fields = [
        "sales_channel",
        "customer_segment",
        "business_traveller_flag",
        "searches",
        "bookings",
        "conversion_rate_pct",
        "average_lowest_fare_gbp",
        "average_booking_lead_days",
    ]

    projections = []

    for field_name in fields:

        projections.append(
            {
                "field":
                    column(
                        "Conversion Funnel",
                        field_name,
                    ),

                "queryRef":
                    f"Conversion Funnel.{field_name}",

                "nativeQueryRef":
                    field_name,
            }
        )

    return {

        "$schema": SCHEMA,

        "name": vid(
            "conversion-opportunity-table"
        ),

        "position": {
            "x": 845,
            "y": 600,
            "z": 6000,
            "height": 410,
            "width": 1020,
            "tabOrder": 6000,
        },

        "visual": {

            "visualType": "tableEx",

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
                    "Conversion Opportunity Matrix"
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
print("RAILPARTNER 360 — STAGE 8H")
print("CUSTOMER & CONVERSION BUILD")
print("=" * 76)


page = find_page(
    "Customer & Conversion"
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
    "[OK] Customer & Conversion page:"
    f" {page.name}"
)


# ============================================================
# BUILD VISUALS
# ============================================================

visuals = [

    create_textbox(
        "title",
        "Customer & Conversion",
        55,
        28,
        850,
        65,
        26,
        True,
    ),

    create_textbox(
        "subtitle",
        (
            "Customer behaviour, funnel performance "
            "and commercial value"
        ),
        55,
        88,
        1100,
        45,
        13,
        False,
    ),

    conversion_chart(),

    revenue_chart(),

    customer_scatter(),

    opportunity_table(),
]


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
print("STAGE 8H VALIDATION")
print("=" * 76)

print(
    "[OK] Title and subtitle created"
)

print(
    "[OK] Conversion-by-channel chart created"
)

print(
    "[OK] Customer revenue chart created"
)

print(
    "[OK] Customer value scatter created"
)

print(
    "[OK] Conversion opportunity table created"
)

print()
print("=" * 76)
print("STAGE 8H COMPLETE")
print("=" * 76)