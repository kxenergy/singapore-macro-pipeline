import time
import requests
import duckdb
import pandas as pd
import logging
from datetime import datetime, timezone

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler("../logs/ingest_mas_fx.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
# data.gov.sg API - open, no auth, free forever
# Dataset: Exchange Rates (Average For Period), Monthly - published by MAS/SingStat
DATASET_ID = "d_3c62d5eed03c40aeafbb6d0fa324e976"
BASE_URL   = f"https://data.gov.sg/api/action/datastore_search?resource_id={DATASET_ID}"
DB_PATH    = r"C:\Users\Kevin\singapore_macro_pipeline\data\warehouse\sg_macro.duckdb"
RAW_TABLE  = "bronze_fx_raw"



# ── Extract — paginate with exponential backoff ────────────────────────────────
def extract() -> list:
    log.info("Hitting data.gov.sg MAS FX API...")
    all_records = []
    limit  = 100   # reduced from 1000 to stay under rate limits
    offset = 0

    while True:
        url     = f"{BASE_URL}&limit={limit}&offset={offset}"
        retries = 0
        max_retries = 5

        while retries < max_retries:
            response = requests.get(url, timeout=30)

            if response.status_code == 429:
                wait = 2 ** retries  # 1s, 2s, 4s, 8s, 16s
                log.warning(f"Rate limited. Waiting {wait}s before retry {retries + 1}/{max_retries}...")
                time.sleep(wait)
                retries += 1
                continue

            response.raise_for_status()
            break  # success — exit retry loop

        data    = response.json()
        records = data["result"]["records"]

        if not records:
            break

        all_records.extend(records)
        log.info(f"  Fetched {len(all_records)} records so far...")

        if len(records) < limit:
            break

        offset += limit
        time.sleep(1)  # polite delay between pages — professional habit

    log.info(f"Total records fetched: {len(all_records)}")
    return all_records

# ── Transform ──────────────────────────────────────────────────────────────────
def transform(records: list) -> pd.DataFrame:
    log.info("Transforming FX records...")
    df = pd.DataFrame(records)

    # Drop internal datastore ID
    df = df.drop(columns=["_id"], errors="ignore")

    # The API returns data PIVOTED — currency names as rows, months as columns
    # We need to UNPIVOT so each row = one currency, one month, one rate
    # This is the core reshape pattern for wide -> long format

    id_cols    = ["DataSeries"]           # the column that holds currency names
    month_cols = [c for c in df.columns if c not in id_cols + ["ingested_at"]]

    df_long = df.melt(
        id_vars    = id_cols,
        value_vars = month_cols,
        var_name   = "rate_month",        # column name for the month
        value_name = "exchange_rate"      # column name for the rate value
    )

    # Rename for clarity
    df_long = df_long.rename(columns={"DataSeries": "currency_pair"})

    # Cast rate to numeric — some cells may be empty strings
    df_long["exchange_rate"] = pd.to_numeric(df_long["exchange_rate"], errors="coerce")

    # Drop rows with no rate value
    df_long = df_long.dropna(subset=["exchange_rate"])

    # Add audit timestamp cleanly using assign (fixes fragmentation warning)
    df_long = df_long.assign(ingested_at=datetime.now(timezone.utc))

    # Sort chronologically
    df_long = df_long.sort_values(["currency_pair", "rate_month"])

    log.info(f"Currency pairs available: {df_long['currency_pair'].unique().tolist()}")
    log.info(f"Parsed {len(df_long)} rows after unpivot")
    return df_long

# ── Load ───────────────────────────────────────────────────────────────────────
def load(df: pd.DataFrame):
    log.info(f"Loading into DuckDB table: {RAW_TABLE}")
    con = duckdb.connect(DB_PATH)

    # Drop and recreate — schema may vary by dataset version
    con.execute(f"DROP TABLE IF EXISTS {RAW_TABLE}")
    con.execute(f"""
        CREATE TABLE {RAW_TABLE} AS
        SELECT * FROM df
    """)

    row_count = con.execute(f"SELECT COUNT(*) FROM {RAW_TABLE}").fetchone()[0]
    log.info(f"Load complete. Total rows in {RAW_TABLE}: {row_count}")
    con.close()

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("=== MAS FX Ingestion Started ===")
    try:
        records = extract()
        df      = transform(records)
        load(df)
        log.info("=== MAS FX Ingestion Completed Successfully ===")
    except Exception as e:
        log.error(f"Ingestion failed: {e}")
        raise