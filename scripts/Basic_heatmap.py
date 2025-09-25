import pandas as pd

# Load data
df = pd.read_csv("MTA_Bus_Automated_Camera_Enforcement_Violations.csv")

# Step 1: Convert to datetime
df["First Occurrence"] = pd.to_datetime(df["First Occurrence"])

# Step 2: Extract buckets
df["hour"] = df["First Occurrence"].dt.hour
df["day_of_week"] = df["First Occurrence"].dt.dayofweek  # 0=Mon, 6=Sun

df.to_csv("processed_violations.csv", index=False)
# Step 3: Group
grouped = df.groupby(["day_of_week", "hour"]).size().reset_index(name="count")

# Step 4: Pivot into grid
heatmap_data = grouped.pivot(index="day_of_week", columns="hour", values="count").fillna(0)

print(heatmap_data.head())
