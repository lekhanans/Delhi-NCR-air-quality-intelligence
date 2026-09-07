# Delhi NCR Air Quality Intelligence System

Machine learning–based air quality forecasting and environmental intelligence platform for Delhi NCR. It combines historical PM2.5 and weather data with trained regression models to deliver 24/48/72-hour pollution forecasts, risk classification, and scenario simulation through an interactive Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![License](https://img.shields.io/badge/License-Unspecified-lightgrey)

---

## Overview

The system moves beyond simple "current AQI" reporting. It ingests historical pollution (PM2.5) and weather data, engineers time-based and lag features, and trains separate `RandomForestRegressor` models for three forecast horizons (24h / 48h / 72h). Predictions are mapped to a four-tier risk framework (LOW / MODERATE / HIGH / SEVERE) and surfaced through a dashboard covering monitoring, forecasting, early warning, weather correlation, and what-if scenario analysis.

## Features

The dashboard (`app.py`) is organized into the following pages:

| Page | Description |
|---|---|
| **Dashboard** | Current PM2.5 snapshot, risk status banner, temperature/humidity, and recent trend charts. |
| **Forecast Centre** | 24h / 48h / 72h PM2.5 forecasts generated from the trained models. |
| **Early Warning** | Automated risk-level detection across all forecast horizons to flag elevated pollution episodes. |
| **Weather Intelligence** | Relationship between meteorological variables (temperature, humidity, wind, pressure, rainfall) and pollution behaviour. |
| **Scenario Simulator** | Interactive what-if analysis — adjust weather parameters and see the resulting 24h PM2.5 prediction and risk shift. |
| **Analytics** | Model performance (Mean Absolute Error per horizon) and historical PM2.5 distribution / summary statistics. |
| **Delhi NCR View** | Prototype map of NCR (Delhi, Noida, Gurugram, Ghaziabad, Faridabad) colored by reference PM2.5 / risk. |
| **About Project** | Project description, core capabilities, and technology stack. |

**Risk classification** (based on forecasted PM2.5, µg/m³):

| Level | Range |
|---|---|
| LOW | ≤ 60 |
| MODERATE | 61–120 |
| HIGH | 121–250 |
| SEVERE | > 250 |

## Tech Stack

- **App / UI:** Streamlit, Plotly (charts), Folium / streamlit-folium (maps)
- **Data:** Pandas, NumPy
- **Modeling:** scikit-learn (`RandomForestRegressor`), Joblib (model persistence)
- **Data source:** [OpenAQ API](https://openaq.org/) (PM2.5 sensor readings) + a weather dataset

## Project Structure

```
.
├── app.py                          # Streamlit dashboard (entry point)
├── test_openaq.py                  # Pulls PM2.5 readings from the OpenAQ API
├── download_recent_data.py         # Downloads a date-ranged PM2.5 dataset from OpenAQ
├── combine_data.py                 # Merges PM2.5 + weather data into an hourly combined dataset
├── train_forecast_models.py        # Feature engineering + trains the 24h/48h/72h RandomForest models
├── combined_pollution_weather.csv  # Hourly merged pollution + weather dataset (model input)
├── pm25_data.csv / clean_pm25_data.csv  # Raw / cleaned PM2.5 exports
├── model_24h.pkl / model_48h.pkl / model_72h.pkl  # Trained forecast models
└── .gitignore
```

## Setup

**Prerequisites:** Python 3.9+

```bash
git clone https://github.com/lekhanans/Delhi-NCR-air-quality-intelligence.git
cd Delhi-NCR-air-quality-intelligence

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install streamlit pandas numpy joblib plotly folium streamlit-folium requests scikit-learn
```

> There's no `requirements.txt` in the repo yet — the command above installs everything `app.py` and the data/training scripts import. Consider adding one (`pip freeze > requirements.txt`).

## Usage

### Run the dashboard

```bash
streamlit run app.py
```

This loads `combined_pollution_weather.csv` and the three `model_*.pkl` files already included in the repo, so it runs out of the box without retraining.

### Rebuild the data pipeline (optional)

To regenerate the dataset and models from scratch:

```bash
python test_openaq.py            # pull PM2.5 readings from OpenAQ
python download_recent_data.py   # pull a specific date-ranged PM2.5 dataset
python combine_data.py           # merge PM2.5 + weather data → combined_pollution_weather.csv
python train_forecast_models.py  # train and save model_24h.pkl / model_48h.pkl / model_72h.pkl
```

### Current model performance (Mean Absolute Error)

| Horizon | MAE (µg/m³) |
|---|---|
| 24h | 15.69 |
| 48h | 15.71 |
| 72h | 16.58 |

## Known Issues

A few things worth cleaning up before this repo is treated as production-ready:

- **Unresolved merge conflicts.** `test_openaq.py`, `download_recent_data.py`, `combine_data.py`, and `combined_pollution_weather.csv` still contain literal Git conflict markers (`<<<<<<< HEAD` / `=======` / `>>>>>>>`) with identical content duplicated on both sides. These need to be resolved and re-committed.
- **`app.py` contains ~1,200 lines of dead code.** An unconditional `st.stop()` around line 1343 halts execution right after the first, complete copy of the app — everything after it (a second full duplicate of the app, lines ~1344–2560) is leftover from the same unresolved merge and never runs. Safe to delete, but worth doing for maintainability.
- **A live OpenAQ API key is hardcoded** in `test_openaq.py` and `download_recent_data.py`. Rotate/revoke this key in your OpenAQ account and load it from an environment variable (e.g. `os.environ["OPENAQ_API_KEY"]`) instead.
- **No `requirements.txt`** — dependencies currently have to be installed manually (see Setup above).
- The **Delhi NCR View** map is explicitly labeled a prototype in-app: it applies the single current PM2.5 reading to all five cities rather than per-location sensor data.

## License

No license file is currently included in this repository. Add one (e.g. MIT, Apache-2.0) to clarify usage terms for others.
