---
title: Full Signal Analysis — Singapore Macro Intelligence
---

[Executive Summary](/) | [Pipeline Architecture](/pipeline) | [GitHub](https://github.com/kxenergy/singapore-macro-pipeline)

```sql cpi_history
select
    period_date,
    round(cpi_yoy_pct * 100, 2) as cpi_yoy
from sg_macro.macro_monthly
where cpi_yoy_pct is not null
order by period_date
```

```sql fx_history
select
    period_date,
    round(usd_sgd, 4) as usd_sgd,
    round(cny_sgd, 4) as cny_sgd,
    round(usd_cny_ratio, 2) as usd_cny_ratio
from sg_macro.macro_monthly
where usd_sgd is not null
order by period_date
```

```sql trade_history
select
    period_date,
    round(imports_sgd_bn, 1) as imports_sgd_bn
from sg_macro.macro_monthly
where imports_sgd_bn is not null
order by period_date
```

```sql log_imports
select
    period_date,
    round(ln(imports_sgd_bn), 3) as imports_log
from sg_macro.macro_monthly
where imports_sgd_bn is not null
    and imports_sgd_bn > 0
order by period_date
```

```sql scatter_data
select
    period_date,
    round(usd_sgd, 4) as usd_sgd,
    round(cpi_yoy_pct * 100, 2) as cpi_inflation,
    case
        when cpi_yoy_pct > 0.04  then 'High above 4pct'
        when cpi_yoy_pct > 0.02  then 'Moderate 2 to 4pct'
        when cpi_yoy_pct >= 0    then 'Low 0 to 2pct'
        else                          'Deflation below 0'
    end as inflation_regime
from sg_macro.macro_monthly
where usd_sgd is not null
    and cpi_yoy_pct is not null
order by period_date
```

```sql case_study
select
    period_date,
    round(usd_sgd, 4)              as usd_sgd,
    round(cny_sgd, 4)              as cny_sgd,
    round(ge_usd_budget_m, 1)      as ge_usd_m,
    round(mindray_cny_budget_m, 0) as mindray_cny_m,
    case
        when usd_sgd < 1.30 then 'Favour US'
        when usd_sgd > 1.40 then 'Favour China'
        else 'Neutral'
    end as signal
from sg_macro.macro_monthly
where usd_sgd is not null
    and cny_sgd is not null
    and period_year >= 2020
order by period_date desc
```

```sql annual
select
    cast(period_year as integer)         as year,
    round(avg(cpi_yoy_pct) * 100, 1)    as avg_cpi_yoy,
    round(avg(usd_sgd), 4)               as usd_sgd,
    round(sum(imports_sgd_bn), 0)        as total_imports_sgd_bn,
    case
        when avg(cpi_yoy_pct) > 0.04  then 'HIGH'
        when avg(cpi_yoy_pct) > 0.02  then 'ELEVATED'
        when avg(cpi_yoy_pct) >= 0    then 'STABLE'
        else                               'DEFLATION'
    end                                  as regime,
    case
        when avg(cpi_yoy_pct) > 0.04  then 'Lock prices. Hedge FX. Accelerate orders.'
        when avg(cpi_yoy_pct) > 0.02  then 'Review contracts. Monitor USD/SGD monthly.'
        when avg(cpi_yoy_pct) >= 0    then 'Negotiate hard. Lock multi-year deals now.'
        else                               'Spot buy. Extend terms. Hold inventory light.'
    end                                  as prescribed_action
from sg_macro.macro_monthly
where usd_sgd is not null
    and imports_sgd_bn is not null
group by period_year
order by period_year desc
limit 12
```

**Three signals, one decision framework:**

**Signal 1 — CPI Inflation** — how fast your cost floor is rising. Below 2%: negotiate and delay. Above 4%: lock prices immediately.

**Signal 2 — USD/SGD and CNY/SGD** — what your SGD buys in each market this month. A 10% SGD weakening against USD equals a 10% price increase on all US-sourced goods before your supplier quotes you anything.

**Signal 3 — Import Volumes** — what the entire market is doing. Rising volumes mean competitors are building stock, lead times will extend. Falling volumes mean suppliers need your order — maximum leverage.

---

## Signal 1 — Inflation: Your Cost Floor

<LineChart
    data={cpi_history}
    x="period_date"
    y="cpi_yoy"
    title="Singapore CPI — Year-on-Year % Change (1999–2026)"
    yAxisTitle="YoY % Change"
    colorPalette={['#2563eb']}
    yMax=8
    yMin=-3
/>

**2008 peak +7.2%** — Global commodity supercycle. Fixed-price contracts signed pre-2007 saved 12–18% vs spot buyers.

**2015–2016 at -1.1%** — Oil crash deflation window. Optimal moment to renegotiate supplier contracts. Most teams were too cautious to act.

**2022 peak +6.1%** — Post-COVID supply shock plus Ukraine commodity surge. Dual-source supply chains maintained continuity. Single-source buyers paid 20–40% spot premiums with 6–12 month lead time extensions.

**2026 at +1.8%** — Cooling within MAS target. Supplier capacity available. This is the negotiation window.

**Counter-intuitive finding:** Singapore's inflation correlates more with global commodity prices than with the SGD exchange rate. MAS's active SGD management absorbs much of the FX-inflation transmission. Watch Brent crude and DRAM spot prices — not just MAS policy.

---

## Signal 2 — Currency: The Silent Price Multiplier

<LineChart
    data={fx_history}
    x="period_date"
    y={["usd_sgd", "cny_sgd"]}
    title="USD/SGD vs CNY/SGD — SGD Cost Per Foreign Currency Unit (1999–2024)"
    yAxisTitle="SGD per Foreign Unit"
    colorPalette={['#2563eb', '#dc2626']}
/>

The USD/SGD line has held between 1.25 and 1.45 for 25 years — MAS policy, not coincidence. The CNY/SGD line shows the RMB's dramatic strengthening from 2005–2014. Chinese goods have become structurally more expensive in SGD terms over 20 years — though they remain far cheaper in absolute cost per unit than US equivalents.

**The USD/CNY Relative Sourcing Power Ratio:**

<LineChart
    data={fx_history}
    x="period_date"
    y="usd_cny_ratio"
    title="Relative Sourcing Power — How Many CNY Does 1 SGD Buy vs 1 USD (1999–2024)"
    yAxisTitle="CNY per USD via SGD"
    colorPalette={['#7c3aed']}
    yMin=5
    yMax=10
/>

When ratio is above 7.5 — China is relatively cheaper, favour Chinese suppliers. When falling — Chinese cost advantage is compressing, reassess US and ASEAN alternatives. Current ratio approximately 7.0 in 2024, down from 8.0 in 2005. China's cost advantage has compressed 12% in SGD terms over 20 years.

---

## The Medical Equipment Case Study

GE Healthcare (USA) vs Mindray (China) — SGD 50M capital equipment budget. Only variable: FX timing.

<DataTable
    data={case_study}
    rows=12
    rowNumbers=false
/>

At USD/SGD 1.45 (2022 peak): SGD 50M buys **USD 34.5M** of GE equipment.
At USD/SGD 1.25 (2014 low): same budget buys **USD 40.0M** — USD 5.5M more purchasing power on identical spend.
For a hospital group on a 3-year capital cycle: the difference between 6 MRI units upgraded or 7.

---

## Signal 3 — Import Volumes: What the Market Is Doing

<BarChart
    data={trade_history}
    x="period_date"
    y="imports_sgd_bn"
    title="Singapore Monthly Merchandise Imports — SGD Billions (1999–2026)"
    yAxisTitle="SGD Billions"
    colorPalette={['#0ea5e9']}
/>

**2009 GFC** — Imports fell 30%. Companies placing 18-month orders in Q2 2009 locked pricing before the 2010–2011 recovery surge.

**2016 oil crash** — Imports fell 18%. Forward contracts signed in 2016 entered 2017's stable period with protected input costs.

**2020 COVID** — Imports fell 22%. The counter-cyclical window lasted 4 months. Companies that acted avoided 2021–2022 shortage premiums entirely.

**Log-scale view — reveals growth rate, not just level:**

<LineChart
    data={log_imports}
    x="period_date"
    y="imports_log"
    title="Import Growth Rate — Log Scale. Straight Line Equals Constant Percentage Growth."
    yAxisTitle="ln(SGD Billions)"
    colorPalette={['#0ea5e9']}
/>

Singapore's import growth rate has been slowing since 2012. The era of automatic volume growth is over. Margin management now matters more than volume capture.

---

## Correlation Analysis — Does Weak SGD Cause Inflation?

<ScatterPlot
    data={scatter_data}
    x="usd_sgd"
    y="cpi_inflation"
    series="inflation_regime"
    title="USD/SGD vs CPI Inflation — 300 Months of Data (1999–2024)"
    xAxisTitle="USD/SGD Rate — higher means weaker SGD"
    yAxisTitle="CPI Inflation YoY %"
    yMax=8
    yMin=-3
/>

High inflation periods are scattered across the full range of USD/SGD values — not concentrated in weak-SGD periods. Singapore's inflation is commodity-driven, not currency-driven. Track Brent crude futures, Baltic Dry Index, and USD/SGD simultaneously — when all three move adversely together, procurement costs spike hardest.

---

## Annual Scorecard — 12 Years of Prescribed Actions

<DataTable
    data={annual}
    rows=12
    rowNumbers=false
/>

Companies following the 2020 DEFLATION signal and locking contracts saved 15–25% on input costs entering 2022. Those ignoring the 2021 ELEVATED signal and continuing spot-buying absorbed the full 2022 HIGH PRESSURE spike.

---

## Pipeline Architecture

This dashboard is a data product — automated, tested, versioned, trusted.

15 automated dbt tests validate every source record before it reaches this page. Idempotent ingestion scripts prevent duplicate data. Every raw record carries an ingestion timestamp — full audit trail from government API to dashboard. Schema changes in source APIs fail loudly rather than silently serving wrong numbers.

**Extract:** SingStat API (CPI) — Python + exponential backoff — Bronze layer

**Extract:** MAS via data.gov.sg (FX) — Python + pagination — Bronze layer  

**Extract:** Enterprise SG (Trade) — Python + idempotent load — Bronze layer

**Transform:** Bronze to Silver to Gold — dbt Core, 5 models, 15 tests

**Serve:** Gold layer — DuckDB — Evidence.dev dashboard

The same patterns are used by data teams at DBS Bank, GovTech Singapore, and commodity trading firms running production analytical systems.

**Data sources:** SingStat CPI (monthly since 1961) · MAS via data.gov.sg (15 currencies since 1988) · Enterprise Singapore via data.gov.sg (merchandise trade since 1976)

**Pipeline last executed:** April 2026 · Tests: 15 of 15 passing · Models: 5

[View full source code, architecture, and test results on GitHub](https://github.com/kxenergy/singapore-macro-pipeline)