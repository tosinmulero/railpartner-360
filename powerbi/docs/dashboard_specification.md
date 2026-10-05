# RailPartner 360 — Power BI Dashboard Specification

## DESIGN SYSTEM

Canvas:
- 16:9 widescreen
- Recommended working size: 1280 x 720

Theme:
- Primary Blue: #2563EB
- Navy: #0F172A
- Teal: #14B8A6
- Amber: #F59E0B
- Red: #EF4444
- Purple: #8B5CF6
- Background: #F8FAFC
- Card Background: #FFFFFF
- Border: #E2E8F0
- Main Text: #0F172A
- Secondary Text: #475569

Typography:
- Page title: Segoe UI Semibold, 22–26 pt
- Visual title: Segoe UI Semibold, 11–13 pt
- KPI values: Segoe UI Semibold, 22–30 pt
- Supporting text: Segoe UI, 9–11 pt

Navigation:
1. Overview
2. Partners
3. Customers
4. Routes & Operations
5. Refund Risk


============================================================
PAGE 1 — EXECUTIVE OVERVIEW
============================================================

Purpose:
Give executives a one-page view of commercial scale,
conversion, B2B contribution, revenue and reliability.

Primary table:
01_executive_kpis

TOP KPI ROW

Card 1:
Title: Searches
Field:
total_searches

Expected:
6,000,000


Card 2:
Title: Bookings
Field:
total_bookings

Expected:
2,000,000


Card 3:
Title: Conversion Rate
Field:
conversion_rate_pct

Expected:
33.33%


Card 4:
Title: Gross Booking Value
Field:
gross_booking_value_gbp

Expected:
GBP 136.40M


Card 5:
Title: Platform Revenue
Field:
platform_revenue_gbp

Expected:
GBP 9.03M


Card 6:
Title: B2B Booking Share
Field:
b2b_booking_share_pct

Expected:
63.86%


VISUAL 1

Type:
Horizontal bar chart

Title:
Top 10 Partners by Platform Revenue

Table:
02_partner_opportunity

Y-axis:
partner_name

X-axis:
platform_revenue_gbp

Tooltip:
bookings
conversion_rate_pct
disruption_rate_pct
commercial_value_at_risk_gbp

Sort:
Platform Revenue descending

Filter:
Top N = 10


VISUAL 2

Type:
Clustered bar chart

Title:
Conversion Performance by Sales Channel

Table:
03_conversion_funnel

Axis:
sales_channel

Value:
conversion_rate_pct

Legend:
business_traveller_flag

Tooltip:
searches
bookings
average_lowest_fare_gbp


VISUAL 3

Type:
Executive KPI panel

Source:
01_executive_kpis

Metrics:
disruption_rate_pct
operator_cancellation_rate_pct
within_3_minutes_pct
commercial_value_at_risk_gbp

Expected headline metrics:
Disruption Rate = 11.23%
Cancellation Rate = 3.74%
Within 3 Minutes = 85.01%
Commercial Value at Risk = GBP 9.72M


Executive insight callout:

"RailPartner 360 processed 6.0M searches and 2.0M
bookings at a 33.33% conversion rate. B2B channels
represent 63.86% of bookings and the platform generated
GBP 9.03M revenue from GBP 136.40M gross booking value."


============================================================
PAGE 2 — PARTNER PERFORMANCE
============================================================

Primary table:
02_partner_opportunity

Slicers:
partner_type
partner_segment
service_tier


KPI CARDS:

Partners
Count of partner_id

Partner Revenue
Sum platform_revenue_gbp

Partner Bookings
Sum bookings

Average Conversion
Average conversion_rate_pct

Commercial Value at Risk
Sum commercial_value_at_risk_gbp


VISUAL 1

Type:
Scatter chart

Title:
Partner Revenue vs Conversion

X-axis:
conversion_rate_pct

Y-axis:
platform_revenue_gbp

Size:
bookings

Details:
partner_name

Tooltip:
partner_segment
service_tier
gross_booking_value_gbp
disruption_rate_pct
refund_amount_gbp
commercial_value_at_risk_gbp


VISUAL 2

Type:
Horizontal bar chart

Title:
Top 10 Revenue Partners

Axis:
partner_name

Value:
platform_revenue_gbp

Filter:
Top 10

Sort:
Descending


VISUAL 3

Type:
Horizontal bar chart

Title:
Partners With Highest Commercial Risk

Axis:
partner_name

Value:
commercial_value_at_risk_gbp

Filter:
Top 10

Sort:
Descending


VISUAL 4

Type:
Matrix

Columns:
partner_name
partner_segment
service_tier
searches
bookings
conversion_rate_pct
platform_revenue_gbp
disruption_rate_pct
refund_amount_gbp
commercial_value_at_risk_gbp
revenue_rank
risk_rank

Conditional formatting:
conversion_rate_pct = green high / red low
disruption_rate_pct = red high
commercial_value_at_risk_gbp = red high


Key finding:
Top revenue partner:
Rail Commerce Partner 027
Platform Revenue:
GBP 217,451.01

Highest-risk partner:
Rail Commerce Partner 026
Commercial Value at Risk:
GBP 248,326.88


============================================================
PAGE 3 — CUSTOMER & CONVERSION
============================================================

Primary tables:
03_conversion_funnel
04_customer_segments

Slicers:
sales_channel
customer_segment
business_traveller_flag
loyalty_tier


VISUAL 1

Type:
Clustered bar chart

Title:
Conversion Rate by Sales Channel

Table:
03_conversion_funnel

Axis:
sales_channel

Value:
conversion_rate_pct

Legend:
customer_segment


VISUAL 2

Type:
Horizontal bar chart

Title:
Customer Segments by Platform Revenue

Table:
04_customer_segments

Axis:
customer_segment

Value:
platform_revenue_gbp

Legend:
loyalty_tier


VISUAL 3

Type:
Scatter chart

Title:
Customer Segment Value vs Conversion

Table:
04_customer_segments

X-axis:
conversion_rate_pct

Y-axis:
platform_revenue_gbp

Size:
bookings

Details:
customer_segment

Legend:
loyalty_tier

Tooltip:
customers
searches
bookings
gross_booking_value_gbp
average_booking_value_gbp
refund_amount_gbp


VISUAL 4

Type:
Matrix

Title:
Conversion Opportunity Matrix

Table:
03_conversion_funnel

Fields:
sales_channel
customer_segment
business_traveller_flag
searches
bookings
conversion_rate_pct
average_lowest_fare_gbp
average_booking_lead_days

Conditional formatting:
conversion_rate_pct
Red = low
Green = high


Key findings:

Best-converting segment:
B2B Partner / Frequent Business
48.69%

Lowest-converting segment:
Mobile Web / Leisure Occasional
17.86%

Highest-value customer segment:
Frequent Business / Gold
GBP 1,539,058.74 platform revenue


============================================================
PAGE 4 — ROUTES & OPERATIONS
============================================================

Primary tables:
05_route_opportunity
06_operator_performance

Slicers:
operator_name
route_type
commercial_priority


KPI CARDS:

Total Journeys
2,000,000

Disruption Rate
11.23%

Cancellation Rate
3.74%

Within 3 Minutes
85.01%


VISUAL 1

Type:
Scatter chart

Title:
Route Revenue vs Operational Disruption

Table:
05_route_opportunity

X-axis:
disruption_rate_pct

Y-axis:
platform_revenue_gbp

Size:
bookings

Details:
route_id

Legend:
commercial_priority

Tooltip:
origin_station
destination_station
operator_name
searches
conversion_rate_pct
average_arrival_delay_minutes
within_3_minutes_pct


VISUAL 2

Type:
Horizontal bar chart

Title:
Top 10 Routes by Platform Revenue

Axis:
origin_station

Value:
platform_revenue_gbp

Tooltip:
destination_station
operator_name
bookings
conversion_rate_pct
disruption_rate_pct

Filter:
Top 10


VISUAL 3

Type:
Clustered bar chart

Title:
Operator Reliability Comparison

Table:
06_operator_performance

Axis:
operator_name

Values:
disruption_rate_pct
cancellation_rate_pct


VISUAL 4

Type:
Matrix

Title:
Priority Route Opportunities

Table:
05_route_opportunity

Fields:
origin_station
destination_station
operator_name
commercial_priority
searches
bookings
conversion_rate_pct
platform_revenue_gbp
disruption_rate_pct
average_arrival_delay_minutes
within_3_minutes_pct

Conditional formatting:
commercial_priority
disruption_rate_pct
conversion_rate_pct


Key findings:

Top revenue route:
RailPartner Station 034
to
RailPartner Station 008

Revenue:
GBP 27,534.26


Highest-disruption route:
RailPartner Station 094
to
RailPartner Station 061

Disruption:
14.38%


Primary conversion opportunity:
RailPartner Station 212
to
RailPartner Station 162


Highest-disruption operator:
Central Metro Rail
11.45%


Best operational performer:
Southern Coast Rail
11.09% disruption


============================================================
PAGE 5 — REFUND & COMMERCIAL RISK
============================================================

Primary table:
07_refund_impact

Slicers:
refund_type
refund_reason
sales_channel
business_traveller_flag


KPI CARD 1

Refund Records

Expected:
196,235


KPI CARD 2

Refund Amount

Expected:
GBP 9.18M


KPI CARD 3

Commercial Value at Risk

Expected:
GBP 9.72M


VISUAL 1

Type:
Horizontal bar chart

Title:
Commercial Value at Risk by Refund Reason

Axis:
refund_reason

Value:
commercial_value_at_risk_gbp

Sort:
Descending


VISUAL 2

Type:
Stacked bar chart

Title:
Refund Exposure by Type and Channel

Axis:
refund_type

Value:
refund_amount_gbp

Legend:
sales_channel


VISUAL 3

Type:
Scatter chart

Title:
Refund Processing Time vs Commercial Exposure

X-axis:
average_processing_days

Y-axis:
commercial_value_at_risk_gbp

Size:
refund_records

Details:
refund_reason

Legend:
refund_type


VISUAL 4

Type:
Matrix

Fields:
refund_type
refund_reason
sales_channel
business_traveller_flag
refund_records
eligible_value_gbp
refund_amount_gbp
commercial_value_at_risk_gbp
average_processing_days

Conditional formatting:
commercial_value_at_risk_gbp = red high
average_processing_days = amber/red high


Primary finding:

Largest refund driver:
Full Refund / Operator Cancellation

Commercial Value at Risk:
GBP 2,848,912.09


============================================================
DASHBOARD STORY
============================================================

The dashboard should communicate this sequence:

Commercial scale
→
Partner contribution
→
Customer conversion
→
Operational reliability
→
Commercial risk
→
Recommended action


============================================================
PORTFOLIO POSITIONING
============================================================

This dashboard demonstrates:

- B2B analytics
- Product analytics
- Commercial analytics
- Customer segmentation
- Conversion analysis
- Partner performance
- Operational analytics
- Revenue analytics
- Risk analytics
- SQL
- PostgreSQL
- dbt
- Python
- Power BI
- Analytics engineering
- Data storytelling
- Executive stakeholder reporting

All transactional data in RailPartner 360 is synthetic
portfolio data and does not represent Trainline proprietary data.
