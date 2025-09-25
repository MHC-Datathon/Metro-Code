import pandas as pd
import folium
from folium.plugins import HeatMap


chunk_size = 10000
chunks = []
total_rows = 0

for chunk in pd.read_csv("MTA_Bus_Automated_Camera_Enforcement_Violations.csv", chunksize=chunk_size):
    chunk["First Occurrence"] = pd.to_datetime(chunk["First Occurrence"], 
                                             format="%m/%d/%Y %I:%M:%S %p", 
                                             errors="coerce")
    chunk = chunk.dropna(subset=["Violation Latitude", "Violation Longitude", "First Occurrence"])
    
    if len(chunk) > 0:
        chunks.append(chunk)
        total_rows += len(chunk)
        print(f"Processed {total_rows} valid rows...")
    
    

df = pd.concat(chunks, ignore_index=True)
df_small = df.tail(1000000).copy()
print(f"Using {len(df_small)} rows for full week analysis")


df_small["day_of_week"] = df_small["First Occurrence"].dt.dayofweek  # 0=Monday, 6=Sunday
df_small["hour"] = df_small["First Occurrence"].dt.hour


day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
time_periods = [
    ("Early Morning (4-8h)", 4, 8),
    ("Morning (8-12h)", 8, 12), 
    ("Afternoon (12-16h)", 12, 16),
    ("Evening (16-20h)", 16, 20),
    ("Night (20-24h)", 20, 24)
]

all_periods = []
heat_layers_data = []

print("Processing all day/time combinations...")

for day_idx in range(7):  # Monday to Sunday
    for time_name, start_hour, end_hour in time_periods:
        # Filter data for this specific day and time
        mask = (df_small["day_of_week"] == day_idx) & \
               (df_small["hour"] >= start_hour) & \
               (df_small["hour"] < end_hour)
        
        period_data = df_small[mask]
        
        if len(period_data) > 5:
            heat_data = [[row["Violation Latitude"], row["Violation Longitude"], 1] 
                        for _, row in period_data.iterrows()]
            
            period_label = f"{day_names[day_idx]} {time_name} ({len(period_data)} violations)"
            all_periods.append(period_label)
            heat_layers_data.append(heat_data)
            
            print(f" {day_names[day_idx]} {time_name}: {len(period_data)} violations")
        else:
            period_label = f"{day_names[day_idx]} {time_name} ({len(period_data)} violations)"
            all_periods.append(period_label)
            heat_layers_data.append([[40.7128, -74.0060, 0.1]])
            
            print(f"  {day_names[day_idx]} {time_name}: {len(period_data)} violations (low data)")

print(f"Total periods created: {len(all_periods)}")


m = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

# Add all heatmaps to the map
for i, heat_data in enumerate(heat_layers_data):
    HeatMap(
        heat_data, 
        radius=25, 
        blur=15,
        gradient={0.2: 'blue', 0.4: 'cyan', 0.6: 'lime', 0.8: 'orange', 1: 'red'},
        min_opacity=0.3
    ).add_to(folium.FeatureGroup(name=f'period_{i}').add_to(m))

#make slider thing
max_index = len(all_periods) - 1

html = f"""
<div style="position: fixed; bottom: 15px; right: 15px; z-index: 1000; 
            background: rgba(255,255,255,0.95); padding: 12px 16px; border-radius: 8px; 
            box-shadow: 0 3px 12px rgba(0,0,0,0.3); font-family: Arial, sans-serif; 
            font-size: 12px; min-width: 280px;">
    
    <div style="margin-bottom: 6px; font-weight: bold; color: #333; font-size: 11px;">
        📅 Time Period Control
    </div>
    
    <input type="range" id="weekSlider" min="0" max="{max_index}" value="0" 
           style="width: 240px; height: 6px; margin: 4px 0; cursor: pointer;">
    
    <div id="weekLabel" style="font-size: 10px; color: #555; margin-top: 4px; 
                               line-height: 1.2;">
        {all_periods[0]}
    </div>
</div>

<script>
var weekPeriods = {all_periods};

function showWeekPeriod(index) {{
    document.querySelectorAll('.leaflet-heatmap-layer').forEach(function(layer) {{
        layer.style.display = 'none';
    }});
    
    var layers = document.querySelectorAll('.leaflet-heatmap-layer');
    if (layers[index]) {{
        layers[index].style.display = 'block';
    }}
    
    document.getElementById('weekLabel').textContent = weekPeriods[index];
}}

document.addEventListener('DOMContentLoaded', function() {{
    var slider = document.getElementById('weekSlider');
    
    slider.addEventListener('input', function() {{
        showWeekPeriod(parseInt(this.value));
    }});
    
    setTimeout(function() {{
        showWeekPeriod(0);
    }}, 1000);
}});
</script>
"""

m.get_root().html.add_child(folium.Element(html))


m.save("violations_heatmap_week_hour_slider.html")
print("\n" + "="*60)
print("="*60)
print(f" Total violations processed: {len(df_small):,}")
print(f" Time periods available: {len(all_periods)}")
print(f"File saved: violations_heatmap_week_hour_slider.html")
