import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

print("Loading combined dataset...")

df = pd.read_csv("combined_pollution_weather.csv")

df["datetime"] = pd.to_datetime(df["datetime"])
df = df.sort_values("datetime").reset_index(drop=True)

# Create time features
df["hour"] = df["datetime"].dt.hour
df["day"] = df["datetime"].dt.day
df["month"] = df["datetime"].dt.month
df["day_of_week"] = df["datetime"].dt.dayofweek

# Create previous PM2.5 features
df["pm25_lag_1"] = df["pm25"].shift(1)
df["pm25_lag_3"] = df["pm25"].shift(3)
df["pm25_lag_6"] = df["pm25"].shift(6)
df["pm25_lag_12"] = df["pm25"].shift(12)
df["pm25_lag_24"] = df["pm25"].shift(24)

# Features used by the proposed coupled model
features = [
    "temperature",
    "humidity",
    "rainfall",
    "pressure",
    "wind_speed",
    "wind_direction",
    "hour",
    "day",
    "month",
    "day_of_week",
    "pm25_lag_1",
    "pm25_lag_3",
    "pm25_lag_6",
    "pm25_lag_12",
    "pm25_lag_24"
]

# Train separate models for each forecast horizon
models = {}

for horizon in [24, 48, 72]:

    print(f"\nTraining {horizon}-hour forecast model...")

    # Future PM2.5 target
    df[f"target_{horizon}h"] = df["pm25"].shift(-horizon)

    training_df = df.dropna(subset=features + [f"target_{horizon}h"])

    X = training_df[features]
    y = training_df[f"target_{horizon}h"]

    # Time-based train/test split
    split_index = int(len(training_df) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)

    print(f"{horizon}-hour MAE:", round(mae, 2))

    joblib.dump(model, f"model_{horizon}h.pkl")

    models[horizon] = mae

print("\n===================================")
print("TRAINING COMPLETED SUCCESSFULLY!")
print("===================================")

print("\nModel Accuracy Summary:")

for horizon, mae in models.items():
    print(f"{horizon} hour forecast MAE: {round(mae, 2)}")

print("\nFiles created:")
print("model_24h.pkl")
print("model_48h.pkl")
print("model_72h.pkl")