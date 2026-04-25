import duckdb

con = duckdb.connect(r'C:\Users\Kevin\singapore_macro_pipeline\data\warehouse\sg_macro.duckdb')

print("=" * 60)
print("SILVER LAYER VERIFICATION")
print("=" * 60)

print("\n>>> STG_CPI — sample with YoY calculation")
print(con.execute("""
    SELECT cpi_category, period_date, cpi_value, cpi_mom_change, cpi_yoy_pct
    FROM main_staging.stg_cpi
    WHERE cpi_category = 'All Items'
    ORDER BY period_date DESC
    LIMIT 6
""").df())

print("\n>>> STG_FX — sample rates")
print(con.execute("""
    SELECT currency_pair, period_date, sgd_per_foreign_unit, foreign_units_per_sgd
    FROM main_staging.stg_fx
    WHERE currency_pair = 'US Dollar'
    ORDER BY period_date DESC
    LIMIT 6
""").df())

print("\n>>> STG_TRADE — recent totals")
print(con.execute("""
    SELECT trade_type, commodity_category, period_date, trade_value_sgd_million
    FROM main_staging.stg_trade
    WHERE commodity_category IN ('Total Merchandise Imports','Total Merchandise Exports')
    ORDER BY period_date DESC
    LIMIT 8
""").df())

con.close()
print("\n" + "=" * 60)
print("Silver verification complete.")
print("=" * 60)