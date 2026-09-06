import requests
import pandas as pd

API_KEY = "2c183ac83a35956b6d866c01193f06f1b2ef13618cbf125e5a1419aa9a405d9a"

SENSOR_ID = 23534

url = f"https://api.openaq.org/v3/sensors/{SENSOR_ID}/measurements"

headers = {
    "X-API-Key": API_KEY
}

params = {
    "limit": 1000
}

response = requests.get(url, headers=headers, params=params)

print("Status Code:", response.status_code)

data = response.json()

clean_data = []

for item in data["results"]:
    clean_data.append({
        "datetime": item["period"]["datetimeFrom"]["local"],
        "pm25": item["value"]
    })

df = pd.DataFrame(clean_data)

df["datetime"] = pd.to_datetime(df["datetime"])

df = df.sort_values("datetime")

df.to_csv("clean_pm25_data.csv", index=False)

print("\nData cleaned successfully!")
print("\nFirst 10 rows:")
print(df.head(10))

print("\nTotal measurements:", len(df))

print("\nDate range:")
print("From:", df["datetime"].min())
print("To:", df["datetime"].max())