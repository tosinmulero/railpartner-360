from __future__ import annotations

from pathlib import Path
import hashlib
import json


# ============================================================
# RAILPARTNER 360
# STAGE 8I — ROUTES & OPERATIONS
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
            "railpartner360::routes::"
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
        "Executive KPIs",
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
                                    f"Executive KPIs.{measure_name}",

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
# ROUTE SCATTER
# ============================================================

def create_route_scatter():

    route = column(
        "Route Opportunity",
        "route_id",
    )

    disruption = aggregation(
        "Route Opportunity",
        "disruption_rate_pct",
        1,
    )

    revenue = aggregation(
        "Route Opportunity",
        "platform_revenue_gbp",
        0,
    )

    bookings = aggregation(
        "Route Opportunity",
        "bookings",
        0,
    )

    priority = column(
        "Route Opportunity",
        "commercial_priority",
    )

    origin = column(
        "Route Opportunity",
        "origin_station",
    )

    destination = column(
        "Route Opportunity",
        "destination_station",
    )

    operator = column(
        "Route Opportunity",
        "operator_name",
    )

    return {

        "$schema": SCHEMA,

        "name": vid(
            "route-scatter"
        ),

        "position": {
            "x": 55,
            "y": 365,
            "z": 4000,
            "height": 360,
            "width": 885,
            "tabOrder": 4000,
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
                                    route,

                                "queryRef":
                                    "Route Opportunity.route_id",

                                "nativeQueryRef":
                                    "route_id",

                                "active": True,
                            }
                        ]
                    },

                    "X": {
                        "projections": [
                            {
                                "field":
                                    disruption,

                                "queryRef":
                                    "Average(Route Opportunity.disruption_rate_pct)",

                                "nativeQueryRef":
                                    "disruption_rate_pct",
                            }
                        ]
                    },

                    "Y": {
                        "projections": [
                            {
                                "field":
                                    revenue,

                                "queryRef":
                                    "Sum(Route Opportunity.platform_revenue_gbp)",

                                "nativeQueryRef":
                                    "platform_revenue_gbp",
                            }
                        ]
                    },

                    "Size": {
                        "projections": [
                            {
                                "field":
                                    bookings,

                                "queryRef":
                                    "Sum(Route Opportunity.bookings)",

                                "nativeQueryRef":
                                    "bookings",
                            }
                        ]
                    },

                    "Series": {
                        "projections": [
                            {
                                "field":
                                    priority,

                                "queryRef":
                                    "Route Opportunity.commercial_priority",

                                "nativeQueryRef":
                                    "commercial_priority",

                                "active": True,
                            }
                        ]
                    },

                    "Tooltips": {
                        "projections": [
                            {
                                "field": origin,
                                "queryRef":
                                    "Route Opportunity.origin_station",
                                "nativeQueryRef":
                                    "origin_station",
                            },
                            {
                                "field":
                                    destination,
                                "queryRef":
                                    "Route Opportunity.destination_station",
                                "nativeQueryRef":
                                    "destination_station",
                            },
                            {
                                "field":
                                    operator,
                                "queryRef":
                                    "Route Opportunity.operator_name",
                                "nativeQueryRef":
                                    "operator_name",
                            },
                        ]
                    },
                }
            },

            "visualContainerObjects":
                title_object(
                    "Route Revenue vs Operational Disruption"
                ),

            "drillFilterOtherVisuals":
                True,
        },

        "filterConfig": {
            "filters": []
        },
    }


# ============================================================
# OPERATOR RELIABILITY CHART
# ============================================================

def create_operator_chart():

    operator = column(
        "Operator Performance",
        "operator_name",
    )

    disruption = aggregation(
        "Operator Performance",
        "disruption_rate_pct",
        1,
    )

    cancellation = aggregation(
        "Operator Performance",
        "cancellation_rate_pct",
        1,
    )

    return {

        "$schema": SCHEMA,

        "name": vid(
            "operator-reliability"
        ),

        "position": {
            "x": 980,
            "y": 365,
            "z": 5000,
            "height": 360,
            "width": 885,
            "tabOrder": 5000,
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
                                    operator,

                                "queryRef":
                                    "Operator Performance.operator_name",

                                "nativeQueryRef":
                                    "operator_name",

                                "active": True,
                            }
                        ]
                    },

                    "Y": {
                        "projections": [
                            {
                                "field":
                                    disruption,

                                "queryRef":
                                    "Average(Operator Performance.disruption_rate_pct)",

                                "nativeQueryRef":
                                    "disruption_rate_pct",
                            },
                            {
                                "field":
                                    cancellation,

                                "queryRef":
                                    "Average(Operator Performance.cancellation_rate_pct)",

                                "nativeQueryRef":
                                    "cancellation_rate_pct",
                            },
                        ]
                    },
                }
            },

            "visualContainerObjects":
                title_object(
                    "Operator Reliability Comparison"
                ),

            "drillFilterOtherVisuals":
                True,
        },

        "filterConfig": {
            "filters": []
        },
    }


# ============================================================
# ROUTE DETAIL TABLE
# ============================================================

def create_route_table():

    fields = [
        "origin_station",
        "destination_station",
        "operator_name",
        "commercial_priority",
        "searches",
        "bookings",
        "conversion_rate_pct",
        "platform_revenue_gbp",
        "disruption_rate_pct",
        "average_arrival_delay_minutes",
        "within_3_minutes_pct",
    ]

    projections = []

    for field_name in fields:

        projections.append(
            {
                "field":
                    column(
                        "Route Opportunity",
                        field_name,
                    ),

                "queryRef":
                    f"Route Opportunity.{field_name}",

                "nativeQueryRef":
                    field_name,
            }
        )

    return {

        "$schema": SCHEMA,

        "name": vid(
            "route-detail-table"
        ),

        "position": {
            "x": 55,
            "y": 760,
            "z": 6000,
            "height": 275,
            "width": 1810,
            "tabOrder": 6000,
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
                    "Priority Route Opportunities"
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
print("RAILPARTNER 360 — STAGE 8I")
print("ROUTES & OPERATIONS BUILD")
print("=" * 76)


page = find_page(
    "Routes & Operations"
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
    "[OK] Routes & Operations page:"
    f" {page.name}"
)


# ============================================================
# PAGE CONTENT
# ============================================================

visuals = [

    create_textbox(
        "title",
        "Routes & Operations",
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
            "Route commercial performance, "
            "operator reliability and service risk"
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
        "journeys",
        "Total Journeys",
    ),
    (
        "disruption",
        "Disruption Rate %",
    ),
    (
        "cancellation",
        "Cancellation Rate %",
    ),
    (
        "punctuality",
        "Within 3 Minutes %",
    ),
]


left = 55
gap = 22
card_width = 435
card_height = 145
card_y = 170


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
# CHARTS + TABLE
# ============================================================

visuals.extend(
    [
        create_route_scatter(),
        create_operator_chart(),
        create_route_table(),
    ]
)


# ============================================================
# WRITE VISUALS
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
print("STAGE 8I VALIDATION")
print("=" * 76)

print(
    "[OK] Title and subtitle created"
)

print(
    "[OK] Four operations KPI cards created"
)

print(
    "[OK] Route revenue/disruption scatter created"
)

print(
    "[OK] Operator reliability chart created"
)

print(
    "[OK] Priority-route table created"
)

print()
print("=" * 76)
print("STAGE 8I COMPLETE")
print("=" * 76)