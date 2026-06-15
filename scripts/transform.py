import pandas as pd
import glob

# Only load the columns we actually need — taxi parquet files have ~19 columns,
# we only use a handful
COLUMNS_NEEDED = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "fare_amount",
    "total_amount",
]

# Memory-efficient dtypes for the columns we keep
DTYPES = {
    "passenger_count": "float32",
    "trip_distance": "float32",
    "fare_amount": "float32",
    "total_amount": "float32",
}

def process_file(filepath):
    """Read, clean, and aggregate a single month's file. Returns a daily summary."""
    df = pd.read_parquet(filepath, columns=COLUMNS_NEEDED)

    # Cast to smaller dtypes to cut memory usage roughly in half
    for col, dtype in DTYPES.items():
        df[col] = df[col].astype(dtype)

    # --- Cleaning ---
    df.drop_duplicates(inplace=True)
    df = df.dropna(subset=["fare_amount", "tpep_pickup_datetime"])
    df = df[(df["fare_amount"] > 0) & (df["trip_distance"] > 0)]

    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
    df["trip_date"] = df["tpep_pickup_datetime"].dt.date

    df["trip_duration_min"] = (
        (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60
    )

    # Aggregate this file's data into daily summary immediately,
    # then drop the detailed dataframe from memory
    daily = df.groupby("trip_date").agg(
        total_trips=("fare_amount", "count"),
        total_revenue=("total_amount", "sum"),
        avg_fare=("fare_amount", "mean"),
        avg_trip_distance=("trip_distance", "mean"),
        avg_trip_duration_min=("trip_duration_min", "mean"),
    ).reset_index()

    row_count = len(df)
    del df  # free memory before moving to next file

    return daily, row_count

def transform():
    files = sorted(glob.glob("data/*.parquet"))
    all_daily_summaries = []
    total_rows = 0

    for f in files:
        print(f"Processing {f}...")
        daily, rows = process_file(f)
        all_daily_summaries.append(daily)
        total_rows += rows
        print(f"  -> {rows} rows after cleaning, {len(daily)} days summarized")

    combined_daily = pd.concat(all_daily_summaries, ignore_index=True)

    combined_daily = combined_daily.groupby("trip_date", as_index=False).agg(
        total_trips=("total_trips", "sum"),
        total_revenue=("total_revenue", "sum"),
        avg_fare=("avg_fare", "mean"),
        avg_trip_distance=("avg_trip_distance", "mean"),
        avg_trip_duration_min=("avg_trip_duration_min", "mean"),
    )

    combined_daily.to_csv("data/daily_summary.csv", index=False)

    print(f"Total rows processed across all files: {total_rows}")
    print(f"Daily summary rows: {len(combined_daily)}")
    print("Transform complete.")

if __name__ == "__main__":
    transform()