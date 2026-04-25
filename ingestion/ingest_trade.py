import requests
import duckdb
import pandas as pd
import logging
import time
from datetime import datetime, timezone

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler("../logs/ingest_trade.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
# Both datasets from data.gov.sg — same API pattern, two dataset IDs
DATASETS = {
    "imports": "d_b89e35ce38cb93a17f5c016e71f50690",  # Merchandise Imports By Commodity Division, Monthly
    "exports": "d_2cd9992cebbe66bfa0b756645ba249b3",  # Domestic Exports By Commodity Group, Monthly
}
BASE_URL  = "https://data.gov.sg/api/action/datastore_search"
DB_PATH   = r"C:\Users\Kevin\singapore_macro_pipeline\data\warehouse\sg_macro.duckdb"
RAW_TABLE = "bronze_trade_raw"

# ── Extract — reusable paginated fetch with backoff ────────────────────────────
def fetch_dataset(dataset_id: str, trade_type: str) -> list:
    log.info(f"Fetching {trade_type} data (dataset: {dataset_id})...")
    all_records = []
    limit  = 100
    offset = 0

    while True:
        url     = f"{BASE_URL}?resource_id={dataset_id}&limit={limit}&offset={offset}"
        retries = 0
        response = None

        while retries < 6:
            r = requests.get(url, timeout=30)
            if r.status_code == 429:
                wait = 2 ** retries
                log.warning(f"  Rate limited. Waiting {wait}s...")
                time.sleep(wait)
                retries += 1
            else:
                r.raise_for_status()
                response = r
                break

        if response is None:
            raise Exception(f"Max retries exceeded for {trade_type} at offset {offset}")

        data = response.json()

        if "result" not in data:
            log.error(f"Unexpected response: {data}")
            raise Exception(f"No 'result' key in response for {trade_type}")

        records = data["result"]["records"]
        if not records:
            break

        for r in records:
            r["trade_type"] = trade_type

        all_records.extend(records)
        log.info(f"  {trade_type}: {len(all_records)} records fetched...")

        if len(records) < limit:
            break

        offset += limit
        time.sleep(2)  # polite delay between pages

    log.info(f"  {trade_type} total: {len(all_records)} records")
    return all_records


def extract() -> list:
    all_records = []
    for trade_type, dataset_id in DATASETS.items():
        records = fetch_dataset(dataset_id, trade_type)
        all_records.extend(records)
        log.info(f"Pausing 30s between datasets to reset rate limit window...")
        time.sleep(30)  # longer pause between datasets
    return all_records

# ── Transform ──────────────────────────────────────────────────────────────────
def transform(records: list) -> pd.DataFrame:
    log.info("Transforming trade records...")
    df = pd.DataFrame(records)
    df = df.drop(columns=["_id"], errors="ignore")

    # Normalise category column name — imports uses 'DataSeries', exports uses 'Data Series Text'
    if "Data Series Text" in df.columns:
        df = df.rename(columns={"Data Series Text": "DataSeries"})

    id_cols    = ["DataSeries", "trade_type"]
    month_cols = [c for c in df.columns if c not in id_cols]

    df_long = df.melt(
        id_vars    = id_cols,
        value_vars = month_cols,
        var_name   = "trade_month",
        value_name = "trade_value_sgd_million"
    )

    df_long = df_long.rename(columns={"DataSeries": "commodity_category"})
    df_long["trade_value_sgd_million"] = pd.to_numeric(
        df_long["trade_value_sgd_million"], errors="coerce"
    )
    df_long = df_long.dropna(subset=["trade_value_sgd_million"])
    df_long = df_long.assign(ingested_at=datetime.now(timezone.utc))
    df_long = df_long.sort_values(["trade_type", "commodity_category", "trade_month"])

    log.info(f"Trade types: {df_long['trade_type'].unique().tolist()}")
    log.info(f"Categories: {df_long['commodity_category'].nunique()} unique")
    log.info(f"Date range: {df_long['trade_month'].min()} to {df_long['trade_month'].max()}")
    log.info(f"Parsed {len(df_long)} rows after unpivot")
    return df_long

# ── Load ───────────────────────────────────────────────────────────────────────
def load(df: pd.DataFrame):
    log.info(f"Loading into DuckDB table: {RAW_TABLE}")
    con = duckdb.connect(DB_PATH)
    con.execute(f"DROP TABLE IF EXISTS {RAW_TABLE}")
    con.execute(f"CREATE TABLE {RAW_TABLE} AS SELECT * FROM df")
    row_count = con.execute(f"SELECT COUNT(*) FROM {RAW_TABLE}").fetchone()[0]
    log.info(f"Load complete. Total rows in {RAW_TABLE}: {row_count}")
    con.close()

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("=== Trade Ingestion Started ===")
    try:
        records = extract()
        df      = transform(records)
        load(df)
        log.info("=== Trade Ingestion Completed Successfully ===")
    except Exception as e:
        log.error(f"Ingestion failed: {e}")
        raise