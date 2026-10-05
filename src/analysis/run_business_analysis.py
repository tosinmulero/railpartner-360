from __future__ import annotations

from pathlib import Path
import os

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SQL_DIR = (
    PROJECT_ROOT
    / "sql"
    / "business_analysis"
)

EXPORT_DIR = (
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

EXPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

load_dotenv(
    PROJECT_ROOT / ".env"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

engine = create_engine(
    f"postgresql+psycopg2://"
    f"{user}:{password}"
    f"@{host}:{port}/{database}"
)


# ============================================================
# SQL FILES
# ============================================================

queries = [
    "01_executive_kpis.sql",
    "02_partner_opportunity.sql",
    "03_conversion_funnel.sql",
    "04_customer_segments.sql",
    "05_route_opportunity.sql",
    "06_operator_performance.sql",
    "07_refund_impact.sql",
]


# ============================================================
# EXECUTE ANALYSES
# ============================================================

results = {}

print("=" * 76)
print("RAILPARTNER 360 - STAGE 7 BUSINESS ANALYSIS")
print("=" * 76)

for filename in queries:

    sql_path = (
        SQL_DIR
        / filename
    )

    sql = sql_path.read_text(
        encoding="utf-8-sig"
    )

    analysis_name = (
        filename
        .replace(".sql", "")
    )

    print(
        f"\nRunning: {analysis_name}"
    )

    df = pd.read_sql_query(
        sql,
        engine,
    )

    results[
        analysis_name
    ] = df

    output_path = (
        EXPORT_DIR
        / f"{analysis_name}.csv"
    )

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8"
    )

    print(
        f"[OK] {len(df):,} rows"
    )

    print(
        f"[SAVED] {output_path.name}"
    )


# ============================================================
# EXECUTIVE KPI VALUES
# ============================================================

kpi = (
    results[
        "01_executive_kpis"
    ]
    .iloc[0]
)


# ============================================================
# TOP PARTNER INSIGHT
# ============================================================

partners = results[
    "02_partner_opportunity"
]

top_partner = (
    partners
    .sort_values(
        "platform_revenue_gbp",
        ascending=False
    )
    .iloc[0]
)

highest_risk_partner = (
    partners
    .sort_values(
        "commercial_value_at_risk_gbp",
        ascending=False
    )
    .iloc[0]
)


# ============================================================
# BEST CONVERSION SEGMENT
# ============================================================

conversion = results[
    "03_conversion_funnel"
]

best_conversion = (
    conversion
    .sort_values(
        "conversion_rate_pct",
        ascending=False
    )
    .iloc[0]
)


# ============================================================
# CUSTOMER VALUE
# ============================================================

customers = results[
    "04_customer_segments"
]

top_customer_segment = (
    customers
    .sort_values(
        "platform_revenue_gbp",
        ascending=False
    )
    .iloc[0]
)


# ============================================================
# ROUTE OPPORTUNITY
# ============================================================

routes = results[
    "05_route_opportunity"
]

route_candidates = (
    routes[
        routes[
            "commercial_priority"
        ]
        .isin(
            [
                "Protect High Demand",
                "Conversion Opportunity",
            ]
        )
    ]
)

if route_candidates.empty:

    route_candidate = (
        routes
        .sort_values(
            "platform_revenue_gbp",
            ascending=False
        )
        .iloc[0]
    )

else:

    route_candidate = (
        route_candidates
        .sort_values(
            "platform_revenue_gbp",
            ascending=False
        )
        .iloc[0]
    )


# ============================================================
# OPERATOR RISK
# ============================================================

operators = results[
    "06_operator_performance"
]

highest_disruption_operator = (
    operators
    .sort_values(
        "disruption_rate_pct",
        ascending=False
    )
    .iloc[0]
)


# ============================================================
# REFUND IMPACT
# ============================================================

refunds = results[
    "07_refund_impact"
]

largest_refund_driver = (
    refunds
    .sort_values(
        "commercial_value_at_risk_gbp",
        ascending=False
    )
    .iloc[0]
)


# ============================================================
# WRITE EXECUTIVE SUMMARY
# ============================================================

summary = f"""# RailPartner 360
## Executive Commercial Analysis

### Portfolio Scale

- Searches analysed: **{int(kpi['total_searches']):,}**
- Bookings analysed: **{int(kpi['total_bookings']):,}**
- Passengers represented: **{int(kpi['total_passengers']):,}**
- Overall conversion rate: **{float(kpi['conversion_rate_pct']):.2f}%**
- Gross booking value: **£{float(kpi['gross_booking_value_gbp']):,.2f}**
- Net ticket value: **£{float(kpi['net_ticket_value_gbp']):,.2f}**
- Platform revenue: **£{float(kpi['platform_revenue_gbp']):,.2f}**
- Average booking value: **£{float(kpi['average_booking_value_gbp']):,.2f}**
- B2B booking share: **{float(kpi['b2b_booking_share_pct']):.2f}%**

### Operational Performance

- Journeys analysed: **{int(kpi['total_journeys']):,}**
- Operator cancellations: **{int(kpi['operator_cancelled_journeys']):,}**
- Operator cancellation rate: **{float(kpi['operator_cancellation_rate_pct']):.2f}%**
- Disruption rate: **{float(kpi['disruption_rate_pct']):.2f}%**
- Journeys within three minutes: **{float(kpi['within_3_minutes_pct']):.2f}%**

### Refund and Commercial Risk

- Refund / compensation records: **{int(kpi['refund_records']):,}**
- Refund amount: **£{float(kpi['total_refund_amount_gbp']):,.2f}**
- Commercial value at risk: **£{float(kpi['commercial_value_at_risk_gbp']):,.2f}**

---

## Key Commercial Findings

### 1. Highest-Revenue Partner

**{top_partner['partner_name']}**

- Segment: {top_partner['partner_segment']}
- Bookings: {int(top_partner['bookings']):,}
- Conversion: {float(top_partner['conversion_rate_pct']):.2f}%
- Platform revenue: £{float(top_partner['platform_revenue_gbp']):,.2f}
- Disruption rate: {float(top_partner['disruption_rate_pct']):.2f}%

This partner should be treated as a strategically important account because it contributes the largest amount of platform revenue.

### 2. Partner With Greatest Commercial Risk

**{highest_risk_partner['partner_name']}**

- Platform revenue: £{float(highest_risk_partner['platform_revenue_gbp']):,.2f}
- Commercial value at risk: £{float(highest_risk_partner['commercial_value_at_risk_gbp']):,.2f}
- Refund records: {int(highest_risk_partner['refund_records']):,}
- Disruption rate: {float(highest_risk_partner['disruption_rate_pct']):.2f}%

Commercial and Product teams should investigate whether disruption is damaging partner experience or future booking behaviour.

### 3. Strongest Funnel Segment

**{best_conversion['sales_channel']} / {best_conversion['customer_segment']}**

- Conversion rate: {float(best_conversion['conversion_rate_pct']):.2f}%
- Searches: {int(best_conversion['searches']):,}
- Bookings: {int(best_conversion['bookings']):,}

This combination provides a benchmark for product funnel performance.

### 4. Highest-Value Customer Segment

**{top_customer_segment['customer_segment']} — {top_customer_segment['loyalty_tier']}**

- Customers: {int(top_customer_segment['customers']):,}
- Bookings: {int(top_customer_segment['bookings']):,}
- Platform revenue: £{float(top_customer_segment['platform_revenue_gbp']):,.2f}
- Conversion: {float(top_customer_segment['conversion_rate_pct']):.2f}%

Retention and loyalty initiatives should prioritise segments with high repeat value and revenue contribution.

### 5. Route Requiring Commercial Attention

**{route_candidate['origin_station']} → {route_candidate['destination_station']}**

- Operator: {route_candidate['operator_name']}
- Commercial priority: {route_candidate['commercial_priority']}
- Searches: {int(route_candidate['searches']):,}
- Bookings: {int(route_candidate['bookings']):,}
- Conversion: {float(route_candidate['conversion_rate_pct']):.2f}%
- Platform revenue: £{float(route_candidate['platform_revenue_gbp']):,.2f}
- Disruption rate: {float(route_candidate['disruption_rate_pct']):.2f}%

This route represents a product, commercial, or reliability optimisation opportunity.

### 6. Highest-Disruption Operator

**{highest_disruption_operator['operator_name']}**

- Journeys: {int(highest_disruption_operator['journeys']):,}
- Disruption rate: {float(highest_disruption_operator['disruption_rate_pct']):.2f}%
- Cancellation rate: {float(highest_disruption_operator['cancellation_rate_pct']):.2f}%
- Average arrival delay: {float(highest_disruption_operator['average_arrival_delay_minutes']):.2f} minutes

Operational reliability should be incorporated into partner-facing performance reporting.

### 7. Largest Refund / Compensation Driver

**{largest_refund_driver['refund_type']} — {largest_refund_driver['refund_reason']}**

- Refund records: {int(largest_refund_driver['refund_records']):,}
- Refund amount: £{float(largest_refund_driver['refund_amount_gbp']):,.2f}
- Commercial value at risk: £{float(largest_refund_driver['commercial_value_at_risk_gbp']):,.2f}
- Average processing time: {float(largest_refund_driver['average_processing_days']):.2f} days

This is the largest quantified source of refund-related commercial exposure in the dataset.

---

## Recommended Business Actions

1. Protect high-value B2B partners by combining revenue performance with service-quality KPIs.
2. Investigate high-search / low-conversion segments for pricing, availability or UX friction.
3. Prioritise reliability interventions on routes where demand and disruption are simultaneously high.
4. Build partner scorecards combining bookings, revenue, conversion, disruption and refund exposure.
5. Use high-performing customer segments as benchmarks for retention and loyalty strategy.
6. Monitor refund processing and disruption-related value at risk as commercial KPIs.
7. Test product interventions through controlled experiments rather than relying only on observational analysis.

---

## Data Disclaimer

Transaction-level customer, booking and journey records in RailPartner 360 are synthetic portfolio data. They are designed to demonstrate analytics engineering, commercial analysis and product analytics methods and do not represent Trainline customer or commercial data.
"""

summary_path = (
    REPORT_DIR
    / "railpartner360_executive_analysis.md"
)

summary_path.write_text(
    summary,
    encoding="utf-8"
)


# ============================================================
# FINAL CONSOLE SUMMARY
# ============================================================

print()
print("=" * 76)
print("EXECUTIVE FINDINGS")
print("=" * 76)

print(
    f"Overall conversion: "
    f"{float(kpi['conversion_rate_pct']):.2f}%"
)

print(
    f"Platform revenue: "
    f"£{float(kpi['platform_revenue_gbp']):,.2f}"
)

print(
    f"B2B booking share: "
    f"{float(kpi['b2b_booking_share_pct']):.2f}%"
)

print(
    f"Disruption rate: "
    f"{float(kpi['disruption_rate_pct']):.2f}%"
)

print(
    f"Commercial value at risk: "
    f"£{float(kpi['commercial_value_at_risk_gbp']):,.2f}"
)

print()
print(
    f"Top revenue partner: "
    f"{top_partner['partner_name']}"
)

print(
    f"Highest-value customer segment: "
    f"{top_customer_segment['customer_segment']} "
    f"/ {top_customer_segment['loyalty_tier']}"
)

print(
    f"Highest-disruption operator: "
    f"{highest_disruption_operator['operator_name']}"
)

print()
print(
    f"[SAVED] {summary_path}"
)

print()
print("=" * 76)
print("STAGE 7 BUSINESS ANALYSIS COMPLETE")
print("=" * 76)

engine.dispose()
