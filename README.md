# Singapore Macro Intelligence Pipeline

An end-to-end, production-grade data engineering pipeline ingesting, transforming, 
testing and serving Singapore macroeconomic data as a live strategic business dashboard.

## What This Project Demonstrates

This is not a tutorial exercise. It is a working data product — built with the same 
architectural patterns used by data teams at DBS Bank, GovTech Singapore, and global 
commodity trading firms — running on a zero-cost local stack.

**The business output:** A three-page dashboard that answers one question for CFOs, 
procurement directors, and supply chain heads: *given current macro conditions, what 
is the optimal procurement posture for a Singapore business this month?*

**The engineering output:** A tested, versioned, automated pipeline that produces 
trustworthy numbers every month without manual intervention — and scales to enterprise 
infrastructure without rebuilding a single model.

---

## The Dashboard

Three pages. Three audiences.

**[Executive Summary](http://localhost:3000)** — The business verdict. One headline, 
four live signals, two charts, one actionable conclusion. Built for a CFO who has 
90 seconds.

**[Full Signal Analysis](http://localhost:3000/analysis)** — Deep dive into all three 
signals: CPI inflation drivers, FX sourcing decisions, import volume cycles, 
correlation analysis, and a 12-year annual scorecard with prescribed actions. 
Built for the analyst who wants to understand the data.

**[Pipeline Architecture](http://localhost:3000/pipeline)** — Plain-language 
explanation of how the pipeline works, why it is trustworthy, what the three 
engineering phases look like, and how this approach differs from a spreadsheet. 
Built for a recruiter or non-technical stakeholder who wants to understand the 
engineering thinking.

---

## Architecture — Phase 1 (Current)

EXTRACT                         TRANSFORM                    SERVE
───────                         ─────────                    ─────
SingStat API (CPI)              Bronze Layer                 Gold Layer
5,000 rows                    Raw immutable data           fct_sg_macro_monthly
23 categories                 Ingestion timestamps         327 joined rows
1961 → 2026      ──────────►  Never modified   ──────────► Tested & documented
MAS / data.gov.sg               Silver Layer                 Evidence.dev
5,332 rows                    Typed columns                3-page dashboard
15 currencies                 Renamed fields               Live at localhost:3000
1988 → 2024      ──────────►  Unpivoted rows   ──────────►
Business logic               GitHub Actions
Enterprise SG                                                Monthly schedule
42,702 rows                   dbt Core                     Auto-runs on push
75 categories                 5 models
1976 → 2026      ──────────►  15 quality tests ──────────►

### Medallion Layers

| Layer | Tables | Rows | Purpose |
|---|---|---|---|
| Bronze | 3 | 53,034 | Raw data — immutable, timestamped, never modified |
| Silver | 3 | 53,034 | Cleaned, typed, renamed, unpivoted |
| Gold | 2 | 327 | Joined analytical mart — tested, documented, query-ready |

### Data Sources

| Source | Dataset | Frequency | Since | Rows |
|---|---|---|---|---|
| SingStat | CPI by category (23 categories) | Monthly | 1961 | 5,000 |
| MAS via data.gov.sg | SGD exchange rates (15 currencies) | Monthly | 1988 | 5,332 |
| Enterprise SG via data.gov.sg | Merchandise imports and exports | Monthly | 1976 | 42,702 |

### Phase 1 Stack — Zero Cost

| Tool | Version | Role |
|---|---|---|
| Python | 3.13 | API ingestion, retry logic, data export |
| dbt Core | 1.11 | SQL transformation, testing, documentation |
| DuckDB | 1.2 | Local analytical warehouse |
| Git + GitHub | — | Version control, audit trail |
| GitHub Actions | — | Monthly pipeline scheduling |
| Evidence.dev | — | Code-based dashboard |

---

## Key Engineering Patterns

### Ingestion — Production-Grade from Day One

**Exponential backoff** — API rate limits (429 errors) are handled automatically. 
The pipeline retries with increasing wait times: 1s, 2s, 4s, 8s, 16s. No manual 
intervention required.

**Idempotent loads** — Running the pipeline twice on the same day produces identical 
results. The delete-before-insert pattern prevents duplicate data regardless of how 
many times scripts execute.

**Pagination** — Multi-page API responses are handled automatically. The pipeline 
fetches all pages before loading, regardless of dataset size.

**Unpivot / melt** — Government APIs return data in wide format (months as columns). 
The transform layer reshapes to long format (one row per observation) that SQL 
can query efficiently.

**Audit timestamps** — Every Bronze row records exactly when it was ingested. 
Full traceability from government API response to dashboard number.

**Structured logging** — Every pipeline run produces a dated log file. Errors are 
captured with full stack traces. Silent failures are not possible.

### Transformation — dbt Models

models/
├── staging/                    # Silver layer — one model per source
│   ├── sources.yml             # Source definitions and freshness checks
│   ├── schema.yml              # Column tests and descriptions
│   ├── stg_cpi.sql             # CPI: parse dates, cast types, YoY window function
│   ├── stg_fx.sql              # FX: filter key currencies, add inverse rate
│   └── stg_trade.sql           # Trade: unpivot, filter totals, cast values
└── marts/                      # Gold layer — joined analytical tables
├── schema.yml              # Data quality tests on final output
├── dim_calendar.sql        # Date dimension with quarter, season, month name
└── fct_sg_macro_monthly.sql # Central fact table joining all three sources

### Data Quality — 15 Automated Tests

Every pipeline run validates:
- No null values in critical columns across all 5 models
- Unique period dates in the Gold mart (no duplicate months)
- Accepted values for trade type (imports, exports only)
- Accepted values for currency pair (7 key currencies only)

If any test fails, the pipeline stops. The dashboard serves the last verified data 
rather than silently propagating corrupted numbers.

### Window Functions — Analytical Value in SQL

```sql
-- Month-over-month and year-over-year CPI change
-- calculated directly in dbt — no Python, no pandas, no manual Excel

cpi_value - lag(cpi_value) over (
    partition by cpi_category
    order by period_date
) as cpi_mom_change,

(cpi_value - lag(cpi_value, 12) over (
    partition by cpi_category
    order by period_date
)) / nullif(lag(cpi_value, 12) over (
    partition by cpi_category
    order by period_date
), 0) * 100 as cpi_yoy_pct
```

---

## Running the Pipeline

### Prerequisites
```bash
python --version    # 3.10 or higher
dbt --version       # 1.11 or higher  
node --version      # 18 or higher (for dashboard)
```

### Install dependencies
```bash
pip install dbt-core dbt-duckdb duckdb requests pandas
cd dashboard && npm install
```

### Configure dbt connection
Create `~/.dbt/profiles.yml`:
```yaml
sg_macro_dbt:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: /path/to/singapore_macro_pipeline/data/warehouse/sg_macro.duckdb
      threads: 4
```

### Run the full pipeline
```bash
# Step 1 — Ingest all three sources
cd ingestion
python ingest_cpi.py
python ingest_mas_fx.py
python ingest_trade.py

# Step 2 — Transform and test
cd ../sg_macro_dbt
dbt run
dbt test

# Step 3 — Export for dashboard
cd ../ingestion
python export_csv.py

# Step 4 — Load dashboard sources
cd ../dashboard
npm run sources

# Step 5 — View dashboard
npm run dev
# Open http://localhost:3000
```

### Generate documentation
```bash
cd sg_macro_dbt
dbt docs generate
dbt docs serve
# Open http://localhost:8080 — full lineage graph
```

---

## Project Structure

singapore_macro_pipeline/
├── .github/
│   └── workflows/
│       └── pipeline.yml        # GitHub Actions — runs dbt on schedule
├── ingestion/                  # Python extraction scripts
│   ├── ingest_cpi.py           # SingStat CPI API
│   ├── ingest_mas_fx.py        # MAS exchange rates via data.gov.sg
│   ├── ingest_trade.py         # Enterprise SG trade via data.gov.sg
│   ├── export_csv.py           # Export Gold mart to CSV for dashboard
│   └── verify_db.py            # Bronze layer verification script
├── sg_macro_dbt/               # dbt project
│   └── models/
│       ├── staging/            # Silver layer (3 models)
│       └── marts/              # Gold layer (2 models)
├── dashboard/                  # Evidence.dev dashboard
│   ├── pages/
│   │   ├── index.md            # Executive summary
│   │   ├── analysis.md         # Full signal analysis
│   │   └── pipeline.md        # Pipeline architecture
│   └── sources/
│       └── sg_macro/           # CSV data source for dashboard
├── data/
│   └── warehouse/              # DuckDB database (gitignored)
├── logs/                       # Pipeline execution logs (gitignored)
└── README.md

---

## Design Decisions and Trade-offs

**DuckDB over cloud warehouse (Phase 1):** For a pipeline processing 53,000 rows, 
DuckDB delivers full analytical SQL capability at zero cost and zero latency. 
The same dbt models run unchanged against Snowflake or BigQuery by updating 
`profiles.yml` only — no model rewrites required.

**CSV export for dashboard:** Evidence.dev's DuckDB connector has compatibility 
issues with Node v24. The CSV export pattern is a pragmatic workaround that 
adds one explicit step (run `export_csv.py` before `npm run sources`) but 
keeps the dashboard stack fully functional. Resolved in Phase 2 by moving 
to a cloud warehouse with a stable JDBC connector.

**Domestic exports only:** The data.gov.sg exports dataset covers domestic exports, 
not re-exports. Singapore's entrepot re-export trade is substantial and would be 
added in Phase 2 using a separate SingStat table, giving a complete trade balance picture.

**Manual scheduling (Phase 1):** Scripts run manually or via GitHub Actions. 
The ingestion scripts are idempotent and logged — drop-in ready for any 
orchestrator. Airflow or Dagster integration is the first Phase 2 upgrade.

---

## Roadmap

### Phase 1 — Foundation (Complete)
Local stack. Zero cost. Proof of concept validated.

- [x] Three government APIs ingested with production-grade error handling
- [x] Medallion architecture (Bronze, Silver, Gold)
- [x] dbt transformation with 15 automated quality tests
- [x] Star schema (fct_ + dim_ naming convention)
- [x] Three-page Evidence.dev dashboard
- [x] GitHub Actions CI/CD workflow
- [x] Full lineage graph via dbt docs

### Phase 2 — Team Scale (Next)
Move to cloud. Enable collaboration. Add orchestration.

- [ ] Migrate DuckDB to BigQuery or Snowflake (free tier)
- [ ] Add Apache Airflow for pipeline orchestration and alerting
- [ ] Integrate Great Expectations for advanced data quality monitoring
- [ ] Add SingStat re-exports dataset for complete trade balance
- [ ] Add Brent crude and Baltic Dry Index as external signals
- [ ] Deploy Evidence dashboard to Netlify or GitHub Pages (public URL)
- [ ] Connect Metabase for self-serve BI exploration
- [ ] Add dbt sources freshness checks and Slack alerting

### Phase 3 — Enterprise Scale (Future)
Real-time data. Enterprise tooling. Production SLAs.

- [ ] Kafka or Confluent for real-time streaming ingestion
- [ ] Spark or Databricks for large-scale batch processing
- [ ] dbt Cloud with hosted CI/CD, semantic layer, and lineage UI
- [ ] Monte Carlo or Soda for data observability and anomaly detection
- [ ] Tableau or Power BI connected to verified Gold mart
- [ ] dbt Semantic Layer for unified business metrics definition
- [ ] Row-level security and data access governance
- [ ] SLA monitoring and automated incident response

**The critical design principle across all three phases:** The Bronze-Silver-Gold 
architecture, dbt transformation logic, and data quality tests defined in Phase 1 
carry forward unchanged. Phases 2 and 3 add infrastructure around the foundation — 
they do not replace it. This is what makes Phase 1 worth doing correctly.

---

## What This Project Demonstrates for Hiring

| Competency | Evidence in this project |
|---|---|
| Data ingestion engineering | 3 production scripts with backoff, pagination, idempotency |
| Data modelling | Medallion architecture, star schema, dimensional modelling |
| Data quality engineering | 15 automated dbt tests, audit timestamps, loud failure mode |
| Analytics engineering | CTE-based SQL, window functions, documented models |
| Data product thinking | Business-oriented dashboard a non-technical user can trust |
| Version control | Git history, branching, meaningful commit messages |
| CI/CD | GitHub Actions workflow running on schedule and push |
| Cross-industry relevance | Healthcare, GovTech, commodities, shipping, fintech framing |

---

## Data Sources and Licensing

All data is sourced from official Singapore government APIs under the 
[Singapore Open Data Licence](https://data.gov.sg/open-data-licence) — 
free for personal and commercial use.

- **SingStat TableBuilder** — Singapore Department of Statistics
- **MAS via data.gov.sg** — Monetary Authority of Singapore  
- **Enterprise Singapore via data.gov.sg** — Enterprise Singapore

---

*Phase 1 complete — April 2026*  
*Pipeline status: All 15 tests passing · 5 models · 53,034 rows processed*  
*Built with: Python 3.13 · dbt Core 1.11 · DuckDB 1.2 · Evidence.dev · GitHub Actions*