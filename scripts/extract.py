import os
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

def list_new_files(prefix="raw/"):
    client = storage.Client()
    bucket = client.bucket(os.getenv("GCS_BUCKET_NAME"))
    blobs = bucket.list_blobs(prefix=prefix)
    return [blob.name for blob in blobs if blob.name.endswith(".parquet")]

def download_file(blob_name, local_path):
    client = storage.Client()
    bucket = client.bucket(os.getenv("GCS_BUCKET_NAME"))
    blob = bucket.blob(blob_name)
    blob.download_to_filename(local_path)
    print(f"Downloaded {blob_name} to {local_path}")

if __name__ == "__main__":
    files = list_new_files()
    print("Found files:", files)
    for f in files:
        local_name = f.split("/")[-1]
        download_file(f, f"data/{local_name}")