{{ config(materialized='table') }}

/*
    Gold layer: Singapore Macro Intelligence Mart
    Joins CPI + FX + Trade into a single analytical table
    aligned on month and year.

    Business value:
    - Shows how import costs (trade) relate to inflation (CPI)
    - Shows how currency strength (FX) affects both
    - Enables correlation analysis across all three signals
    - Date range: 1999 onwards where all three sources overlap cleanly
*/

with cpi as (
    select
        period_date,
        period_year,
        period_month,
        cpi_value,
        cpi_mom_change,
        cpi_yoy_pct
    from {{ ref('stg_cpi') }}
    where cpi_category = 'All Items'
        and period_date >= '1999-01-01'
),

usd_sgd as (
    select
        period_date,
        sgd_per_foreign_unit    as usd_sgd_rate,
        foreign_units_per_sgd   as sgd_strength_vs_usd
    from {{ ref('stg_fx') }}
    where currency_pair = 'US Dollar'
),

cny_sgd as (
    select
        period_date,
        sgd_per_foreign_unit    as cny_sgd_rate
    from {{ ref('stg_fx') }}
    where currency_pair = 'Renminbi'
),

total_imports as (
    select
        period_date,
        trade_value_sgd_million as total_imports_sgd
    from {{ ref('stg_trade') }}
    where commodity_category = 'Total Merchandise Imports'
        and trade_type = 'imports'
),

total_exports as (
    select
        period_date,
        sum(trade_value_sgd_million) as total_exports_sgd
    from {{ ref('stg_trade') }}
    where trade_type = 'exports'
    group by period_date
),

-- Spine: CPI drives the date range as it has the longest history
-- Left join everything else so we don't lose CPI rows
joined as (
    select
        cpi.period_date,
        cpi.period_year,
        cpi.period_month,

        -- CPI signals
        cpi.cpi_value,
        cpi.cpi_mom_change,
        cpi.cpi_yoy_pct,

        -- FX signals
        usd.usd_sgd_rate,
        usd.sgd_strength_vs_usd,
        cny.cny_sgd_rate,

        -- Trade signals
        imp.total_imports_sgd,
        exp.total_exports_sgd,

        -- Derived: trade balance (exports minus imports)
        -- Positive = surplus, Negative = deficit
        round(
            exp.total_exports_sgd - imp.total_imports_sgd, 0
        )                                           as trade_balance_sgd,

        -- Derived: trade openness (imports + exports as ratio)
        round(
            (imp.total_imports_sgd + exp.total_exports_sgd)
            / nullif(imp.total_imports_sgd, 0),
        2)                                          as trade_openness_ratio

    from cpi
    left join usd_sgd      usd on cpi.period_date = usd.period_date
    left join cny_sgd      cny on cpi.period_date = cny.period_date
    left join total_imports imp on cpi.period_date = imp.period_date
    left join total_exports exp on cpi.period_date = exp.period_date
),

-- Join to calendar dimension for richer time attributes
final as (
    select
        j.*,
        cal.month_name,
        cal.month_abbr,
        cal.quarter,
        cal.sg_trade_season
    from joined j
    left join {{ ref('dim_calendar') }} cal
        on j.period_date = cal.period_date
)

select * from final
where period_date >= '1999-01-01'
order by period_date desc