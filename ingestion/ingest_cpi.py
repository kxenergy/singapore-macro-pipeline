import requests
import duckdb
import pandas as pd
import logging
import os
from datetime import datetime, timezone

# ── Portable paths ─────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH   = os.path.join(BASE_DIR, "data", "warehouse", "sg_macro.duckdb")
LOG_PATH  = os.path.join(BASE_DIR, "logs", "ingest_cpi.log")
RAW_TABLE = "bronze_cpi_raw"
API_URL   = "https://tablebuilder.singstat.gov.sg/api/table/tabledata/M213751"

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ── Extract ────────────────────────────────────────────────────────────────────
def extract() -> dict:
    log.info("Hitting SingStat CPI API...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://tablebuilder.singstat.gov.sg/"
    }
    response = requests.get(API_URL, headers=headers, timeout=30)
    response.raise_for_status()
    log.info(f"API response received. Status: {response.status_code}")
    return response.json()

# ── Transform to flat DataFrame ────────────────────────────────────────────────
def transform(raw: dict) -> pd.DataFrame:
    log.info("Parsing API response into DataFrame...")
    
    records = []
    data_rows = raw["Data"]["row"]
    
    for row in data_rows:
        category = row["rowText"]
        for obs in row["columns"]:
            records.append({
                "cpi_category": category,
                "time_period":  obs["key"],
                "cpi_value":    float(obs["value"]) if obs["value"] not in ("", "na") else None
            })
    
    df = pd.DataFrame(records)
    # audit trail — when did WE pull this
    df["ingested_at"] = datetime.now(timezone.utc)  
    log.info(f"Parsed {len(df)} rows across {df['cpi_category'].nunique()} categories")
    return df

# ── Load into DuckDB Bronze layer ──────────────────────────────────────────────
def load(df: pd.DataFrame):
    log.info(f"Loading into DuckDB table: {RAW_TABLE}")
    con = duckdb.connect(DB_PATH)
    
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS {RAW_TABLE} (
            cpi_category VARCHAR,
            time_period  VARCHAR,
            cpi_value    DOUBLE,
            ingested_at  TIMESTAMP
        )
    """)
    
    # Idempotent load — delete today's data before inserting
    # This means running twice won't duplicate rows
    today = datetime.now(timezone.utc).date()
    con.execute(f"""
        DELETE FROM {RAW_TABLE}
        WHERE CAST(ingested_at AS DATE) = '{today}'
    """)
    
    con.execute(f"INSERT INTO {RAW_TABLE} SELECT * FROM df")
    row_count = con.execute(f"SELECT COUNT(*) FROM {RAW_TABLE}").fetchone()[0]
    log.info(f"Load complete. Total rows in {RAW_TABLE}: {row_count}")
    con.close()

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("=== CPI Ingestion Started ===")
    try:
        raw  = extract()
        df   = transform(raw)
        load(df)
        log.info("=== CPI Ingestion Completed Successfully ===")
    except Exception as e:
        log.error(f"Ingestion failed: {e}")
        raise