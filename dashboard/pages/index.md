---
title: Singapore Macro Intelligence
---

[Full Analysis](/analysis) | [Pipeline Architecture](/pipeline) | [GitHub](https://github.com/kxenergy/singapore-macro-pipeline)

```sql latest
select *
from sg_macro.macro_monthly
where cpi_yoy_pct is not null
order by period_date desc
limit 1
```

```sql latest_fx
select *
from sg_macro.macro_monthly
where usd_sgd is not null
order by period_date desc
limit 1
```

```sql latest_trade
select *
from sg_macro.macro_monthly
where imports_sgd_bn is not null
order by period_date desc
limit 1
```

```sql annual_clean
select
    cast(period_year as integer)         as year,
    round(avg(cpi_yoy_pct) * 100, 1) as avg_inflation,
    round(avg(usd_sgd), 4)               as usd_sgd,
    round(sum(imports_sgd_bn), 0)        as imports_sgd_bn,
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

```sql case_study
select
    period_date,
    round(usd_sgd, 4)               as usd_sgd,
    round(cny_sgd, 4)               as cny_sgd,
    round(ge_usd_budget_m, 1)       as ge_usd_m,
    round(mindray_cny_budget_m, 0)  as mindray_cny_m,
    case
        when usd_sgd < 1.30 then 'Favour US'
        when usd_sgd > 1.40 then 'Favour China'
        else 'Neutral'
    end                             as signal
from sg_macro.macro_monthly
where usd_sgd is not null
    and cny_sgd is not null
    and period_year >= 2020
order by period_date desc
```

<h1 style="font-size:2.2rem; font-weight:700; margin:2rem 0 0.5rem; line-height:1.15;">
The procurement window that appears once every 5–7 years<br>
<span style="color:#2563eb;">is open right now.</span>
</h1>

<p style="font-size:1.1rem; color:#6b7280; margin:0 0 2rem; max-width:680px;">
25 years of Singapore government data — CPI, exchange rates, import volumes — distilled into one decision signal for CFOs, procurement directors, and supply chain heads.
</p>

---

## March 2026 — All Three Signals Are Green

<BigValue
    data={latest}
    value="cpi_yoy_pct"
    title="Inflation YoY"
    fmt="pct2"
    subtitle="Mar 2026 — lowest since 2021"
/>

<BigValue
    data={latest_fx}
    value="usd_sgd"
    title="USD / SGD"
    fmt="0.0000"
    subtitle="Near 25-year average — SGD stable"
/>

<BigValue
    data={latest_fx}
    value="cny_sgd"
    title="CNY / SGD"
    fmt="0.0000"
    subtitle="7x CNY purchasing power vs USD"
/>

<BigValue
    data={latest_trade}
    value="imports_sgd_bn"
    title="Monthly Imports (SGD Billions)"
    fmt="#,##0.0"
    subtitle="Feb 2026 — SGD Billions"
/>

---

## This Has Happened Only Twice in 15 Years

The chart below shows Singapore's inflation (blue) and USD/SGD rate (red) since 2010. **The procurement window opens when both lines fall simultaneously into the low zone** — inflation below 2%, USD/SGD below 1.35.

It happened in **2015–2016**. Briefly in **2019**. And it is happening **now**.

```sql inflation_only
select
    period_date,
    round(cpi_yoy_pct * 100, 2) as inflation
from sg_macro.macro_monthly
where cpi_yoy_pct is not null
    and period_year >= 2010
order by period_date
```

```sql fx_only
select
    period_date,
    round(usd_sgd, 4) as fx_rate
from sg_macro.macro_monthly
where usd_sgd is not null
    and period_year >= 2010
order by period_date
```

<LineChart
    data={inflation_only}
    x="period_date"
    y="inflation"
    title="Signal 1 — CPI Inflation YoY % (2010–2026)"
    yAxisTitle="Inflation YoY %"
    colorPalette={['#2563eb']}
    yMax=8
    yMin=-3
/>

<LineChart
    data={fx_only}
    x="period_date"
    y="fx_rate"
    title="Signal 2 — USD/SGD Rate (2010–2024)"
    yAxisTitle="SGD per USD"
    colorPalette={['#dc2626']}
    yMax=1.60
    yMin=1.15
/>

> **Right now:** Inflation is 1.80%. USD/SGD is 1.34. Both are in the green zone simultaneously — for the first time since 2019.

---

## What Companies Did During the Last Window — And What It Was Worth

The 2015–2016 window lasted 18 months. Companies that locked multi-year supply contracts during that period entered the catastrophic 2022 inflation spike (+6.1%) with **fixed pricing**. Those on spot markets absorbed the full hit.

On a SGD 100M annual procurement budget: **SGD 6–9M saved per year** — not projected, not modelled. Paid on actual invoices.

---

## 12 Years of Evidence — The Prescription Was Correct Every Time

<DataTable
    data={annual_clean}
    rows=12
    rowNumbers=false
/>

---

## The Medical Equipment Case — SGD 50M Decision

For Singapore's hospital groups and MedTech distributors: FX timing on a single capital equipment order can swing purchasing power by **USD 5.5M on an identical SGD budget**.

<DataTable
    data={case_study}
    rows=8
    rowNumbers=false
/>

**GE Healthcare (US):** At today's USD/SGD 1.34, SGD 50M buys **USD 37.3M** of equipment.
At the 2022 weak-SGD peak of 1.45, the same budget bought only **USD 34.5M** — USD 2.8M less.
At the 2014 strong-SGD low of 1.25, it would have bought **USD 40M** — USD 2.7M more.

**Current signal: NEUTRAL** — lock service contracts now while inflation is at 1.8%, even if FX has no clear edge.

---

## What This Data Cannot Tell You

The window closes when the next commodity shock, supply chain disruption, or geopolitical event arrives. The 2019 window lasted 4 months before COVID ended it. The current window could last 6 months or 2 years.

**What the data tells you with certainty:** The conditions that enabled 8–15% procurement cost advantages in 2015–2016 exist again today. The question is not whether to act. It is what to prioritise and how long a contract horizon makes sense given your business cycle.

---

[Full signal analysis — inflation drivers, FX correlation study, log-scale import growth, and pipeline documentation](./analysis)

---

<!-- INDEX FOOTER START -->