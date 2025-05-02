import os
import time
import pandas as pd
from sqlalchemy import Table, MetaData, create_engine
from sqlalchemy.dialects.postgresql import insert

def upload_to_rds(df: pd.DataFrame, table_name: str = 'events', conflict_cols=None):
    # ─── 1) Read your RDS creds ────────────────────────────────────────
    username = os.environ.get('RDS_USERNAME')
    password = os.environ.get('RDS_PASSWORD')
    host     = os.environ.get('RDS_HOST')
    port     = os.environ.get('RDS_PORT', 5432)
    db_name  = os.environ.get('RDS_DB_NAME')

    if not all([username, password, host, db_name]):
        raise Exception("One or more required RDS environment variables are missing.")

    connection_string = (
        f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}"
    )
    print(f"Connecting to {host}/{db_name}…")

    # ─── 2) Prep the engine + reflect your existing table ─────────────
    engine = create_engine(connection_string)
    meta = MetaData(bind=engine)
    tbl = Table(table_name, meta, autoload_with=engine)

    # ─── 3) Build the INSERT … ON CONFLICT statement ────────────────
    conflict_cols = conflict_cols or ['id']
    records = df.to_dict(orient='records')
    if not records:
        print("No records to upload.")
        return

    stmt = insert(tbl).values(records)
    stmt = stmt.on_conflict_do_nothing(index_elements=conflict_cols)

    # ─── 4) Fire it off in one transaction ──────────────────────────
    print(f"Uploading {len(records)} rows (skipping duplicates on {conflict_cols})…")
    t0 = time.time()
    with engine.begin() as conn:
        result = conn.execute(stmt)
    duration = time.time() - t0

    print(f"Inserted {result.rowcount} new rows; {len(records) - result.rowcount} skipped.")
    print(f"Done in {duration:.2f}s.")
