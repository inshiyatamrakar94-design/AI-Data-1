import sqlite3
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set seaborn style for clean visualizations
sns.set_theme(style="whitegrid")

# ==========================================
# STEP 1: Fetch Data from Open-Meteo Forecast API & Store in SQLite
# ==========================================

# Define 5 distinct cities with coordinates
cities = {
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "Sydney": {"lat": -33.8688, "lon": 151.2093},
    "Cairo": {"lat": 30.0444, "lon": 31.2357}
}

all_data = []

print("⚡ Connecting live to Open-Meteo to fetch data for the past 7 days...")

# FIXED: Standard clean endpoint path without trailing parameter collisions
base_url = "https://api.open-meteo.com/v1/forecast"

for city, coords in cities.items():
    # FIXED: Grouped all variables here. 'past_days' automatically pulls the last 7 days.
    query_params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "daily": "temperature_2m_max,temperature_2m_min,rain_sum",
        "timezone": "auto",
        "past_days": 7,
        "forecast_days": 0  # Ensures we ONLY get historical data, not forward predictions
    }
    
    response = requests.get(base_url, params=query_params)
    response.raise_for_status() 
    response_json = response.json()
    
    daily = response_json.get("daily", {})
    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    rain = daily.get("rain_sum", []) 
    
    for i in range(len(dates)):
        all_data.append({
            "city": city,
            "date": dates[i],
            "max_temp": max_temps[i],
            "min_temp": min_temps[i],
            "rain": rain[i]
        })

# Create dataframe and initialize SQLite DB
df_raw = pd.DataFrame(all_data)
conn = sqlite3.connect("weather.db")
df_raw.to_sql("weather_data", conn, if_exists="replace", index=False)
conn.close()
print("Data pipeline complete: Table successfully written live to weather.db\n")


# ==========================================
# STEP 2: Load into Pandas & Run Full EDA Checklist
# ==========================================

conn = sqlite3.connect("weather.db")
df = pd.read_sql_query("SELECT * FROM weather_data", conn)
conn.close()

print("--- EDA CHECKLIST ---")
print(f"1. Dataset Shape: {df.shape} (Rows, Columns)")
print("\n2. Null Value Count:")
print(df.isnull().sum())
print("\n3. Dataset Statistical Summary (.describe()):")
print(df.describe(include='all'))
print("\n4. Value Counts per City:")
print(df['city'].value_counts())
print("-" * 30 + "\n")


# ==========================================
# STEP 3: Histogram of Max Temperatures (With Value Labels)
# ==========================================

plt.figure(figsize=(9, 5))
ax1 = sns.histplot(data=df, x="max_temp", kde=True, bins=10, color="teal")

for patch in ax1.patches:
    height = patch.get_height()
    if height > 0:  
        ax1.annotate(f'{int(height)}', 
                     (patch.get_x() + patch.get_width() / 2, height), 
                     ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 3),
                     textcoords='offset points')

plt.title("Distribution of Max Temperatures Across All Cities Combined")
plt.xlabel("Max Temperature (°C)")
plt.ylabel("Frequency (Count of Days)")
plt.savefig("chart1_histogram.png", bbox_inches='tight')
plt.close()


# ==========================================
# STEP 4: Side-by-Side Box Plots (With Median Annotations)
# ==========================================

plt.figure(figsize=(10, 6))
# Added hue="city" and legend=False to satisfy modern Seaborn rules
ax2 = sns.boxplot(data=df, x="city", y="max_temp", hue="city", legend=False, palette="Set2")

for tick, label in enumerate(ax2.get_xticklabels()):
    city_name = label.get_text()
    median_val = df[df['city'] == city_name]['max_temp'].median()
    ax2.text(tick, median_val, f'{median_val:.1f}°C', 
             ha='center', va='bottom', fontweight='bold', color='black', fontsize=10)

plt.title("Comparison of Max Temperatures by City")
plt.xlabel("City")
plt.ylabel("Max Temperature (°C)")
plt.savefig("chart2_boxplot.png", bbox_inches='tight')
plt.close()



# ==========================================
# STEP 5: Identify Outliers Using the IQR Method
# ==========================================

print("--- OUTLIER IDENTIFICATION ---")
outliers_list = []

for city_name in df['city'].unique():
    city_df = df[df['city'] == city_name]
    q1 = city_df['max_temp'].quantile(0.25)
    q3 = city_df['max_temp'].quantile(0.75)
    iqr = q3 - q1
    
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    city_outliers = city_df[(city_df['max_temp'] < lower_bound) | (city_df['max_temp'] > upper_bound)]
    if not city_outliers.empty:
        outliers_list.append(city_outliers)

if outliers_list:
    outliers_df = pd.concat(outliers_list)
    print("Identified Outlier Days:")
    print(outliers_df[['city', 'date', 'max_temp']])
else:
    print("No statistical outliers detected in max temperatures across any city during this 7-day window.")
print("-" * 30 + "\n")


# ==========================================
# STEP 6: KDE Curve per City (With Peak Labels)
# ==========================================

plt.figure(figsize=(10, 6))
ax3 = sns.kdeplot(data=df, x="max_temp", hue="city", fill=True, common_norm=False, alpha=0.4)

for line in ax3.get_lines():
    x, y = line.get_data()
    if len(y) > 0:
        peak_idx = np.argmax(y)
        peak_x = x[peak_idx]
        peak_y = y[peak_idx]
        label = line.get_label()
        ax3.text(peak_x, peak_y + 0.005, f"{label}", ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.title("Kernel Density Estimate (KDE) of Max Temperature by City")
plt.xlabel("Max Temperature (°C)")
plt.ylabel("Density")
plt.savefig("chart3_kde.png", bbox_inches='tight')
plt.close()


# ==========================================
# STEP 7: Grouped Summary Table
# ==========================================

summary_table = df.groupby("city")["max_temp"].agg(["mean", "median", "std", "min", "max"])
print("--- GROUPED SUMMARY TABLE (MAX TEMPERATURE) ---")
print(summary_table.round(2))
print("-" * 30 + "\n")


# ==========================================
# BONUS: Bar Plot (With Precise Rain Total Labels)
# ==========================================

plt.figure(figsize=(10, 6))
# Added hue="city" and legend=False to clear the palette warning
ax4 = sns.barplot(data=df, x="city", y="rain", estimator=np.sum, errorbar=None, hue="city", legend=False, palette="Blues_r")

for container in ax4.containers:
    ax4.bar_label(container, fmt='%.1f mm', padding=3, fontsize=10, fontweight='bold')

plt.title("Total Accumulated Rainfall over 7 Days")
plt.xlabel("City")
plt.ylabel("Total Rainfall (mm)")
plt.savefig("chart4_bonus_rainfall.png", bbox_inches='tight')
plt.close()


print("All labeled charts saved successfully as .png images inside your working folder.")
