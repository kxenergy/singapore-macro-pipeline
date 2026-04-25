import duckdb

con = duckdb.connect(r'C:\Users\Kevin\singapore_macro_pipeline\data\warehouse\sg_macro.duckdb')

print("=" * 60)
print("BRONZE LAYER VERIFICATION")
print("=" * 60)

# ── Table inventory ────────────────────────────────────────────
print("\n>>> ALL TABLES IN WAREHOUSE")
print(con.execute("SHOW TABLES").df())

# ── CPI ───────────────────────────────────────────────────────
print("\n>>> BRONZE_CPI_RAW")
print(f"Row count : {con.execute('SELECT COUNT(*) FROM bronze_cpi_raw').fetchone()[0]:,}")
print(f"Categories: {con.execute('SELECT COUNT(DISTINCT cpi_category) FROM bronze_cpi_raw').fetchone()[0]}")
print(f"Date range: {con.execute('SELECT MIN(time_period), MAX(time_period) FROM bronze_cpi_raw').fetchone()}")
print(f"Nulls     : {con.execute('SELECT COUNT(*) FROM bronze_cpi_raw WHERE cpi_value IS NULL').fetchone()[0]}")
print("\nSample:")
print(con.execute("SELECT * FROM bronze_cpi_raw LIMIT 3").df())

# ── FX ────────────────────────────────────────────────────────
print("\n>>> BRONZE_FX_RAW")
print(f"Row count  : {con.execute('SELECT COUNT(*) FROM bronze_fx_raw').fetchone()[0]:,}")
print(f"Currencies : {con.execute('SELECT COUNT(DISTINCT currency_pair) FROM bronze_fx_raw').fetchone()[0]}")
print(f"Date range : {con.execute('SELECT MIN(rate_month), MAX(rate_month) FROM bronze_fx_raw').fetchone()}")
print(f"Nulls      : {con.execute('SELECT COUNT(*) FROM bronze_fx_raw WHERE exchange_rate IS NULL').fetchone()[0]}")
print("\nCurrencies available:")
print(con.execute("SELECT DISTINCT currency_pair FROM bronze_fx_raw ORDER BY 1").df())
print("\nSample:")
print(con.execute("SELECT * FROM bronze_fx_raw LIMIT 3").df())

# ── Trade ─────────────────────────────────────────────────────
print("\n>>> BRONZE_TRADE_RAW")
print(f"Row count  : {con.execute('SELECT COUNT(*) FROM bronze_trade_raw').fetchone()[0]:,}")
print(f"Categories : {con.execute('SELECT COUNT(DISTINCT commodity_category) FROM bronze_trade_raw').fetchone()[0]}")
print(f"Trade types: {con.execute('SELECT DISTINCT trade_type FROM bronze_trade_raw').fetchone()}")
print(f"Date range : {con.execute('SELECT MIN(trade_month), MAX(trade_month) FROM bronze_trade_raw').fetchone()}")
print(f"Nulls      : {con.execute('SELECT COUNT(*) FROM bronze_trade_raw WHERE trade_value_sgd_million IS NULL').fetchone()[0]}")
print("\nTop 5 import categories by total value:")
print(con.execute("""
    SELECT commodity_category, ROUND(SUM(trade_value_sgd_million), 0) as total_sgd_million
    FROM bronze_trade_raw
    WHERE trade_type = 'imports'
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 5
""").df())
print("\nTop 5 export categories by total value:")
print(con.execute("""
    SELECT commodity_category, ROUND(SUM(trade_value_sgd_million), 0) as total_sgd_million
    FROM bronze_trade_raw
    WHERE trade_type = 'exports'
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 5
""").df())

con.close()
print("\n" + "=" * 60)
print("Verification complete.")
print("=" * 60)