import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap

df = pd.read_csv('processed_violations.csv')

grouped = df.groupby(["day_of_week", "hour"]).size().reset_index(name="count")

# Step 4: Pivot into grid
heatmap_data = grouped.pivot(index="day_of_week", columns="hour", values="count").fillna(0)



plt.figure(figsize=(12,6))
sns.heatmap(heatmap_data, cmap="Reds")
plt.xlabel("Hour of Day")
plt.ylabel("Day of Week")
plt.title("Violations Heatmap")
plt.show()

m = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

# Take lat/lon of violations (sample if dataset is huge)
heat_data = df[['Violation Latitude', 'Violation Longitude']].dropna().values.tolist()

# Add heatmap
HeatMap(heat_data, radius=8).add_to(m)

# Save to html
m.save("violations_heatmap.html")
