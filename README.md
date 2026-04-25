# Singapore Macro Intelligence Pipeline

An end-to-end data engineering pipeline ingesting, transforming and serving
Singapore macroeconomic data for analytical use.

## Business Context

Singapore's economy is uniquely sensitive to three interconnected signals:
**inflation** (CPI), **currency strength** (SGD exchange rates), and
**trade volumes** (merchandise imports and exports). This pipeline makes
all three signals available in a single, tested, production-grade Gold table
updated on demand.

Relevant to: GovTech, commodities trading, healthcare procurement,
shipping and logistics, and any business with SGD-denominated import exposure.

## Architecture
SingStat API  ──►  ingest_cpi.py   ──►  bronze_cpi_raw   ──►  stg_cpi   ──►
MAS / data.gov.sg ► ingest_mas_fx.py ──►  bronze_fx_raw  ──►  stg_fx    ──►  mart_sg_macro
data.gov.sg   ──►  ingest_trade.py ──►  bronze_trade_raw ──►  stg_trade ──►

### Medallion layers
| Layer | Location | Purpose |
|---|---|---|
| Bronze | DuckDB `main.*` | Raw immutable data with ingestion timestamps |
| Silver | DuckDB `main_staging.*` | Typed, renamed, unpivoted, business-ready |
| Gold | DuckDB `main_marts.*` | Joined analytical mart, tested, query-ready |

## Data Sources

| Source | Dataset | Frequency | Rows |
|---|---|---|---|
| SingStat | CPI by category | Monthly | 5,000 |
| MAS via data.gov.sg | SGD exchange rates, 15 currencies | Monthly | 5,332 |
| Enterprise SG via data.gov.sg | Merchandise imports & domestic exports | Monthly | 42,702 |

## Tech Stack

| Tool | Role |
|---|---|
| Python 3.13 | Ingestion scripts |
| DuckDB | Local analytical warehouse |
| dbt Core | Transformation, testing, documentation |
| Git + GitHub | Version control |

## Key Engineering Patterns

- **Idempotent loads** — delete-before-insert prevents duplicate data on reruns
- **Exponential backoff** — automatic retry on API rate limits (429 errors)
- **Pagination** — handles multi-page API responses automatically
- **Unpivot / melt** — reshapes wide government data to long analytical format
- **Window functions** — MoM and YoY CPI change calculated in SQL
- **dbt tests** — 15 automated data quality tests across all models
- **Audit timestamps** — every Bronze row records when it was ingested

## Gold Mart — `mart_sg_macro`

327 monthly rows covering 1999–2026 with:
- CPI value, month-over-month change, year-over-year %
- USD/SGD and CNY/SGD exchange rates
- Total merchandise imports and domestic exports
- Derived trade balance

## Running the Pipeline

```bash
# Ingest all three sources
cd ingestion
python ingest_cpi.py
python ingest_mas_fx.py
python ingest_trade.py

# Run all dbt transformations
cd ../sg_macro_dbt
dbt run

# Run data quality tests
dbt test

# View documentation and lineage
dbt docs generate && dbt docs serve
```

## Project Structure
singapore_macro_pipeline/
├── ingestion/          # Python ingestion scripts
│   ├── ingest_cpi.py
│   ├── ingest_mas_fx.py
│   └── ingest_trade.py
├── sg_macro_dbt/       # dbt project
│   └── models/
│       ├── staging/    # Silver layer — stg_cpi, stg_fx, stg_trade
│       └── marts/      # Gold layer — mart_sg_macro
├── data/
│   └── warehouse/      # DuckDB database (gitignored)
└── logs/               # Ingestion logs (gitignored)

## Design Decisions & Trade-offs

**DuckDB over cloud warehouse** — For a portfolio pipeline processing <50k rows,
DuckDB delivers full analytical SQL capability at zero cost and zero latency.
At 10x data volume the same dbt models run unchanged against Snowflake or
BigQuery by updating `profiles.yml` only.

**No orchestrator yet** — Scripts run manually or via OS scheduler. At production
scale, Dagster or Airflow would manage dependencies and alerting.
The ingestion scripts are already idempotent and logged — drop-in ready
for any orchestrator.

**Domestic exports only** — The data.gov.sg exports dataset covers domestic
exports, not re-exports. Singapore's entrepot re-export trade is substantial
and would be added in a production version using a separate SingStat table.

## Day 1 Built Summary Log

3 live government APIs ingested         ✓
52,034 rows across 3 Bronze tables      ✓
Exponential backoff + retry logic       ✓
Idempotent pipeline — safe to rerun     ✓
Medallion architecture implemented      ✓
4 dbt models with full lineage          ✓
15 automated data quality tests         ✓
327 rows of joined macro intelligence   ✓
Portfolio README written                ✓
Everything on GitHub                    ✓