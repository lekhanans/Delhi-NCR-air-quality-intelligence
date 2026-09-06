import pandas as pd

print("Loading PM2.5 data...")

# Load PM2.5 datasets
pm25_2025 = pd.read_csv("full_pm25_2025.csv")
pm25_2026 = pd.read_csv("full_pm25_2026.csv")

# Combine both years
pm25_df = pd.concat(
    [pm25_2025, pm25_2026],
    ignore_index=True
)

print("Total PM2.5 records:", len(pm25_df))

# Convert PM2.5 datetime
pm25_df["datetime"] = pd.to_datetime(
    pm25_df["datetime"],
    utc=True
)

# Convert UTC to Indian time and remove timezone
pm25_df["datetime"] = (
    pm25_df["datetime"]
    .dt.tz_convert("Asia/Kolkata")
    .dt.tz_localize(None)
)

# Round timestamps to the hour
pm25_df["datetime"] = pm25_df["datetime"].dt.floor("h")

# Average multiple PM2.5 readings in the same hour
pm25_hourly = (
    pm25_df.groupby("datetime", as_index=False)["pm25"]
    .mean()
)

print("Hourly PM2.5 records:", len(pm25_hourly))


print("\nLoading weather data...")

# Load weather data
weather_df = pd.read_csv("weather_2025_2026.csv")

# Convert datetime
weather_df["datetime"] = pd.to_datetime(weather_df["datetime"])

# Remove timezone if present
if weather_df["datetime"].dt.tz is not None:
    weather_df["datetime"] = weather_df["datetime"].dt.tz_localize(None)

# Round timestamps to the hour
weather_df["datetime"] = weather_df["datetime"].dt.floor("h")

print("Weather records:", len(weather_df))


print("\nCombining pollution and weather data...")

# Merge PM2.5 and weather data
combined_df = pd.merge(
    pm25_hourly,
    weather_df,
    on="datetime",
    how="inner"
)

# Sort by datetime
combined_df = combined_df.sort_values("datetime")

# Remove missing values
combined_df = combined_df.dropna()

# Save final dataset
combined_df.to_csv(
    "combined_pollution_weather.csv",
    index=False
)

print("\n====================================")
print("DATA COMBINED SUCCESSFULLY!")
print("====================================")

print("Total combined records:", len(combined_df))

print("\nColumns:")
print(combined_df.columns.tolist())

print("\nDate range:")
print(combined_df["datetime"].min())
print("to")
print(combined_df["datetime"].max())

print("\nFile created:")
print("combined_pollution_weather.csv")

print("\nFirst 5 rows:")
print(combined_df.head())