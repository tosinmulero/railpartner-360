from __future__ import annotations

from pathlib import Path
import hashlib
import json


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


def create_scatter():

    partner = column(
        "Partner Performance",
        "partner_name",
    )

    conversion = aggregation(
        "Partner Performance",
        "conversion_rate_pct",
        1,
    )

    revenue = aggregation(
        "Partner Performance",
        "platform_revenue_gbp",
        0,
    )

    bookings = aggregation(
        "Partner Performance",
        "bookings",
        0,
    )

    risk = aggregation(
        "Partner Performance",
        "commercial_value_at_risk_gbp",
        0,
    )

    return {
        "$schema": SCHEMA,
        "name": vid(
            "revenue-conversion-scatter"
        ),

        "position": {
            "x": 1240,
            "y": 385,
            "z": 6000,
            "height": 285,
            "width": 625,
            "tabOrder": 6000,
        },

        "visual": {

            "visualType": "scatterChart",

            "query": {

                "queryState": {

                    "Category": {
                        "projections": [
                            {
                                "field": partner,
                                "queryRef":
                                    "Partner Performance.partner_name",
                                "nativeQueryRef":
                                    "partner_name",
                                "active": True,
                            }
                        ]
                    },

                    "X": {
                        "projections": [
                            {
                                "field": conversion,
                                "queryRef":
                                    "Average(Partner Performance.conversion_rate_pct)",
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
                                    "Sum(Partner Performance.platform_revenue_gbp)",
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
                                    "Sum(Partner Performance.bookings)",
                                "nativeQueryRef":
                                    "bookings",
                            }
                        ]
                    },

                    "Tooltips": {
                        "projections": [
                            {
                                "field": risk,
                                "queryRef":
                                    "Sum(Partner Performance.commercial_value_at_risk_gbp)",
                                "nativeQueryRef":
                                    "commercial_value_at_risk_gbp",
                            }
                        ]
                    },
                }
            },

            "visualContainerObjects":
                title_object(
                    "Revenue vs Conversion"
                ),

            "drillFilterOtherVisuals":
                True,
        },

        "filterConfig": {
            "filters": []
        },
    }


def create_table():

    fields = [
        "partner_name",
        "partner_segment",
        "service_tier",
        "searches",
        "bookings",
        "conversion_rate_pct",
        "platform_revenue_gbp",
        "disruption_rate_pct",
        "refund_amount_gbp",
        "commercial_value_at_risk_gbp",
        "revenue_rank",
        "risk_rank",
    ]

    projections = []

    for field_name in fields:

        field = column(
            "Partner Performance",
            field_name,
        )

        projections.append(
            {
                "field": field,
                "queryRef":
                    f"Partner Performance.{field_name}",
                "nativeQueryRef":
                    field_name,
            }
        )

    return {
        "$schema": SCHEMA,

        "name": vid(
            "partner-detail-table"
        ),

        "position": {
            "x": 55,
            "y": 700,
            "z": 7000,
            "height": 330,
            "width": 1810,
            "tabOrder": 7000,
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

                            "columnAdjustment": {
                                "expr": {
                                    "Literal": {
                                        "Value":
                                            "'growToFit'"
                                    }
                                }
                            },

                            "autoSizeColumnWidth": {
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

            "visualContainerObjects":
                title_object(
                    "Partner Performance Detail"
                ),

            "drillFilterOtherVisuals":
                True,
        },

        "filterConfig": {
            "filters": []
        },
    }


print("=" * 76)
print("RAILPARTNER 360 — STAGE 8G-2")
print("PARTNER PERFORMANCE DETAIL BUILD")
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


# ============================================================
# RESIZE EXISTING RANKING CHARTS
# ============================================================

revenue_chart = (
    visuals_dir
    / vid("revenue-ranking")
    / "visual.json"
)

risk_chart = (
    visuals_dir
    / vid("risk-ranking")
    / "visual.json"
)


if revenue_chart.exists():

    data = json.loads(
        revenue_chart.read_text(
            encoding="utf-8-sig"
        )
    )

    data["position"].update(
        {
            "x": 55,
            "y": 385,
            "width": 555,
            "height": 285,
        }
    )

    write_json(
        revenue_chart,
        data,
    )

    print(
        "[OK] Revenue ranking resized"
    )


if risk_chart.exists():

    data = json.loads(
        risk_chart.read_text(
            encoding="utf-8-sig"
        )
    )

    data["position"].update(
        {
            "x": 630,
            "y": 385,
            "width": 555,
            "height": 285,
        }
    )

    write_json(
        risk_chart,
        data,
    )

    print(
        "[OK] Risk ranking resized"
    )


# ============================================================
# CREATE NEW VISUALS
# ============================================================

new_visuals = [
    create_scatter(),
    create_table(),
]


for visual in new_visuals:

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

for visual in new_visuals:

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
print("STAGE 8G-2 VALIDATION")
print("=" * 76)

print(
    "[OK] Revenue vs Conversion scatter created"
)

print(
    "[OK] Partner detail table created"
)

print(
    "[OK] Existing ranking charts preserved"
)

print(
    "[OK] Partner page layout reorganised"
)

print()
print("=" * 76)
print("STAGE 8G-2 COMPLETE")
print("=" * 76)