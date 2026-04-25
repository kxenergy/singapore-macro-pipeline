{{ config(materialized='view') }}

/*
    Silver layer: CPI
    - Cleans column names
    - Parses time_period string into a proper date
    - Casts types explicitly
    - Adds month-over-month and year-over-year change via window functions
*/

with source as (
    select * from {{ source('bronze', 'bronze_cpi_raw') }}
),

cleaned as (
    select
        cpi_category,
        strptime(time_period, '%Y %b')                  as period_date,
        left(time_period, 4)::integer                   as period_year,
        strftime(
            strptime(time_period, '%Y %b'), '%m'
        )::integer                                      as period_month,
        cpi_value::double                               as cpi_value,
        ingested_at
    from source
    where cpi_value is not null
),

with_mom as (
    select
        *,
        round(
            cpi_value - lag(cpi_value) over (
                partition by cpi_category
                order by period_date
            ),
        3)                                              as cpi_mom_change,

        round(
            (cpi_value - lag(cpi_value, 12) over (
                partition by cpi_category
                order by period_date
            )) / nullif(
                lag(cpi_value, 12) over (
                    partition by cpi_category
                    order by period_date
                ), 0
            ) * 100,
        2)                                              as cpi_yoy_pct
    from cleaned
)

select * from with_mom
order by cpi_category, period_date