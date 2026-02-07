
import pandas as pd
import os

# Define paths
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, 'data', 'oc_review.csv')

print(f"Reading from {csv_path}...")
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"Error: File not found at {csv_path}")
    exit(1)

# Check if 'date' column exists
if 'date' not in df.columns:
    print("Error: 'date' column not found in CSV.")
    print("Available columns:", df.columns.tolist())
    exit(1)

print("Processing dates...")
# Convert to datetime, coercing errors
df["date_dt"] = pd.to_datetime(df["date"], errors="coerce")
df["hour"] = df["date_dt"].dt.hour

def to_time_bucket_3(h):
    if pd.isna(h):
        return None
    h = int(h)
    if 5 <= h <= 10:
        return "Morning"
    elif 11 <= h <= 15:
        return "Lunch"
    else:
        return "Dinner"

print("Updating time_bucket column...")
df["time_bucket"] = df["hour"].apply(to_time_bucket_3)

# Drop the temporary helper columns if you don't want them persistent, 
# but the user didn't explicitly ask to remove them. 
# Usually it's cleaner to remove helper columns 'date_dt' and 'hour'. 
# The user asked to "update the oc_review.csv on the time_bucket column".
# I will keep 'time_bucket' and drop 'date_dt' and 'hour' to avoid clutter.
df.drop(columns=['date_dt', 'hour'], inplace=True)

print(f"Saving updated data to {csv_path}...")
df.to_csv(csv_path, index=False)
print("Done!")
