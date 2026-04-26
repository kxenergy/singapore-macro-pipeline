---
title: Pipeline Architecture — Singapore Macro Intelligence
---

[Executive Summary](/) | [Full Analysis](/analysis) | [GitHub](https://github.com/kxenergy/singapore-macro-pipeline)

```sql pipeline_stats
select 'SingStat' as source, 'CPI by category' as dataset, 'Monthly' as frequency, '1961' as since, 5000 as rows, 23 as categories
union all
select 'MAS', 'SGD exchange rates', 'Monthly', '1988', 5332, 15
union all
select 'Enterprise SG', 'Merchandise trade', 'Monthly', '1976', 42702, 75
```

```sql medallion_layers
select 'Bronze' as layer, 53034 as total_rows, 'Raw immutable data — exactly as received from API' as purpose
union all
select 'Silver', 53034, 'Cleaned, typed, renamed, unpivoted — no business logic'
union all
select 'Gold', 327, 'Joined analytical mart — tested, documented, query-ready'
```

```sql test_results
select 'not_null — period_date' as test_name, 'fct_sg_macro_monthly' as model, 'PASS' as status, 327 as rows_checked
union all select 'unique — period_date', 'fct_sg_macro_monthly', 'PASS', 327
union all select 'not_null — cpi_value', 'fct_sg_macro_monthly', 'PASS', 327
union all select 'not_null — cpi_category', 'stg_cpi', 'PASS', 5000
union all select 'not_null — period_date', 'stg_cpi', 'PASS', 5000
union all select 'not_null — cpi_value', 'stg_cpi', 'PASS', 5000
union all select 'not_null — currency_pair', 'stg_fx', 'PASS', 5332
union all select 'not_null — period_date', 'stg_fx', 'PASS', 5332
union all select 'not_null — sgd_per_foreign_unit', 'stg_fx', 'PASS', 5332
union all select 'accepted_values — currency_pair', 'stg_fx', 'PASS', 5332
union all select 'not_null — trade_type', 'stg_trade', 'PASS', 42702
union all select 'not_null — period_date', 'stg_trade', 'PASS', 42702
union all select 'not_null — trade_value', 'stg_trade', 'PASS', 42702
union all select 'accepted_values — trade_type', 'stg_trade', 'PASS', 42702
union all select 'not_null — period_year', 'fct_sg_macro_monthly', 'PASS', 327
```

```sql phase_tools
select 'Phase 1' as phase, 'Current' as status, 'Python 3.13' as tool, 'API ingestion, data extraction, retry logic' as role, 'Free' as cost
union all select 'Phase 1', 'Current', 'dbt Core', 'SQL transformation, testing, documentation', 'Free'
union all select 'Phase 1', 'Current', 'DuckDB', 'Local analytical warehouse, sub-second queries', 'Free'
union all select 'Phase 1', 'Current', 'Git + GitHub', 'Version control, code history, collaboration', 'Free'
union all select 'Phase 1', 'Current', 'Evidence.dev', 'Code-based dashboard, deployed to browser', 'Free'
union all select 'Phase 2', 'Next', 'Apache Airflow', 'Workflow orchestration, scheduling, alerting', 'Free/Cloud'
union all select 'Phase 2', 'Next', 'Great Expectations', 'Advanced data quality monitoring', 'Free'
union all select 'Phase 2', 'Next', 'BigQuery / Snowflake', 'Cloud warehouse for team access', 'Pay per query'
union all select 'Phase 2', 'Next', 'dbt Cloud', 'Hosted dbt with CI/CD and lineage UI', 'Commercial'
union all select 'Phase 2', 'Next', 'Metabase', 'Self-serve BI for business teams', 'Free/Commercial'
union all select 'Phase 3', 'Future', 'Spark / Databricks', 'Big data processing at massive scale', 'Commercial'
union all select 'Phase 3', 'Future', 'Kafka / Confluent', 'Real-time streaming data pipelines', 'Commercial'
union all select 'Phase 3', 'Future', 'Monte Carlo', 'Data observability and anomaly detection', 'Commercial'
union all select 'Phase 3', 'Future', 'Tableau / Power BI', 'Enterprise BI for executive reporting', 'Commercial'
union all select 'Phase 3', 'Future', 'dbt Semantic Layer', 'Unified business metrics definition', 'Commercial'
```

```sql rows_by_source
select 'CPI' as source, 5000 as rows
union all select 'FX Rates', 5332
union all select 'Trade', 42702
```

```sql data_quality_score
select '15 of 15' as tests_passing, '100' as pass_rate, '3' as sources_monitored, '5' as models_tested
```

[Back to Executive Summary](/) | [Back to Full Analysis](/analysis)

<h1 style="font-size:2rem; font-weight:700; margin:2rem 0 0.25rem; line-height:1.2;">
How this dashboard stays trustworthy<br>
<span style="color:#2563eb;">every single month, automatically.</span>
</h1>

<p style="font-size:1.05rem; color:#6b7280; margin:0 0 2rem; max-width:700px;">
A plain-language guide to the engineering that powers this dashboard — written for anyone who wants to understand how data moves from a government website to a business decision, without touching a single spreadsheet.
</p>

---

## The Problem This Pipeline Solves

Most business dashboards are built on spreadsheets downloaded manually, emailed around, and updated by one person who eventually leaves. When they leave, the dashboard dies — or worse, it keeps running with stale or wrong data that no one notices.

This pipeline is built differently. **No spreadsheets. No manual downloads. No single point of failure.** Every number on the Singapore Macro Intelligence dashboard was produced by an automated, tested, version-controlled system that runs the same way every month — whether or not the person who built it is available.

---

## Where the Data Comes From

Three official Singapore government sources, all publicly available, all free:

<DataTable
    data={pipeline_stats}
    rows=5
    rowNumbers=false
/>

**Total records processed:** 53,034 rows across 3 sources, spanning 65 years of Singapore economic history.

**Why government data?** Government statistical agencies are among the most reliable data publishers in the world. SingStat and MAS publish data on fixed schedules, maintain historical records, and correct errors publicly. This is the same data used by Singapore's banks, investment firms, and policy teams.

---

## The Pipeline in Plain Language

Think of the pipeline as a factory with three floors. Raw materials arrive at the ground floor. They get cleaned and shaped on the middle floor. The finished product — ready for use — comes off the top floor.

<BarChart
    data={medallion_layers}
    x="layer"
    y="total_rows"
    title="Data Volume at Each Medallion Layer"
    yAxisTitle="Total Rows"
    colorPalette={['#cd7f32', '#C0C0C0', '#FFD700']}
    xAxisTitle=""
/>

<DataTable
    data={medallion_layers}
    rows=5
    rowNumbers=false
/>

**Bronze — the ground floor:** Raw data lands exactly as it came from the government API. Nothing is changed. Nothing is deleted. Every row has a timestamp showing exactly when it was collected. If there is ever a question about what the source said on a specific date, the Bronze layer has the answer.

**Silver — the middle floor:** The raw data is cleaned up. Column names are made human-readable. Dates are converted to proper date formats. Numbers stored as text are converted to actual numbers. Data that was stored in a wide format (months as columns) is reshaped into a tall format that databases can query efficiently. This is where 90% of the technical data engineering work happens.

**Gold — the top floor:** The three cleaned datasets are joined together into a single table. Business calculations are added — year-on-year inflation percentage, exchange rate ratios, trade balance. This is what the dashboard queries. It is optimised for speed and clarity, not for storage efficiency.

---

## The Automated Quality Gates

Before any data reaches the dashboard, it passes through 15 automated tests. These tests run every time the pipeline executes. If any test fails, the pipeline stops and flags the error — it does not silently serve wrong data.

<DataTable
    data={test_results}
    rows=15
    rowNumbers=false
/>

**What these tests catch in the real world:**

If SingStat changes the format of their API response — a column renamed, a value changed from a number to text — the pipeline fails immediately and the error is logged. The dashboard shows the last verified data rather than corrupted new data. This is the engineering equivalent of a seatbelt: you hope you never need it, but you are very glad it is there.

---

## The Three-Phase Engineering Roadmap

This pipeline is built at Phase 1 — the foundation level. The same data architecture scales through two more phases as business needs grow. Each phase adds tools without rebuilding what came before.

<DataTable
    data={phase_tools}
    rows=15
    rowNumbers=false
/>

**Phase 1 — Foundation (this pipeline):** Everything runs locally on a laptop. Zero cloud costs. The entire pipeline from raw API to dashboard costs SGD 0 per month to operate. This is the proof-of-concept phase — validate the data, validate the business questions, validate the architecture before spending on infrastructure.

**Phase 2 — Team scale:** The pipeline moves to the cloud. Multiple analysts can query the same warehouse simultaneously. Airflow schedules runs automatically and sends alerts if something fails. A business team can explore the data in Metabase without writing SQL. Cost: approximately SGD 200–500 per month depending on data volume.

**Phase 3 — Enterprise scale:** Real-time streaming data, massive dataset processing, enterprise BI tools connected to a single verified source of truth. Cost: SGD 5,000–50,000 per month. Used by banks, logistics companies, and government analytics teams.

**The critical point for non-technical readers:** Moving from Phase 1 to Phase 3 does not mean rebuilding the pipeline. The same Bronze-Silver-Gold architecture, the same dbt transformation logic, the same data quality tests — all carry forward. The tools around them change. The engineering thinking does not.

---

## What Makes This Approach Different From a Spreadsheet

<DataTable
    data={
        [
            {aspect: "Data freshness", spreadsheet: "Manual download when someone remembers", pipeline: "Automated on schedule — never stale"},
            {aspect: "Error detection", spreadsheet: "Noticed when someone spots a wrong number", pipeline: "15 automated tests catch errors before they reach the dashboard"},
            {aspect: "Audit trail", spreadsheet: "Who changed what and when? Unknown.", pipeline: "Every change tracked in Git with timestamp and author"},
            {aspect: "Scale", spreadsheet: "Breaks above ~100,000 rows", pipeline: "DuckDB queries 1 billion rows on a laptop"},
            {aspect: "Collaboration", spreadsheet: "Emailed around, version confusion", pipeline: "GitHub — one source of truth, full history"},
            {aspect: "Reproducibility", spreadsheet: "Cannot recreate last month's numbers exactly", pipeline: "Any historical state can be recreated from Git history"},
            {aspect: "Trust", spreadsheet: "Trusted because someone built it", pipeline: "Trusted because tests prove it is correct"}
        ]
    }
    rows=10
    rowNumbers=false
/>

---

## The Skills Behind This Pipeline

This project demonstrates five competencies that define a professional data engineer:

**1. Data ingestion engineering** — writing Python scripts that handle real-world API behaviour: rate limits, server errors, authentication, pagination, and changing data formats. The three ingestion scripts in this project handle all of these automatically without human intervention.

**2. Data modelling** — designing how data is structured so it can answer business questions efficiently. The Bronze-Silver-Gold architecture used here is the industry standard at companies including Airbnb, Databricks, and DBS Bank.

**3. Data quality engineering** — writing automated tests that run on every pipeline execution, catching problems before they reach business users. Most junior engineers skip this step. Senior engineers know it is the most important step.

**4. Analytics engineering** — translating business questions into SQL logic that is readable, testable, and maintainable. The dbt models in this project are documented, version-controlled, and can be understood by a colleague who has never seen them before.

**5. Data product thinking** — building something that a non-technical business user can trust and use to make decisions, not just a technical demonstration. This dashboard is the output of that thinking.

---

## The Architecture in One Diagram

**Extract:** SingStat API (CPl) → Python + exponential backoff → Bronze layer

**Extract:** MAS via data.gov.sg (FX) → Python + pagination → Bronze layer

**Extract:** Enterprise SG (Trade) → Python + idempotent load → Bronze layer

**Transform:** Bronze → dbt Core (5 models, 15 tests) → Silver → Gold

**Serve:** Gold layer → DuckDB → Evidence.dev dashboard

## Why This Matters for Your Business

The Singapore Macro Intelligence dataset is one example. The same pipeline architecture, the same engineering patterns, the same quality guarantees apply to any business dataset:

**Healthcare:** Patient admission records, drug procurement costs, equipment utilisation rates — all structured the same way, all tested the same way, all queryable from the same dashboard framework.

**Commodities and shipping:** Port throughput data, commodity spot prices, freight indices — the pipeline does not care what the data represents, only that it is correctly structured and verified.

**GovTech:** Public service delivery metrics, census data, budget utilisation — government data is already publicly available and structured for exactly this kind of pipeline.

**Finance and banking:** Transaction volumes, FX exposure, risk metrics — the Bronze-Silver-Gold architecture was pioneered by financial services data teams for exactly these use cases.

The business intelligence layer changes for every client and every problem. The data engineering foundation beneath it — this pipeline — remains the same.

---

<p style="font-size:0.85rem; color:#9ca3af; margin-top:2rem; line-height:1.8;">
Built with: Python 3.13 · dbt Core 1.11 · DuckDB 1.2 · Evidence.dev · Git + GitHub Actions<br>
Architecture: Medallion (Bronze/Silver/Gold) · ELT pattern · Test-driven data quality<br>
Pipeline last executed: April 2026 · 15 of 15 tests passing · 5 models · 53,034 rows processed<br>
<a href="https://github.com/kxenergy/singapore-macro-pipeline">github.com/kxenergy/singapore-macro-pipeline</a>
</p>