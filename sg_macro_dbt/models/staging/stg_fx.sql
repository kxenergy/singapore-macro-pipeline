{{ config(materialized='view') }}

/*
    Silver layer: FX rates
    - Standardises month format from '2024Jan' to a real date
    - Filters to key currencies that matter for Singapore macro story
    - Adds inverse rate (how many foreign units per SGD)
*/

with source as (
    select * from {{ source('bronze', 'bronze_fx_raw') }}
),

cleaned as (
    select
        currency_pair,

        -- Parse '2024Jan' into a real date
        strptime(rate_month, '%Y%b')                as period_date,
        left(rate_month, 4)::integer                as period_year,
        right(rate_month, 3)                        as period_month_abbr,

        exchange_rate::double                       as sgd_per_foreign_unit,

        -- Inverse: how many foreign units does 1 SGD buy?
        round(1.0 / nullif(exchange_rate::double, 0), 4)
                                                    as foreign_units_per_sgd,
        ingested_at

    from source
    where exchange_rate is not null
        and exchange_rate > 0
),

-- Focus on currencies most relevant to Singapore trade story
key_currencies as (
    select * from cleaned
    where currency_pair in (
        'US Dollar',
        'Renminbi',
        'Euro',
        'Malaysian Ringgit',
        'Japanese Yen',
        'Sterling Pound',
        'Australian Dollar'
    )
)

select * from key_currencies
order by currency_pair, period_date