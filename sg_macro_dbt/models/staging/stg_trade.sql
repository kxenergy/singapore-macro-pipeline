{{ config(materialized='view') }}

/*
    Silver layer: Merchandise trade
    - Parses month format from '2024Jan' to a real date
    - Keeps both imports and exports
    - Filters to top-level summary categories to avoid double counting
    - Values are in SGD millions as published by SingStat
*/

with source as (
    select * from {{ source('bronze', 'bronze_trade_raw') }}
),

cleaned as (
    select
        trade_type,
        commodity_category,

        -- Parse '2024Jan' into a real date
        strptime(trade_month, '%Y%b')              as period_date,
        left(trade_month, 4)::integer               as period_year,
        right(trade_month, 3)                       as period_month_abbr,

        trade_value_sgd_million::double             as trade_value_sgd_million,
        ingested_at

    from source
    where trade_value_sgd_million is not null
        and trade_value_sgd_million > 0
),

-- Keep only the total merchandise lines to avoid double counting
-- commodity sub-categories sum into these totals
totals_only as (
    -- Imports: use the published total row
    select * from cleaned
    where trade_type = 'imports'
        and commodity_category = 'Total Merchandise Imports'

    union all

    -- Exports: no summary row exists, keep all commodity rows
    -- The mart will sum these into a total
    select * from cleaned
    where trade_type = 'exports'
)

select * from totals_only
order by trade_type, commodity_category, period_date