import os
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

def load_to_bq(data_path, table_name, file_type="csv"):
    client = bigquery.Client()
    project = os.getenv("GCP_PROJECT_ID")
    dataset = os.getenv("BQ_DATASET")
    table_id = f"{project}.{dataset}.{table_name}"

    if file_type == "parquet":
        df = pd.read_parquet(data_path)
    else:
        df = pd.read_csv(data_path)

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        autodetect=True,
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"Loaded {len(df)} rows into {table_id}")

if __name__ == "__main__":
    load_to_bq("data/daily_summary.csv", "daily_summary", file_type="csv")