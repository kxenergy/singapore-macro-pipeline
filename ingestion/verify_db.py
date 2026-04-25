import duckdb

con = duckdb.connect(r'C:\Users\Kevin\singapore_macro_pipeline\data\warehouse\sg_macro.duckdb')

print('=== Row Count ===')
print(con.execute('SELECT COUNT(*) FROM bronze_cpi_raw').fetchone()[0])

print('\n=== Sample Data (5 rows) ===')
print(con.execute('SELECT * FROM bronze_cpi_raw LIMIT 5').df())

print('\n=== All 23 Categories ===')
print(con.execute('SELECT DISTINCT cpi_category FROM bronze_cpi_raw ORDER BY 1').df())

print('\n=== Date Range ===')
print(con.execute('SELECT MIN(time_period), MAX(time_period) FROM bronze_cpi_raw').df())

con.close()
print('\nVerification complete.')