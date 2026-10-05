from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "exports"
    / "stage7_business_analysis"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "executive"
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def load(name):
    return pd.read_csv(
        DATA_DIR / name
    )


def num(value):
    if pd.isna(value):
        return 0.0
    return float(value)


def integer(value):
    if pd.isna(value):
        return 0
    return int(value)


# ============================================================
# LOAD ANALYTICAL OUTPUTS
# ============================================================

kpis = load(
    "01_executive_kpis.csv"
)

partners = load(
    "02_partner_opportunity.csv"
)

conversion = load(
    "03_conversion_funnel.csv"
)

customers = load(
    "04_customer_segments.csv"
)

routes = load(
    "05_route_opportunity.csv"
)

operators = load(
    "06_operator_performance.csv"
)

refunds = load(
    "07_refund_impact.csv"
)


# ============================================================
# EXECUTIVE KPIs
# ============================================================

kpi = kpis.iloc[0]


# ============================================================
# PARTNER FINDINGS
# ============================================================

top_partner = (
    partners
    .sort_values(
        "platform_revenue_gbp",
        ascending=False,
    )
    .iloc[0]
)

highest_risk_partner = (
    partners
    .sort_values(
        "commercial_value_at_risk_gbp",
        ascending=False,
    )
    .iloc[0]
)


# ============================================================
# CONVERSION FINDINGS
# ============================================================

best_conversion = (
    conversion
    .sort_values(
        "conversion_rate_pct",
        ascending=False,
    )
    .iloc[0]
)

lowest_conversion = (
    conversion[
        conversion["searches"] > 0
    ]
    .sort_values(
        "conversion_rate_pct",
        ascending=True,
    )
    .iloc[0]
)


# ============================================================
# CUSTOMER FINDINGS
# ============================================================

top_customer_segment = (
    customers
    .sort_values(
        "platform_revenue_gbp",
        ascending=False,
    )
    .iloc[0]
)


# ============================================================
# ROUTE FINDINGS
# ============================================================

top_revenue_route = (
    routes
    .sort_values(
        "platform_revenue_gbp",
        ascending=False,
    )
    .iloc[0]
)

highest_disruption_route = (
    routes[
        routes["journeys"] >= 500
    ]
    .sort_values(
        "disruption_rate_pct",
        ascending=False,
    )
    .iloc[0]
)

conversion_opportunities = routes[
    routes[
        "commercial_priority"
    ] == "Conversion Opportunity"
]

if not conversion_opportunities.empty:

    best_route_opportunity = (
        conversion_opportunities
        .sort_values(
            "searches",
            ascending=False,
        )
        .iloc[0]
    )

else:

    best_route_opportunity = (
        routes
        .sort_values(
            "searches",
            ascending=False,
        )
        .iloc[0]
    )


# ============================================================
# OPERATOR FINDINGS
# ============================================================

highest_disruption_operator = (
    operators
    .sort_values(
        "disruption_rate_pct",
        ascending=False,
    )
    .iloc[0]
)

best_operator = (
    operators
    .sort_values(
        [
            "disruption_rate_pct",
            "cancellation_rate_pct",
        ],
        ascending=True,
    )
    .iloc[0]
)


# ============================================================
# REFUND FINDINGS
# ============================================================

largest_refund_driver = (
    refunds
    .sort_values(
        "commercial_value_at_risk_gbp",
        ascending=False,
    )
    .iloc[0]
)


# ============================================================
# TERMINAL OUTPUT
# ============================================================

print()
print("=" * 76)
print("EXECUTIVE FINDINGS")
print("=" * 76)

print()
print("PORTFOLIO SCALE")
print("-" * 76)

print(
    f"Searches: "
    f"{integer(kpi['total_searches']):,}"
)

print(
    f"Bookings: "
    f"{integer(kpi['total_bookings']):,}"
)

print(
    f"Overall conversion: "
    f"{num(kpi['conversion_rate_pct']):.2f}%"
)

print(
    f"Gross booking value: "
    f"GBP {num(kpi['gross_booking_value_gbp']):,.2f}"
)

print(
    f"Platform revenue: "
    f"GBP {num(kpi['platform_revenue_gbp']):,.2f}"
)

print(
    f"B2B booking share: "
    f"{num(kpi['b2b_booking_share_pct']):.2f}%"
)

print()
print("OPERATIONS")
print("-" * 76)

print(
    f"Journeys: "
    f"{integer(kpi['total_journeys']):,}"
)

print(
    f"Disruption rate: "
    f"{num(kpi['disruption_rate_pct']):.2f}%"
)

print(
    f"Cancellation rate: "
    f"{num(kpi['operator_cancellation_rate_pct']):.2f}%"
)

print(
    f"Within 3 minutes: "
    f"{num(kpi['within_3_minutes_pct']):.2f}%"
)

print()
print("COMMERCIAL RISK")
print("-" * 76)

print(
    f"Refund records: "
    f"{integer(kpi['refund_records']):,}"
)

print(
    f"Refund amount: "
    f"GBP {num(kpi['total_refund_amount_gbp']):,.2f}"
)

print(
    f"Commercial value at risk: "
    f"GBP {num(kpi['commercial_value_at_risk_gbp']):,.2f}"
)

print()
print("TOP COMMERCIAL FINDINGS")
print("-" * 76)

print(
    f"Top revenue partner: "
    f"{top_partner['partner_name']} "
    f"(GBP {num(top_partner['platform_revenue_gbp']):,.2f})"
)

print(
    f"Highest-risk partner: "
    f"{highest_risk_partner['partner_name']} "
    f"(GBP {num(highest_risk_partner['commercial_value_at_risk_gbp']):,.2f} at risk)"
)

print(
    f"Best-converting segment: "
    f"{best_conversion['sales_channel']} / "
    f"{best_conversion['customer_segment']} "
    f"({num(best_conversion['conversion_rate_pct']):.2f}%)"
)

print(
    f"Lowest-converting segment: "
    f"{lowest_conversion['sales_channel']} / "
    f"{lowest_conversion['customer_segment']} "
    f"({num(lowest_conversion['conversion_rate_pct']):.2f}%)"
)

print(
    f"Highest-value customer segment: "
    f"{top_customer_segment['customer_segment']} / "
    f"{top_customer_segment['loyalty_tier']} "
    f"(GBP {num(top_customer_segment['platform_revenue_gbp']):,.2f})"
)

print(
    f"Top revenue route: "
    f"{top_revenue_route['origin_station']} -> "
    f"{top_revenue_route['destination_station']} "
    f"(GBP {num(top_revenue_route['platform_revenue_gbp']):,.2f})"
)

print(
    f"Highest-disruption route: "
    f"{highest_disruption_route['origin_station']} -> "
    f"{highest_disruption_route['destination_station']} "
    f"({num(highest_disruption_route['disruption_rate_pct']):.2f}%)"
)

print(
    f"Route conversion opportunity: "
    f"{best_route_opportunity['origin_station']} -> "
    f"{best_route_opportunity['destination_station']}"
)

print(
    f"Highest-disruption operator: "
    f"{highest_disruption_operator['operator_name']} "
    f"({num(highest_disruption_operator['disruption_rate_pct']):.2f}%)"
)

print(
    f"Best operational performer: "
    f"{best_operator['operator_name']} "
    f"({num(best_operator['disruption_rate_pct']):.2f}% disruption)"
)

print(
    f"Largest refund driver: "
    f"{largest_refund_driver['refund_type']} / "
    f"{largest_refund_driver['refund_reason']} "
    f"(GBP {num(largest_refund_driver['commercial_value_at_risk_gbp']):,.2f} at risk)"
)


# ============================================================
# EXECUTIVE MARKDOWN REPORT
# ============================================================

report = f"""# RailPartner 360 — Executive Analysis

## Executive KPIs

| KPI | Result |
|---|---:|
| Searches | {integer(kpi['total_searches']):,} |
| Bookings | {integer(kpi['total_bookings']):,} |
| Conversion Rate | {num(kpi['conversion_rate_pct']):.2f}% |
| Gross Booking Value | GBP {num(kpi['gross_booking_value_gbp']):,.2f} |
| Platform Revenue | GBP {num(kpi['platform_revenue_gbp']):,.2f} |
| B2B Booking Share | {num(kpi['b2b_booking_share_pct']):.2f}% |
| Journeys | {integer(kpi['total_journeys']):,} |
| Disruption Rate | {num(kpi['disruption_rate_pct']):.2f}% |
| Operator Cancellation Rate | {num(kpi['operator_cancellation_rate_pct']):.2f}% |
| Within 3 Minutes | {num(kpi['within_3_minutes_pct']):.2f}% |
| Refund Amount | GBP {num(kpi['total_refund_amount_gbp']):,.2f} |
| Commercial Value at Risk | GBP {num(kpi['commercial_value_at_risk_gbp']):,.2f} |

## Commercial Findings

### Partner Performance

The highest-revenue partner is **{top_partner['partner_name']}**, generating **GBP {num(top_partner['platform_revenue_gbp']):,.2f}** in platform revenue.

The partner with the highest commercial value at risk is **{highest_risk_partner['partner_name']}**, with **GBP {num(highest_risk_partner['commercial_value_at_risk_gbp']):,.2f}** exposed.

### Funnel Performance

The strongest conversion segment is **{best_conversion['sales_channel']} / {best_conversion['customer_segment']}**, converting at **{num(best_conversion['conversion_rate_pct']):.2f}%**.

The weakest segment is **{lowest_conversion['sales_channel']} / {lowest_conversion['customer_segment']}**, converting at **{num(lowest_conversion['conversion_rate_pct']):.2f}%**.

### Customer Value

The highest-value customer segment is **{top_customer_segment['customer_segment']} / {top_customer_segment['loyalty_tier']}**, contributing **GBP {num(top_customer_segment['platform_revenue_gbp']):,.2f}** in platform revenue.

### Route Performance

The highest-revenue route is **{top_revenue_route['origin_station']} to {top_revenue_route['destination_station']}**, producing **GBP {num(top_revenue_route['platform_revenue_gbp']):,.2f}** in platform revenue.

The highest-disruption route among materially travelled routes is **{highest_disruption_route['origin_station']} to {highest_disruption_route['destination_station']}**, with a disruption rate of **{num(highest_disruption_route['disruption_rate_pct']):.2f}%**.

The strongest identified conversion opportunity is **{best_route_opportunity['origin_station']} to {best_route_opportunity['destination_station']}**.

### Operator Performance

The highest-disruption operator is **{highest_disruption_operator['operator_name']}**, with a disruption rate of **{num(highest_disruption_operator['disruption_rate_pct']):.2f}%**.

The strongest operational performer is **{best_operator['operator_name']}**, with disruption at **{num(best_operator['disruption_rate_pct']):.2f}%**.

### Refund Exposure

The largest refund-related commercial exposure is **{largest_refund_driver['refund_type']} / {largest_refund_driver['refund_reason']}**, representing **GBP {num(largest_refund_driver['commercial_value_at_risk_gbp']):,.2f}** in value at risk.

## Recommended Actions

1. Protect and grow high-revenue strategic partners.
2. Investigate low-conversion channels and customer segments.
3. Prioritise high-demand routes with elevated disruption.
4. Incorporate reliability metrics into partner scorecards.
5. Target high-value customer segments with retention initiatives.
6. Monitor refund exposure as a commercial KPI.
7. Test product changes using measurable experimentation frameworks.

## Portfolio Disclaimer

The transaction-level customer, search, booking and journey data used in RailPartner 360 are synthetic. The project demonstrates analytics engineering, product analytics, commercial analytics and business intelligence techniques and does not represent Trainline proprietary data.
"""

report_path = (
    REPORT_DIR
    / "railpartner360_executive_analysis.md"
)

report_path.write_text(
    report,
    encoding="utf-8",
)

print()
print(
    f"[SAVED] {report_path}"
)

print()
print("=" * 76)
print("STAGE 7B EXECUTIVE ANALYSIS COMPLETE")
print("=" * 76)