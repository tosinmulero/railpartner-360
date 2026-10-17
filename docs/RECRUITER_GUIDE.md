# Recruiter evidence guide — RailPartner 360 — B2B Rail Retail & Customer Intelligence

[**Full case study on Mulero Analytics**](https://tosinmulero.github.io/data-analytics-portfolio/case-studies/railpartner-360.html) · [Repository README](../README.md) · [Main portfolio](https://tosinmulero.github.io/data-analytics-portfolio/projects.html)

> **Data provenance:** Synthetic rail retail transactions. No proprietary Trainline customer, operator or partner information.

## The question

How can rail search, booking, partner, route and refund records become a coherent management-reporting model?

## Technical approach

- Prepare, validate and model transactional data with Python and PostgreSQL.
- Use dbt analytics engineering and a governed Power BI semantic model.
- Present partner, customer, revenue, disruption and refund insights.

## Documented results to review

- 6 million searches and 2 million bookings in the generated example.
- 33.33% overall search-to-booking conversion and 63.86% B2B booking share.
- £9.03M simulated platform revenue across a five-page Power BI analytical experience.

## Evidence map

| Review item | Source | What it supports |
|---|---|---|
| Executive dashboard | [Open](../docs/screenshots/01_executive_overview.png) | Headlines and KPI relationships |
| Partner performance | [Open](../docs/screenshots/02_partner_performance.png) | B2B metrics in the report |
| Refunds and risk | [Open](../docs/screenshots/05_refund_commercial_risk.png) | Operational-commercial exposure |
| Dashboard specification | [Open](../powerbi/docs/dashboard_specification.md) | Report design and definitions |

## Reproducibility and limitations

Consult the README and dashboard specification for the SQL/dbt workflow, BI model and recorded quality checks. Outputs are synthetic portfolio measures rather than real commercial results.

The repository README and linked source files remain the primary technical record. Numbers in this guide summarise the documented project artefacts; they are not claims of a third-party deployment, independently verified business impact or a live customer engagement.

## Reviewer path

1. Scan the [portfolio case study](https://tosinmulero.github.io/data-analytics-portfolio/case-studies/railpartner-360.html) for the problem and conclusions.
2. Open the main visual and supporting artefacts from the evidence map.
3. Review the repository README for tooling, methods, reproducibility instructions and limitations.
4. Inspect the code and workflows if deeper technical assurance is required.

---

*Independent portfolio work by Oluwatosin Mulero. Technical details and evidence are maintained in this repository.*
