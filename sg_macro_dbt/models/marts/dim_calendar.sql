{{ config(materialized='table') }}

/*
    Dimension: Calendar
    A date spine covering our full data range.
    Enables time-based filtering in any BI tool without SQL knowledge.
    Standard pattern in every production data warehouse.
*/

with date_spine as (
    select
        period_date,
        extract('year'  from period_date)::integer   as year,
        extract('month' from period_date)::integer   as month_num,
        strftime(period_date, '%b')                  as month_abbr,
        strftime(period_date, '%B')                  as month_name,
        case extract('month' from period_date)::integer
            when 1  then 'Q1' when 2  then 'Q1' when 3  then 'Q1'
            when 4  then 'Q2' when 5  then 'Q2' when 6  then 'Q2'
            when 7  then 'Q3' when 8  then 'Q3' when 9  then 'Q3'
            when 10 then 'Q4' when 11 then 'Q4' when 12 then 'Q4'
        end                                          as quarter,
        case
            when extract('month' from period_date)::integer
                 between 3 and 5  then 'Asia Dry Season'
            when extract('month' from period_date)::integer
                 between 6 and 9  then 'Monsoon Season'
            else 'Year End / Q1'
        end                                          as sg_trade_season

    from (
        select unnest(
            generate_series(
                date '1999-01-01',
                current_date,
                interval '1 month'
            )
        )::date as period_date
    )
)

select * from date_spine
order by period_date