import os
import duckdb
import pandas as pd

# ── Portable paths — works on any machine ─────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH     = os.path.join(BASE_DIR, "data", "warehouse", "sg_macro.duckdb")
OUTPUT_PATH = os.path.join(BASE_DIR, "dashboard", "sources", "sg_macro", "macro_monthly.csv")

con = duckdb.connect(DB_PATH)

df = con.execute("""
    SELECT
        period_date,
        period_year,
        cast(period_month as integer)                           as period_month,
        month_name,
        quarter,
        sg_trade_season,
        round(cpi_value, 1)                                     as cpi_index,
        round(cpi_yoy_pct / 100.0, 4)                          as cpi_yoy_pct,
        round(cpi_mom_change / 100.0, 5)                        as cpi_mom_pct,
        round(usd_sgd_rate, 4)                                  as usd_sgd,
        round(cny_sgd_rate, 4)                                  as cny_sgd,
        round(usd_sgd_rate / nullif(cny_sgd_rate,0), 2)        as usd_cny_ratio,
        round(total_imports_sgd / 1000000.0, 2)                as imports_sgd_bn,
        round(total_exports_sgd / 1000000.0, 2)                as exports_sgd_bn,
        round(trade_balance_sgd / 1000000.0, 2)                as trade_balance_sgd_bn,
        round(50 / usd_sgd_rate, 1)                            as ge_usd_budget_m,
        round(50 / nullif(cny_sgd_rate,0), 0)                  as mindray_cny_budget_m
    FROM main_marts.fct_sg_macro_monthly
    ORDER BY period_date
""").df()

df.to_csv(OUTPUT_PATH, index=False)
print(f"Exported {len(df)} rows")
print(f"DB path:     {DB_PATH}")
print(f"Output path: {OUTPUT_PATH}")
print(f"\nSample (last 3 rows):")
print(df.tail(3).to_string())
con.close()