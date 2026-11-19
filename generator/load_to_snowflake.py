import os
from pathlib import Path

import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv

load_dotenv()

conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    role="DBT_ROLE",
    warehouse="DBT_WH",
    database="FOODDELIVERY",
    schema="RAW",
)
print(conn)

for path in sorted(Path("data").glob("*.parquet")):
    table = path.stem.upper()
    print(table)
    df = pd.read_parquet(path)
    df.columns = [c.upper() for c in df.columns]   # avoid quoted lowercase columns in Snowflake
    df["_LOADED_AT"] = pd.Timestamp.now()           # used later for source freshness checks
    print(f"Loading {table} ({len(df):,} rows)...")
    ok, _, nrows, _ = write_pandas(
        conn, df, table_name=table, auto_create_table=True,
        overwrite=True, use_logical_type=True,
    )
    print(f"  success={ok}, rows={nrows:,}")

conn.close()
print("All tables loaded.")