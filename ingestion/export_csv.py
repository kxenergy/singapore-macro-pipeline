import duckdb
import pandas as pd

con = duckdb.connect(r'C:\Users\Kevin\singapore_macro_pipeline\data\warehouse\sg_macro.duckdb')

df = con.execute("""
    SELECT
        period_date,
        period_year,
        cast(period_month as integer) as period_month,
        month_name,
        quarter,
        sg_trade_season,
        -- CPI: stored as 1.80 meaning 1.80% -- keep as-is, display with % suffix
        round(cpi_value, 1)                                     as cpi_index,
        round(cpi_yoy_pct / 100.0, 4)                          as cpi_yoy_pct,
        round(cpi_mom_change / 100.0, 5)                        as cpi_mom_pct,
        -- FX: SGD per foreign unit
        round(usd_sgd_rate, 4)                                  as usd_sgd,
        round(cny_sgd_rate, 4)                                  as cny_sgd,
        round(usd_sgd_rate / nullif(cny_sgd_rate,0), 2)        as usd_cny_ratio,
        -- Trade: raw values are SGD thousands, divide by 1e6 = SGD billions
        round(total_imports_sgd / 1000000.0, 2)                as imports_sgd_bn,
        round(total_exports_sgd / 1000000.0, 2)                as exports_sgd_bn,
        round(trade_balance_sgd / 1000000.0, 2)                as trade_balance_sgd_bn,
        -- Case study: SGD 50M budget in foreign currency
        round(50 / usd_sgd_rate, 1)                            as ge_usd_budget_m,
        round(50 / nullif(cny_sgd_rate,0), 0)                  as mindray_cny_budget_m
    FROM main_marts.fct_sg_macro_monthly
    ORDER BY period_date
""").df()

output_path = r'C:\Users\Kevin\singapore_macro_pipeline\dashboard\sources\sg_macro\macro_monthly.csv'
df.to_csv(output_path, index=False)
print(f"Exported {len(df)} rows")
print(f"Columns: {list(df.columns)}")
print(f"\nSample (last 3 rows):")
print(df.tail(3).to_string())
con.close()