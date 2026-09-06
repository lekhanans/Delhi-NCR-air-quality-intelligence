<<<<<<< HEAD
import requests
import pandas as pd

# Paste your OpenAQ API key here
API_KEY = "2c183ac83a35956b6d866c01193f06f1b2ef13618cbf125e5a1419aa9a405d9a"

# PM2.5 Sensor ID for New Delhi
SENSOR_ID = 23534

# OpenAQ API URL
url = f"https://api.openaq.org/v3/sensors/{SENSOR_ID}/measurements"

# API header
headers = {
    "X-API-Key": API_KEY
}

# Request 2025 data
params = {
    "limit": 1000,
    "datetime_from": "2025-01-01T00:00:00Z",
    "datetime_to": "2025-12-31T23:59:59Z"
}

# Get data from OpenAQ
response = requests.get(
    url,
    headers=headers,
    params=params
)

print("Status Code:", response.status_code)

# Convert response to JSON
data = response.json()

# Store cleaned measurements
clean_data = []

if "results" in data:

    for item in data["results"]:

        clean_data.append({
            "datetime": item["period"]["datetimeFrom"]["local"],
            "pm25": item["value"]
        })

    # Create DataFrame
    df = pd.DataFrame(clean_data)

    if not df.empty:

        # Convert datetime
        df["datetime"] = pd.to_datetime(df["datetime"])

        # Sort by date
        df = df.sort_values("datetime")

        # Save CSV
        df.to_csv("pm25_2025_data.csv", index=False)

        print("\n2025 data downloaded successfully!")

        print("\nTotal measurements:", len(df))

        print("\nDate range:")
        print("From:", df["datetime"].min())
        print("To:", df["datetime"].max())

        print("\nFirst 10 rows:")
        print(df.head(10))

    else:
        print("No data found for 2025.")

else:
=======
import requests
import pandas as pd

# Paste your OpenAQ API key here
API_KEY = "2c183ac83a35956b6d866c01193f06f1b2ef13618cbf125e5a1419aa9a405d9a"

# PM2.5 Sensor ID for New Delhi
SENSOR_ID = 23534

# OpenAQ API URL
url = f"https://api.openaq.org/v3/sensors/{SENSOR_ID}/measurements"

# API header
headers = {
    "X-API-Key": API_KEY
}

# Request 2025 data
params = {
    "limit": 1000,
    "datetime_from": "2025-01-01T00:00:00Z",
    "datetime_to": "2025-12-31T23:59:59Z"
}

# Get data from OpenAQ
response = requests.get(
    url,
    headers=headers,
    params=params
)

print("Status Code:", response.status_code)

# Convert response to JSON
data = response.json()

# Store cleaned measurements
clean_data = []

if "results" in data:

    for item in data["results"]:

        clean_data.append({
            "datetime": item["period"]["datetimeFrom"]["local"],
            "pm25": item["value"]
        })

    # Create DataFrame
    df = pd.DataFrame(clean_data)

    if not df.empty:

        # Convert datetime
        df["datetime"] = pd.to_datetime(df["datetime"])

        # Sort by date
        df = df.sort_values("datetime")

        # Save CSV
        df.to_csv("pm25_2025_data.csv", index=False)

        print("\n2025 data downloaded successfully!")

        print("\nTotal measurements:", len(df))

        print("\nDate range:")
        print("From:", df["datetime"].min())
        print("To:", df["datetime"].max())

        print("\nFirst 10 rows:")
        print(df.head(10))

    else:
        print("No data found for 2025.")

else:
>>>>>>> f7f87c7d9431ba76418b9176ec3543b83ba303cf
    print("Error:", data)