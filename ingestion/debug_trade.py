import duckdb

con = duckdb.connect(r'C:\Users\Kevin\singapore_macro_pipeline\data\warehouse\sg_macro.duckdb')

print(">>> DISTINCT TRADE TYPES IN BRONZE")
print(con.execute("SELECT DISTINCT trade_type FROM bronze_trade_raw").df())

print("\n>>> DISTINCT CATEGORIES WHERE TRADE_TYPE = exports")
print(con.execute("""
    SELECT DISTINCT commodity_category 
    FROM bronze_trade_raw 
    WHERE trade_type = 'exports'
    ORDER BY 1
""").df())

print("\n>>> ROW COUNT BY TRADE TYPE")
print(con.execute("""
    SELECT trade_type, COUNT(*) as rows
    FROM bronze_trade_raw
    GROUP BY trade_type
""").df())

print("\n>>> SAMPLE EXPORTS ROWS")
print(con.execute("""
    SELECT trade_type, commodity_category, trade_month, trade_value_sgd_million
    FROM bronze_trade_raw
    WHERE trade_type = 'exports'
    LIMIT 5
""").df())

con.close()