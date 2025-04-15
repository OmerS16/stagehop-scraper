import os
import pandas as pd
from sqlalchemy import create_engine
import time

def upload_to_rds(df: pd.DataFrame, table_name: str = 'events'):
    print("Reading environment variables...")
    username = os.environ.get('RDS_USERNAME')
    password = os.environ.get('RDS_PASSWORD')
    host = os.environ.get('RDS_HOST')
    port = os.environ.get('RDS_PORT', 5432)
    db_name = os.environ.get('RDS_DB_NAME')

    if not all([username, password, host, db_name]):
        raise Exception("One or more required RDS environment variables are missing.")

    connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}"
    print(f"Connection string ready: host={host}, db={db_name}")

    try:
        print("Creating SQLAlchemy engine...")
        engine = create_engine(connection_string)

        print("Uploading DataFrame to RDS...")
        t0 = time.time()
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"Uploaded {len(df)} records to table '{table_name}' in database '{db_name}'.")
        print(f"Upload finished in {time.time() - t0:.2f} seconds")

    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        raise
