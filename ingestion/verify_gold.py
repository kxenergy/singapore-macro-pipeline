import duckdb

con = duckdb.connect(r'C:\Users\Kevin\singapore_macro_pipeline\data\warehouse\sg_macro.duckdb')

print("=" * 60)
print("GOLD MART VERIFICATION")
print("=" * 60)

print("\n>>> ROW COUNT & DATE RANGE")
print(con.execute("""
    SELECT
        COUNT(*)            as total_rows,
        MIN(period_date)    as earliest,
        MAX(period_date)    as latest,
        COUNT(usd_sgd_rate) as fx_rows,
        COUNT(total_imports_sgd) as trade_rows
    FROM main_marts.mart_sg_macro
""").df())

print("\n>>> LATEST 6 MONTHS — FULL PICTURE")
print(con.execute("""
    SELECT
        period_date,
        cpi_value,
        cpi_yoy_pct         as cpi_yoy_pct,
        usd_sgd_rate,
        total_imports_sgd,
        total_exports_sgd,
        trade_balance_sgd
    FROM main_marts.mart_sg_macro
    WHERE usd_sgd_rate IS NOT NULL
    ORDER BY period_date DESC
    LIMIT 6
""").df())

print("\n>>> TRADE BALANCE SIGN CHECK")
print(con.execute("""
    SELECT
        period_date,
        total_exports_sgd,
        total_imports_sgd,
        trade_balance_sgd,
        CASE WHEN trade_balance_sgd > 0 THEN 'Surplus'
             ELSE 'Deficit' END as balance_status
    FROM main_marts.mart_sg_macro
    WHERE total_exports_sgd IS NOT NULL
    ORDER BY period_date DESC
    LIMIT 6
""").df())

print("\n>>> INFLATION DURING HIGH USD PERIODS")
print(con.execute("""
    SELECT
        period_year,
        ROUND(AVG(cpi_yoy_pct), 2)      as avg_cpi_yoy_pct,
        ROUND(AVG(usd_sgd_rate), 4)     as avg_usd_sgd,
        ROUND(AVG(total_imports_sgd), 0) as avg_monthly_imports
    FROM main_marts.mart_sg_macro
    WHERE usd_sgd_rate IS NOT NULL
        AND total_imports_sgd IS NOT NULL
    GROUP BY period_year
    ORDER BY period_year DESC
    LIMIT 10
""").df())

print("\n>>> TRADE CATEGORIES AVAILABLE")
print(con.execute("""
    SELECT DISTINCT trade_type, commodity_category
    FROM main_staging.stg_trade
    ORDER BY trade_type, commodity_category
""").df())

con.close()
print("\n" + "=" * 60)
print("Gold verification complete.")
print("=" * 60)

print("\n>>> ALL CATEGORIES IN BRONZE TRADE RAW")
print(con.execute("""
    SELECT DISTINCT trade_type, commodity_category
    FROM bronze_trade_raw
    ORDER BY trade_type, commodity_category
""").df())