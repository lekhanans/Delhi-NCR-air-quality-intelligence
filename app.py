import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Delhi NCR Air Quality Intelligence System",
    page_icon="AQ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# GLOBAL CONSTANTS
# =========================================================
DATA_FILE = "combined_pollution_weather.csv"
MODEL_FILES = {
    "24h": "model_24h.pkl",
    "48h": "model_48h.pkl",
    "72h": "model_72h.pkl"
}

RISK_LEVELS = {
    "LOW": {
        "color": "#2ecc71",
        "bg": "rgba(46, 204, 113, 0.12)",
        "message": "No immediate pollution risk detected. Current environmental conditions are stable and preventive monitoring continues."
    },
    "MODERATE": {
        "color": "#f1c40f",
        "bg": "rgba(241, 196, 15, 0.12)",
        "message": "Moderate pollution conditions detected. Enhanced environmental monitoring is recommended."
    },
    "HIGH": {
        "color": "#e67e22",
        "bg": "rgba(230, 126, 34, 0.12)",
        "message": "High pollution risk detected. Preventive action and public awareness measures are recommended."
    },
    "SEVERE": {
        "color": "#e74c3c",
        "bg": "rgba(231, 76, 60, 0.14)",
        "message": "Severe pollution risk detected. Immediate environmental response and public safety measures are recommended."
    }
}

NCR_LOCATIONS = {
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Noida": {"lat": 28.5355, "lon": 77.3910},
    "Gurugram": {"lat": 28.4595, "lon": 77.0266},
    "Ghaziabad": {"lat": 28.6692, "lon": 77.4538},
    "Faridabad": {"lat": 28.4089, "lon": 77.3178}
}

ACCENT = "#22d3ee"
BHUVAN_MAP_URL = "https://bhuvan-app1.nrsc.gov.in/bhuvan2d/bhuvan/bhuvan2d.php"
GOOGLE_DELHI_MAP_URL = "https://www.google.com/maps/@28.6139,77.2090,11z"

# =========================================================
# CUSTOM CSS - PREMIUM DARK THEME
# =========================================================
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: "Times New Roman", Times, serif;
    }

    .stApp {
        background-color: #0a0b0d;
        color: #e5e7eb;
    }

    section[data-testid="stSidebar"] {
        background-color: #0f1113;
        border-right: 1px solid #1f2226;
    }

    section[data-testid="stSidebar"] .stRadio label {
        color: #cbd5e1;
        font-size: 14px;
        font-weight: 500;
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #f8fafc;
    }

    h1, h2, h3, h4 {
        color: #f8fafc !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    p, span, div, label {
        color: #cbd5e1;
    }

    .platform-header {
        padding: 28px 32px;
        background: linear-gradient(180deg, #101215 0%, #0c0d0f 100%);
        border: 1px solid #1f2226;
        border-radius: 14px;
        margin-bottom: 28px;
    }

    .platform-header h1 {
        font-size: 28px !important;
        margin: 0 0 6px 0 !important;
    }

    .platform-header .subtitle {
        color: #8b95a1;
        font-size: 14px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-weight: 500;
    }

    .kpi-card {
        background: #121417;
        border: 1px solid #22262b;
        border-radius: 12px;
        padding: 20px 22px;
        transition: border-color 0.2s ease, transform 0.2s ease;
        height: 100%;
    }

    .kpi-card:hover {
        border-color: #34383f;
        transform: translateY(-2px);
    }

    .kpi-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #8b95a1;
        font-weight: 600;
        margin-bottom: 10px;
    }

    .kpi-value {
        font-size: 30px;
        font-weight: 700;
        color: #f8fafc;
        font-family: "Times New Roman", Times, serif;
        line-height: 1.1;
    }

    .kpi-unit {
        font-size: 13px;
        color: #8b95a1;
        font-weight: 500;
        margin-left: 4px;
    }

    .kpi-delta {
        font-size: 12px;
        margin-top: 8px;
        color: #8b95a1;
    }

    .status-banner {
        border-radius: 12px;
        padding: 20px 24px;
        border: 1px solid;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .status-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .status-text-title {
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 2px;
    }

    .status-text-body {
        font-size: 13.5px;
        color: #a9b2bd;
    }

    .section-title {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
        color: #8b95a1;
        margin: 8px 0 14px 0;
        border-left: 3px solid #22d3ee;
        padding-left: 10px;
    }

    .panel {
        background: #121417;
        border: 1px solid #22262b;
        border-radius: 12px;
        padding: 20px;
    }

    .stButton > button {
        background: linear-gradient(180deg, #1a1d21 0%, #131518 100%);
        color: #e5e7eb;
        border: 1px solid #2c3138;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #22d3ee;
        color: #22d3ee;
    }

    .stButton > button:focus {
        box-shadow: none !important;
    }

    div[data-testid="stMetric"] {
        background: #121417;
        border: 1px solid #22262b;
        border-radius: 12px;
        padding: 14px 18px;
    }

    .stSlider label, .stSelectbox label, .stNumberInput label {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
        font-size: 13.5px !important;
    }

    hr {
        border-color: #1f2226 !important;
    }

    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0b0d;
    }
    ::-webkit-scrollbar-thumb {
        background: #2c3138;
        border-radius: 4px;
    }

    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.03em;
    }

    .footer-note {
        color: #5c6570;
        font-size: 12px;
        text-align: center;
        margin-top: 40px;
        padding-top: 18px;
        border-top: 1px solid #1f2226;
    }

    :root {
        --text-primary: #111827;
        --text-heading: #1f2937;
        --text-body: #374151;
        --text-secondary: #4b5563;
        --text-muted: #6b7280;
        --text-on-dark: #f9fafb;
        --text-on-light: #111827;
        --border-color: #d9dde2;
        --surface: #ffffff;
        --surface-secondary: #f3f4f6;
        --sidebar-background: #2c4355;
    }

    .stApp {
        background-color: var(--surface-secondary);
        color: var(--text-body);
    }

    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-background);
        border-right-color: var(--border-color);
    }

    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] * {
        color: var(--text-on-dark);
    }

    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: var(--text-on-dark) !important;
    }

    .main h1,
    .main h2,
    .main h3,
    .main h4,
    .main h5,
    .main h6,
    .main .platform-header h1,
    .main .section-title,
    .main .status-text-title {
        color: var(--text-primary) !important;
    }

    .platform-header,
    .panel,
    .kpi-card,
    div[data-testid="stMetric"],
    .status-banner {
        background: var(--surface);
        border-color: var(--border-color);
    }

    .main p,
    .main label,
    .main .panel,
    .main .panel p,
    .main .panel span,
    .main .panel label,
    .main .status-text-body,
    .main .stSlider label,
    .main .stSelectbox label,
    .main .stNumberInput label {
        color: var(--text-body) !important;
    }

    .main .platform-header .subtitle,
    .main .kpi-label,
    .main .kpi-unit,
    .main .kpi-delta,
    .main [data-testid="stCaptionContainer"],
    .main [data-testid="stCaptionContainer"] * {
        color: var(--text-muted) !important;
    }

    .main .kpi-value,
    .main div[data-testid="stMetricValue"],
    .main div[data-testid="stMetric"] {
        color: var(--text-on-light) !important;
    }

    .main [style*="color:#f8fafc"],
    .main [style*="color:#e5e7eb"],
    .main [style*="color:#cbd5e1"],
    .main [style*="color:#a9b2bd"],
    .main [style*="color:#8b95a1"] {
        color: var(--text-body) !important;
    }

    .main [data-testid="stAlert"] {
        color: var(--text-body) !important;
    }

    .main [data-testid="stAlert"] p,
    .main [data-testid="stAlert"] span,
    .main [data-testid="stAlert"] div {
        color: var(--text-body) !important;
    }

    .main .stButton > button {
        background: #131518 !important;
        color: var(--text-on-dark) !important;
        border-color: #2c3138 !important;
    }

    .main .stButton > button span {
        color: var(--text-on-dark) !important;
    }

    .main .badge[style*="#2ecc71"] {
        color: #166534 !important;
    }

    .main .badge[style*="#f1c40f"] {
        color: #854d0e !important;
    }

    .main .badge[style*="#e67e22"] {
        color: #9a3412 !important;
    }

    .main .badge[style*="#e74c3c"] {
        color: #991b1b !important;
    }

    .footer-note {
        color: var(--text-muted) !important;
        border-top-color: var(--border-color);
    }

    /* Direct selectors keep custom HTML and Streamlit widgets readable. */
    .platform-header h1,
    .platform-header h1 span {
        color: var(--text-primary) !important;
        font-size: 34px !important;
        font-weight: 700 !important;
    }

    .platform-header .subtitle {
        color: var(--text-secondary) !important;
        font-size: 17px !important;
        font-weight: 500 !important;
    }

    .section-title {
        color: var(--text-heading) !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    }

    .kpi-label {
        color: var(--text-heading) !important;
        font-size: 15px !important;
        font-weight: 600 !important;
    }

    .kpi-value,
    .kpi-card .kpi-value,
    .kpi-card .kpi-value span:not(.badge) {
        color: #111111 !important;
        font-size: 36px !important;
        font-weight: 700 !important;
    }

    .kpi-unit,
    .kpi-card .kpi-unit {
        color: var(--text-secondary) !important;
        font-size: 15px !important;
        font-weight: 500 !important;
    }

    .kpi-delta,
    .kpi-card .kpi-delta {
        color: var(--text-secondary) !important;
    }

    .platform-header,
    .panel,
    .kpi-card,
    .status-banner,
    div[data-testid="stMetric"] {
        color: var(--text-body) !important;
    }

    .platform-header [style*="color:"],
    .panel [style*="color:"],
    .kpi-card [style*="color:"] {
        color: var(--text-body) !important;
    }

    .platform-header h1,
    .panel h1,
    .panel h2,
    .panel h3,
    .panel h4,
    .panel p,
    .panel span,
    .panel div,
    .kpi-card div,
    .kpi-card span {
        color: var(--text-body) !important;
    }

    .platform-header h1,
    .kpi-card .kpi-value {
        color: #111111 !important;
    }

    .kpi-card .kpi-label {
        color: var(--text-heading) !important;
    }

    .kpi-card .kpi-unit {
        color: var(--text-secondary) !important;
    }

    [data-testid="stSlider"] label,
    [data-testid="stSlider"] label p,
    [data-testid="stSlider"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSlider"] [data-baseweb="slider"] ~ div,
    [data-testid="stSlider"] [role="slider"] {
        color: var(--text-body) !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }

    [data-testid="stSlider"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-body) !important;
    }

    [data-testid="stSlider"] [data-testid="stThumbValue"],
    [data-testid="stSlider"] [data-testid="stSliderThumbValue"],
    [data-testid="stSlider"] [data-baseweb="slider"] div {
        color: var(--text-body) !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }

    [data-testid="stSlider"] [data-baseweb="slider"] {
        color: var(--text-body) !important;
    }

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] *,
    [data-testid="stAlert"],
    [data-testid="stAlert"] * {
        color: var(--text-body) !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
    }

    .stButton > button,
    .stButton > button p,
    .stButton > button span {
        background: #131518 !important;
        color: var(--text-on-dark) !important;
        font-size: 15px !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stRadio label p {
        color: var(--text-on-dark) !important;
        font-size: 16px !important;
    }

    .status-text-title {
        color: var(--text-heading) !important;
    }

    .badge[style*="#2ecc71"] {
        color: #166534 !important;
    }

    .badge[style*="#f1c40f"] {
        color: #854d0e !important;
    }

    .badge[style*="#e67e22"] {
        color: #9a3412 !important;
    }

    .badge[style*="#e74c3c"] {
        color: #991b1b !important;
    }

    .status-text-title[style*="#2ecc71"] {
        color: #166534 !important;
    }

    .status-text-title[style*="#f1c40f"] {
        color: #854d0e !important;
    }

    .status-text-title[style*="#e67e22"] {
        color: #9a3412 !important;
    }

    .status-text-title[style*="#e74c3c"] {
        color: #991b1b !important;
    }

    .status-text-body {
        color: var(--text-body) !important;
        font-size: 15px !important;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# COLUMN NAME CANDIDATES (handles common variations)
# =========================================================
COLUMN_CANDIDATES = {
    "datetime": ["datetime", "date_time", "timestamp"],
    "date": ["date"],
    "time": ["time"],
    "pm25": ["pm2.5", "pm25", "pm_2_5", "pm2_5", "pm2.5 (ug/m3)", "pm2.5(ug/m3)", "pm25(ug/m3)"],
    "temperature": ["temperature", "temp", "temp_c", "temperature_c"],
    "humidity": ["humidity", "rh", "relative_humidity"],
    "rainfall": ["rainfall", "rain", "precipitation", "precip"],
    "pressure": ["pressure", "atm_pressure", "sea_level_pressure", "slp"],
    "wind_speed": ["wind_speed", "windspeed", "wind speed", "ws"],
    "wind_direction": ["wind_direction", "winddirection", "wind direction", "wd"]
}


def find_column(df, key):
    """Find the actual column name in df matching a standard key."""
    candidates = COLUMN_CANDIDATES.get(key, [key])
    cols_lower = {c.lower().strip(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    for cand in candidates:
        for col_lower, original in cols_lower.items():
            if cand.lower() in col_lower:
                return original
    return None


# =========================================================
# DATA LOADING
# =========================================================
@st.cache_data(show_spinner=False)
def load_data():
    if not os.path.exists(DATA_FILE):
        return None, f"Data file not found: {DATA_FILE}. Please ensure it is placed in the project directory."

    try:
        with open(DATA_FILE, "r", encoding="utf-8-sig") as data_file:
            has_merge_marker = data_file.readline().strip() == "<<<<<<< HEAD"
        read_options = {"on_bad_lines": "skip"}
        if has_merge_marker:
            read_options["skiprows"] = 1
        df = pd.read_csv(DATA_FILE, **read_options)
    except Exception as e:
        return None, f"Failed to read {DATA_FILE}: {e}"

    if df.empty:
        return None, f"{DATA_FILE} is empty."

    df.columns = [c.strip() for c in df.columns]

    # Resolve datetime column safely
    dt_col = find_column(df, "datetime")
    date_col = find_column(df, "date")
    time_col = find_column(df, "time")

    try:
        if dt_col is not None:
            df["Datetime"] = pd.to_datetime(df[dt_col], errors="coerce")
        elif date_col is not None and time_col is not None:
            df["Datetime"] = pd.to_datetime(
                df[date_col].astype(str) + " " + df[time_col].astype(str),
                errors="coerce"
            )
        elif date_col is not None:
            df["Datetime"] = pd.to_datetime(df[date_col], errors="coerce")
        else:
            df["Datetime"] = pd.date_range(
                end=datetime.now(), periods=len(df), freq="h"
            )
    except Exception:
        df["Datetime"] = pd.date_range(end=datetime.now(), periods=len(df), freq="h")

    # Remove timezone info to avoid merge/comparison problems
    try:
        if pd.api.types.is_datetime64tz_dtype(df["Datetime"]):
            df["Datetime"] = df["Datetime"].dt.tz_localize(None)
    except Exception:
        pass

    df = df.dropna(subset=["Datetime"]).sort_values("Datetime").reset_index(drop=True)

    # Standardize key columns (create standard aliases without deleting originals)
    pm25_col = find_column(df, "pm25")
    if pm25_col is not None:
        df["PM2.5"] = pd.to_numeric(df[pm25_col], errors="coerce")
    else:
        return None, "Could not detect a PM2.5 column in the dataset."

    for key, alias in [
        ("temperature", "Temperature"),
        ("humidity", "Humidity"),
        ("rainfall", "Rainfall"),
        ("pressure", "Pressure"),
        ("wind_speed", "WindSpeed"),
        ("wind_direction", "WindDirection"),
    ]:
        col = find_column(df, key)
        if col is not None:
            df[alias] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[alias] = np.nan

    # Safe missing value handling
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isna().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val if pd.notna(median_val) else 0)

    df["PM2.5"] = df["PM2.5"].clip(lower=0)

    return df, None


@st.cache_resource(show_spinner=False)
def load_models():
    models = {}
    errors = []
    for horizon, filename in MODEL_FILES.items():
        if not os.path.exists(filename):
            errors.append(f"Model file not found: {filename}")
            continue
        try:
            models[horizon] = joblib.load(filename)
        except Exception as e:
            errors.append(f"Failed to load {filename}: {e}")
    return models, errors


# =========================================================
# RISK CLASSIFICATION
# =========================================================
def classify_risk(pm25_value):
    if pm25_value is None or pd.isna(pm25_value):
        return "LOW"
    if pm25_value <= 60:
        return "LOW"
    elif pm25_value <= 120:
        return "MODERATE"
    elif pm25_value <= 250:
        return "HIGH"
    else:
        return "SEVERE"


def calculate_pm25_aqi(pm25_value):
    """Calculate the CPCB PM2.5 sub-index by linear interpolation."""
    if pm25_value is None or pd.isna(pm25_value):
        return None
    breakpoints = [
        (0, 30, 0, 50), (31, 60, 51, 100), (61, 90, 101, 200),
        (91, 120, 201, 300), (121, 250, 301, 400), (251, 500, 401, 500)
    ]
    concentration = max(0, min(float(pm25_value), 500))
    for low_conc, high_conc, low_aqi, high_aqi in breakpoints:
        if concentration <= high_conc:
            return round(low_aqi + (concentration - low_conc) * (high_aqi - low_aqi) / (high_conc - low_conc))
    return 500


def estimate_inversion_strength(wind_speed, humidity):
    """Estimate surface stagnation from available near-surface weather only."""
    if wind_speed is None or humidity is None:
        return None
    wind_factor = max(0.0, min(1.0, 1.0 - float(wind_speed) / 10.0))
    humidity_factor = max(0.0, min(1.0, (float(humidity) - 45.0) / 55.0))
    return round(100 * (0.65 * wind_factor + 0.35 * humidity_factor))


def dispersion_status(inversion_strength):
    if inversion_strength is None:
        return "UNKNOWN"
    if inversion_strength >= 70:
        return "POOR"
    if inversion_strength >= 40:
        return "LIMITED"
    return "FAVOURABLE"


def risk_badge_html(risk_level):
    info = RISK_LEVELS[risk_level]
    return f"""<span class="badge" style="background:{info['bg']}; color:{info['color']}; border:1px solid {info['color']}55;">{risk_level}</span>"""


# =========================================================
# FEATURE ALIGNMENT FOR MODEL PREDICTION
# =========================================================
def build_feature_vector(model, df, overrides=None):
    """
    Build a single-row feature dataframe matching the model's expected
    input features. Uses the most recent data row as the baseline and
    applies any overrides (used by the Scenario Simulator).
    """
    overrides = overrides or {}
    latest = df.iloc[-1]

    alias_map = {
        "temperature": "Temperature",
        "temp": "Temperature",
        "humidity": "Humidity",
        "rh": "Humidity",
        "rainfall": "Rainfall",
        "rain": "Rainfall",
        "pressure": "Pressure",
        "wind_speed": "WindSpeed",
        "windspeed": "WindSpeed",
        "wind_direction": "WindDirection",
        "winddirection": "WindDirection",
        "pm2.5": "PM2.5",
        "pm25": "PM2.5"
    }

    if hasattr(model, "feature_names_in_"):
        feature_names = list(model.feature_names_in_)
    else:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        feature_names = [c for c in numeric_cols if c != "PM2.5"]

    row_data = {}
    for feat in feature_names:
        feat_lower = feat.lower().strip()

        value = None
        if feat in overrides:
            value = overrides[feat]
        elif feat_lower in overrides:
            value = overrides[feat_lower]
        elif feat_lower in alias_map and alias_map[feat_lower] in overrides:
            value = overrides[alias_map[feat_lower]]
        elif feat in df.columns:
            value = latest[feat]
        elif feat_lower in alias_map and alias_map[feat_lower] in df.columns:
            value = latest[alias_map[feat_lower]]
        else:
            matched_col = None
            for col in df.columns:
                if col.lower().strip() == feat_lower:
                    matched_col = col
                    break
            if matched_col is not None:
                value = latest[matched_col]
            else:
                if feat in df.select_dtypes(include=[np.number]).columns:
                    value = df[feat].mean()
                else:
                    value = 0

        if value is None or (isinstance(value, float) and pd.isna(value)):
            value = 0

        row_data[feat] = value

    feature_df = pd.DataFrame([row_data], columns=feature_names)
    return feature_df


def safe_predict(model, feature_df):
    try:
        pred = model.predict(feature_df)
        return float(np.ravel(pred)[0]), None
    except Exception as e:
        return None, str(e)


# =========================================================
# LOAD DATA & MODELS
# =========================================================
df, data_error = load_data()
models, model_errors = load_models()

if data_error:
    st.error(data_error)
    st.stop()

if model_errors:
    for err in model_errors:
        st.warning(err)

latest_row = df.iloc[-1]
current_pm25 = float(latest_row["PM2.5"])
current_temp = float(latest_row["Temperature"]) if pd.notna(latest_row["Temperature"]) else None
current_humidity = float(latest_row["Humidity"]) if pd.notna(latest_row["Humidity"]) else None
current_wind_speed = float(latest_row["WindSpeed"]) if pd.notna(latest_row["WindSpeed"]) else None
current_risk = classify_risk(current_pm25)
current_aqi = calculate_pm25_aqi(current_pm25)
inversion_strength = estimate_inversion_strength(current_wind_speed, current_humidity)
current_dispersion = dispersion_status(inversion_strength)

# =========================================================
# GENERATE FORECASTS (used across multiple pages)
# =========================================================
def generate_all_forecasts():
    results = {}
    for horizon in ["24h", "48h", "72h"]:
        model = models.get(horizon)
        if model is None:
            results[horizon] = {"value": None, "risk": None, "error": "Model not loaded"}
            continue
        feature_df = build_feature_vector(model, df)
        pred, err = safe_predict(model, feature_df)
        if err:
            results[horizon] = {"value": None, "risk": None, "error": err}
        else:
            pred = max(0, pred)
            results[horizon] = {"value": pred, "risk": classify_risk(pred), "error": None}
    return results


forecasts = generate_all_forecasts()

HORIZON_HOURS = {"24h": 24, "48h": 48, "72h": 72}

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
with st.sidebar:
    st.markdown("### AQI INTELLIGENCE")
    st.markdown(
        "<div style='color:#8b95a1; font-size:12px; margin-bottom:20px;'>DELHI NCR CONTROL CENTRE</div>",
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Forecast Centre",
            "Early Warning",
            "Weather Intelligence",
            "Scenario Simulator",
            "Analytics",
            "Delhi NCR View",
            "About Project"
        ],
        label_visibility="collapsed"
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style='font-size:12px; color:#8b95a1; line-height:1.8;'>
        SYSTEM STATUS: <span style='color:#2ecc71;'>ONLINE</span><br>
        MODELS LOADED: {len(models)}/3<br>
        RECORDS: {len(df):,}<br>
        LAST UPDATE: {latest_row['Datetime'].strftime('%d %b, %H:%M')}
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# SHARED HEADER
# =========================================================
def render_header(title, subtitle):
    st.markdown(f"""
    <div class="platform-header">
        <h1>{title}</h1>
        <div class="subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def kpi_card(label, value, unit="", delta=None):
    delta_html = f"<div class='kpi-delta'>{delta}</div>" if delta else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}<span class="kpi-unit">{unit}</span></div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def status_banner(risk_level, custom_message=None):
    info = RISK_LEVELS[risk_level]
    message = custom_message if custom_message else info["message"]
    st.markdown(f"""
    <div class="status-banner" style="border-color:{info['color']}55; background:{info['bg']};">
        <div class="status-dot" style="background:{info['color']};"></div>
        <div>
            <div class="status-text-title" style="color:{info['color']};">{risk_level} RISK LEVEL</div>
            <div class="status-text-body">{message}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# PAGE: DASHBOARD
# =========================================================
if page == "Dashboard":
    render_header("Delhi NCR Air Quality Intelligence System", "Real-Time Environmental Monitoring & Predictive Analytics")

    status_banner(current_risk)

    st.markdown("<div class='section-title'>CURRENT ENVIRONMENTAL SNAPSHOT</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Current PM2.5", f"{current_pm25:.1f}", "µg/m³")
    with c2:
        kpi_card("Risk Level", current_risk, "")
    with c3:
        kpi_card("Temperature", f"{current_temp:.1f}" if current_temp is not None else "N/A", "°C")
    with c4:
        kpi_card("Humidity", f"{current_humidity:.1f}" if current_humidity is not None else "N/A", "%")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>ATMOSPHERIC COUPLING INDICATORS</div>", unsafe_allow_html=True)
    a1, a2, a3 = st.columns(3)
    with a1:
        kpi_card("PM2.5 AQI", str(current_aqi) if current_aqi is not None else "N/A", "")
    with a2:
        kpi_card("Inversion / Stagnation Proxy", str(inversion_strength) if inversion_strength is not None else "N/A", "%")
    with a3:
        kpi_card("Pollution Dispersion", current_dispersion, "")
    st.caption("The inversion value is a near-surface stagnation proxy derived from wind speed and humidity. True inversion strength requires vertical temperature or PBL-height observations.")
    st.info("Coupled-model data readiness: PM2.5 and surface weather are available. PM10, O3, NOx, PBL height, vertical temperature profiles, and satellite fire-plume inputs still need to be connected for full WRF-Chem-style forecasting.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>PM2.5 FORECAST OVERVIEW</div>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    for col, horizon, label in zip([f1, f2, f3], ["24h", "48h", "72h"], ["24-HOUR FORECAST", "48-HOUR FORECAST", "72-HOUR FORECAST"]):
        with col:
            res = forecasts[horizon]
            if res["value"] is not None:
                risk = res["risk"]
                kpi_card(label, f"{res['value']:.1f}", "µg/m³", delta=risk_badge_html(risk))
            else:
                kpi_card(label, "N/A", "", delta=f"<span style='color:#e74c3c;'>{res['error']}</span>")

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("<div class='section-title'>HISTORICAL POLLUTION TREND</div>", unsafe_allow_html=True)
        recent_df = df.tail(500)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=recent_df["Datetime"], y=recent_df["PM2.5"],
            mode="lines", line=dict(color=ACCENT, width=2),
            fill="tozeroy", fillcolor="rgba(34, 211, 238, 0.08)",
            name="PM2.5"
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#121417",
            plot_bgcolor="#121417",
            font=dict(color="#cbd5e1", family="Times New Roman"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=340,
            xaxis=dict(gridcolor="#1f2226"),
            yaxis=dict(gridcolor="#1f2226", title="PM2.5 (µg/m³)")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("<div class='section-title'>FORECAST COMPARISON</div>", unsafe_allow_html=True)
        horizons_valid = [h for h in ["24h", "48h", "72h"] if forecasts[h]["value"] is not None]
        values_valid = [forecasts[h]["value"] for h in horizons_valid]
        colors_valid = [RISK_LEVELS[forecasts[h]["risk"]]["color"] for h in horizons_valid]

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=horizons_valid, y=values_valid,
            marker_color=colors_valid,
            text=[f"{v:.1f}" for v in values_valid],
            textposition="outside"
        ))
        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor="#121417",
            plot_bgcolor="#121417",
            font=dict(color="#cbd5e1", family="Times New Roman"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=340,
            yaxis=dict(gridcolor="#1f2226", title="PM2.5 (µg/m³)"),
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>EARLY WARNING STATUS</div>", unsafe_allow_html=True)
    warn_cols = st.columns(3)
    for col, horizon, label in zip(warn_cols, ["24h", "48h", "72h"], ["24H", "48H", "72H"]):
        with col:
            res = forecasts[horizon]
            if res["value"] is not None and res["risk"] in ["HIGH", "SEVERE"]:
                st.markdown(f"""
                <div class="panel" style="border-color:{RISK_LEVELS[res['risk']]['color']}55;">
                    <div style="font-weight:700; color:{RISK_LEVELS[res['risk']]['color']};">{label} WARNING ACTIVE</div>
                    <div style="font-size:13px; color:#a9b2bd; margin-top:6px;">Predicted PM2.5: {res['value']:.1f} µg/m³ — {res['risk']} risk expected.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="panel">
                    <div style="font-weight:700; color:#2ecc71;">{label} NORMAL</div>
                    <div style="font-size:13px; color:#a9b2bd; margin-top:6px;">No elevated risk expected in this horizon.</div>
                </div>
                """, unsafe_allow_html=True)


# =========================================================
# PAGE: FORECAST CENTRE
# =========================================================
elif page == "Forecast Centre":
    render_header("Forecast Centre", "Machine Learning Based PM2.5 Prediction — 24H / 48H / 72H")

    cols = st.columns(3)
    for col, horizon in zip(cols, ["24h", "48h", "72h"]):
        with col:
            res = forecasts[horizon]
            target_time = latest_row["Datetime"] + timedelta(hours=HORIZON_HOURS[horizon])
            if res["value"] is not None:
                st.markdown(f"""
                <div class="panel">
                    <div class="kpi-label">FORECAST HORIZON</div>
                    <div style="font-size:20px; font-weight:700; color:#f8fafc; margin-bottom:14px;">{horizon.upper()}</div>
                    <div class="kpi-label">PREDICTED PM2.5</div>
                    <div class="kpi-value">{res['value']:.1f}<span class="kpi-unit">µg/m³</span></div>
                    <div style="margin:12px 0;">{risk_badge_html(res['risk'])}</div>
                    <div class="kpi-label">TARGET TIME</div>
                    <div style="font-size:13.5px; color:#cbd5e1;">{target_time.strftime('%d %b %Y, %H:%M')}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="panel">
                    <div class="kpi-label">FORECAST HORIZON</div>
                    <div style="font-size:20px; font-weight:700; color:#f8fafc;">{horizon.upper()}</div>
                    <div style="color:#e74c3c; margin-top:14px; font-size:13px;">Unable to generate forecast: {res['error']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>FORECAST TRAJECTORY</div>", unsafe_allow_html=True)

    valid_horizons = [h for h in ["24h", "48h", "72h"] if forecasts[h]["value"] is not None]
    if valid_horizons:
        x_points = [latest_row["Datetime"]] + [latest_row["Datetime"] + timedelta(hours=HORIZON_HOURS[h]) for h in valid_horizons]
        y_points = [current_pm25] + [forecasts[h]["value"] for h in valid_horizons]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_points, y=y_points, mode="lines+markers",
            line=dict(color=ACCENT, width=3),
            marker=dict(size=10, color=[RISK_LEVELS[current_risk]["color"]] + [RISK_LEVELS[forecasts[h]["risk"]]["color"] for h in valid_horizons]),
            name="PM2.5 Trajectory"
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#121417",
            plot_bgcolor="#121417",
            font=dict(color="#cbd5e1"),
            margin=dict(l=10, r=10, t=20, b=10),
            height=380,
            xaxis=dict(gridcolor="#1f2226", title="Time"),
            yaxis=dict(gridcolor="#1f2226", title="PM2.5 (µg/m³)")
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>RECENT HISTORICAL CONTEXT</div>", unsafe_allow_html=True)
    recent = df.tail(200)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=recent["Datetime"], y=recent["PM2.5"], mode="lines",
                               line=dict(color="#8b95a1", width=1.5), name="Historical PM2.5"))
    fig3.update_layout(
        template="plotly_dark", paper_bgcolor="#121417", plot_bgcolor="#121417",
        font=dict(color="#cbd5e1"), margin=dict(l=10, r=10, t=20, b=10), height=300,
        xaxis=dict(gridcolor="#1f2226"), yaxis=dict(gridcolor="#1f2226", title="PM2.5 (µg/m³)")
    )
    st.plotly_chart(fig3, use_container_width=True)


# =========================================================
# PAGE: EARLY WARNING
# =========================================================
elif page == "Early Warning":
    render_header("Early Warning System", "Automated Risk Detection Across Forecast Horizons")

    status_banner(current_risk, custom_message=f"Current observed PM2.5 is {current_pm25:.1f} µg/m³.")

    st.markdown("<div class='section-title'>WARNING TIMELINE</div>", unsafe_allow_html=True)
    for horizon, label in zip(["24h", "48h", "72h"], ["24-HOUR HORIZON", "48-HOUR HORIZON", "72-HOUR HORIZON"]):
        res = forecasts[horizon]
        if res["value"] is None:
            st.markdown(f"""
            <div class="panel" style="margin-bottom:14px;">
                <div style="font-weight:700; color:#e74c3c;">{label} — DATA UNAVAILABLE</div>
                <div style="font-size:13px; color:#a9b2bd; margin-top:4px;">{res['error']}</div>
            </div>
            """, unsafe_allow_html=True)
            continue

        risk = res["risk"]
        info = RISK_LEVELS[risk]
        target_time = latest_row["Datetime"] + timedelta(hours=HORIZON_HOURS[horizon])
        st.markdown(f"""
        <div class="panel" style="margin-bottom:14px; border-color:{info['color']}55;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-weight:700; color:#f8fafc; font-size:15px;">{label}</div>
                    <div style="font-size:13px; color:#a9b2bd; margin-top:4px;">Target: {target_time.strftime('%d %b, %H:%M')} — Predicted PM2.5: {res['value']:.1f} µg/m³</div>
                </div>
                <div>{risk_badge_html(risk)}</div>
            </div>
            <div style="font-size:13.5px; color:#cbd5e1; margin-top:12px;">{info['message']}</div>
        </div>
        """, unsafe_allow_html=True)

    active_warnings = sum(1 for h in ["24h", "48h", "72h"] if forecasts[h]["value"] is not None and forecasts[h]["risk"] in ["HIGH", "SEVERE"])
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>SUMMARY</div>", unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    with s1:
        kpi_card("Active Warnings", str(active_warnings), "of 3")
    with s2:
        kpi_card("Current Status", current_risk, "")
    with s3:
        worst = max(
            [forecasts[h]["risk"] for h in ["24h", "48h", "72h"] if forecasts[h]["value"] is not None] + [current_risk],
            key=lambda r: ["LOW", "MODERATE", "HIGH", "SEVERE"].index(r)
        )
        kpi_card("Peak Risk Expected", worst, "")


# =========================================================
# PAGE: WEATHER INTELLIGENCE
# =========================================================
elif page == "Weather Intelligence":
    render_header("Weather Intelligence", "Relationship Between Meteorological Factors and PM2.5")

    weather_vars = {
        "Temperature": "°C",
        "Humidity": "%",
        "Rainfall": "mm",
        "Pressure": "hPa",
        "WindSpeed": "m/s",
        "WindDirection": "°"
    }

    available_vars = [v for v in weather_vars if df[v].notna().any() and df[v].nunique() > 1]

    if not available_vars:
        st.warning("No usable weather variables were detected in the dataset.")
    else:
        selected_var = st.selectbox("Select Weather Parameter", available_vars)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='section-title'>PM2.5 vs {selected_var.upper()}</div>", unsafe_allow_html=True)
            fig = px.scatter(
                df, x=selected_var, y="PM2.5",
                color="PM2.5", color_continuous_scale="Turbo",
                opacity=0.6
            )
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#121417", plot_bgcolor="#121417",
                font=dict(color="#cbd5e1"), margin=dict(l=10, r=10, t=10, b=10), height=380,
                xaxis=dict(gridcolor="#1f2226"), yaxis=dict(gridcolor="#1f2226")
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(f"<div class='section-title'>{selected_var.upper()} TREND OVER TIME</div>", unsafe_allow_html=True)
            recent = df.tail(300)
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=recent["Datetime"], y=recent[selected_var], mode="lines",
                                       line=dict(color=ACCENT, width=2)))
            fig2.update_layout(
                template="plotly_dark", paper_bgcolor="#121417", plot_bgcolor="#121417",
                font=dict(color="#cbd5e1"), margin=dict(l=10, r=10, t=10, b=10), height=380,
                xaxis=dict(gridcolor="#1f2226"), yaxis=dict(gridcolor="#1f2226")
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>CORRELATION MATRIX</div>", unsafe_allow_html=True)
        corr_cols = ["PM2.5"] + available_vars
        corr_matrix = df[corr_cols].corr()
        fig3 = px.imshow(
            corr_matrix, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1
        )
        fig3.update_layout(
            template="plotly_dark", paper_bgcolor="#121417", plot_bgcolor="#121417",
            font=dict(color="#cbd5e1"), margin=dict(l=10, r=10, t=10, b=10), height=420
        )
        st.plotly_chart(fig3, use_container_width=True)


# =========================================================
# PAGE: SCENARIO SIMULATOR
# =========================================================
elif page == "Scenario Simulator":
    render_header("Scenario Simulator", "Interactive What-If Analysis Using the 24-Hour Forecasting Model")

    model_24h = models.get("24h")
    if model_24h is None:
        st.error("The 24-hour model is not available. Scenario simulation requires model_24h.pkl.")
    else:
        st.markdown("<div class='section-title'>ADJUST ENVIRONMENTAL PARAMETERS</div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            sim_temp = st.slider(
                "Temperature (°C)",
                float(df["Temperature"].min()), float(df["Temperature"].max()),
                float(current_temp) if current_temp is not None else float(df["Temperature"].mean())
            )
            sim_humidity = st.slider(
                "Humidity (%)",
                float(df["Humidity"].min()), float(df["Humidity"].max()),
                float(current_humidity) if current_humidity is not None else float(df["Humidity"].mean())
            )
        with col2:
            sim_rainfall = st.slider(
                "Rainfall (mm)",
                float(df["Rainfall"].min()), float(df["Rainfall"].max()),
                float(latest_row["Rainfall"])
            )
            sim_pressure = st.slider(
                "Pressure (hPa)",
                float(df["Pressure"].min()), float(df["Pressure"].max()),
                float(latest_row["Pressure"])
            )
        with col3:
            sim_wind_speed = st.slider(
                "Wind Speed (m/s)",
                float(df["WindSpeed"].min()), float(df["WindSpeed"].max()),
                float(latest_row["WindSpeed"])
            )
            sim_wind_dir = st.slider(
                "Wind Direction (°)",
                float(df["WindDirection"].min()), float(df["WindDirection"].max()),
                float(latest_row["WindDirection"])
            )

        st.markdown("<br>", unsafe_allow_html=True)
        run_sim = st.button("▶ RUN SCENARIO SIMULATION", use_container_width=False)

        if run_sim:
            overrides = {
                "Temperature": sim_temp,
                "Humidity": sim_humidity,
                "Rainfall": sim_rainfall,
                "Pressure": sim_pressure,
                "WindSpeed": sim_wind_speed,
                "WindDirection": sim_wind_dir
            }

            baseline_features = build_feature_vector(model_24h, df)
            baseline_pred, base_err = safe_predict(model_24h, baseline_features)

            scenario_features = build_feature_vector(model_24h, df, overrides=overrides)
            scenario_pred, sim_err = safe_predict(model_24h, scenario_features)

            if base_err or sim_err:
                st.error(f"Simulation failed: {base_err or sim_err}")
            else:
                baseline_pred = max(0, baseline_pred)
                scenario_pred = max(0, scenario_pred)
                diff = scenario_pred - baseline_pred
                scenario_risk = classify_risk(scenario_pred)
                baseline_risk = classify_risk(baseline_pred)

                st.markdown("<div class='section-title'>SIMULATION RESULT</div>", unsafe_allow_html=True)
                r1, r2, r3 = st.columns(3)
                with r1:
                    kpi_card("Baseline Forecast (24H)", f"{baseline_pred:.1f}", "µg/m³", delta=risk_badge_html(baseline_risk))
                with r2:
                    kpi_card("Simulated Forecast (24H)", f"{scenario_pred:.1f}", "µg/m³", delta=risk_badge_html(scenario_risk))
                with r3:
                    direction = "increase" if diff > 0 else ("decrease" if diff < 0 else "no change")
                    color = "#e74c3c" if diff > 0 else ("#2ecc71" if diff < 0 else "#8b95a1")
                    kpi_card("Predicted Difference", f"{diff:+.1f}", "µg/m³", delta=f"<span style='color:{color};'>{direction}</span>")

                st.markdown("<br>", unsafe_allow_html=True)
                interpretation = (
                    f"Under the simulated environmental conditions, PM2.5 is projected to {direction} "
                    f"by {abs(diff):.1f} µg/m³ relative to the current baseline forecast, shifting the "
                    f"expected risk classification from {baseline_risk} to {scenario_risk}. "
                    f"This suggests that the adjusted meteorological parameters have a "
                    f"{'notable' if abs(diff) > 10 else 'moderate' if abs(diff) > 3 else 'minor'} "
                    f"influence on near-term air quality under current conditions."
                )
                st.markdown(f"""
                <div class="panel">
                    <div class="kpi-label">PROFESSIONAL INTERPRETATION</div>
                    <div style="font-size:14px; color:#cbd5e1; margin-top:8px; line-height:1.6;">{interpretation}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='section-title'>BASELINE VS SCENARIO COMPARISON</div>", unsafe_allow_html=True)
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=["Baseline Forecast", "Scenario Forecast"],
                    y=[baseline_pred, scenario_pred],
                    marker_color=[RISK_LEVELS[baseline_risk]["color"], RISK_LEVELS[scenario_risk]["color"]],
                    text=[f"{baseline_pred:.1f}", f"{scenario_pred:.1f}"],
                    textposition="outside"
                ))
                fig.update_layout(
                    template="plotly_dark", paper_bgcolor="#121417", plot_bgcolor="#121417",
                    font=dict(color="#cbd5e1"), margin=dict(l=10, r=10, t=20, b=10), height=380,
                    yaxis=dict(gridcolor="#1f2226", title="PM2.5 (µg/m³)"), showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Adjust the parameters above and click 'Run Scenario Simulation' to generate a prediction using the trained 24-hour model.")


# =========================================================
# PAGE: ANALYTICS
# =========================================================
elif page == "Analytics":
    render_header("Analytics", "Model Performance & Historical Data Insights")

    st.markdown("<div class='section-title'>MODEL PERFORMANCE (MEAN ABSOLUTE ERROR)</div>", unsafe_allow_html=True)
    mae_values = {"24h": 15.69, "48h": 15.71, "72h": 16.58}
    m1, m2, m3 = st.columns(3)
    for col, horizon in zip([m1, m2, m3], ["24h", "48h", "72h"]):
        with col:
            kpi_card(f"{horizon.upper()} MODEL MAE", f"{mae_values[horizon]:.2f}", "µg/m³")

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("<div class='section-title'>MAE COMPARISON</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(mae_values.keys()), y=list(mae_values.values()),
            marker_color=ACCENT,
            text=[f"{v:.2f}" for v in mae_values.values()],
            textposition="outside"
        ))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#121417", plot_bgcolor="#121417",
            font=dict(color="#cbd5e1"), margin=dict(l=10, r=10, t=20, b=10), height=360,
            yaxis=dict(gridcolor="#1f2226", title="MAE (µg/m³)"), showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("<div class='section-title'>HISTORICAL PM2.5 DISTRIBUTION</div>", unsafe_allow_html=True)
        fig2 = px.histogram(df, x="PM2.5", nbins=40, color_discrete_sequence=[ACCENT])
        fig2.update_layout(
            template="plotly_dark", paper_bgcolor="#121417", plot_bgcolor="#121417",
            font=dict(color="#cbd5e1"), margin=dict(l=10, r=10, t=20, b=10), height=360,
            xaxis=dict(gridcolor="#1f2226"), yaxis=dict(gridcolor="#1f2226")
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>DATASET SUMMARY STATISTICS</div>", unsafe_allow_html=True)
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        kpi_card("Average PM2.5", f"{df['PM2.5'].mean():.1f}", "µg/m³")
    with d2:
        kpi_card("Maximum PM2.5", f"{df['PM2.5'].max():.1f}", "µg/m³")
    with d3:
        kpi_card("Minimum PM2.5", f"{df['PM2.5'].min():.1f}", "µg/m³")
    with d4:
        kpi_card("Total Measurements", f"{len(df):,}", "")


# =========================================================
# PAGE: DELHI NCR VIEW
# =========================================================
elif page == "Delhi NCR View":
    render_header("Delhi NCR Geographic Intelligence", "Live PM2.5 Detection View")

    st.markdown("<div class='section-title'>ML AIR-POLLUTION PREDICTION MAP</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="panel" style="margin-bottom:20px; border-color:#22d3ee55;">
        <div style="color:#22d3ee; font-weight:700; font-size:13.5px;">AIR QUALITY MONITORING ACTIVE</div>
        <div style="font-size:13px; color:#a9b2bd; margin-top:6px;">
        The markers show the latest PM2.5 reading available to this application, classified by health risk.
        The current dataset is sourced from the primary Delhi monitor; NCR locations are regional reference points
        until individual live sensors are connected.
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected_horizon = st.selectbox(
        "Prediction horizon",
        ["24h", "48h", "72h"],
        format_func=lambda value: f"{value.replace('h', '-hour')} PM2.5 forecast"
    )
    selected_forecast = forecasts[selected_horizon]
    predicted_pm25 = selected_forecast["value"]
    predicted_risk = selected_forecast["risk"] or "LOW"

    prediction_points = {
        "Delhi Centre": (28.7041, 77.1025),
        "Noida": (28.5355, 77.3910),
        "Gurugram": (28.4595, 77.0266),
        "Ghaziabad": (28.6692, 77.4538),
        "Faridabad": (28.4089, 77.3178),
        "Dwarka": (28.5921, 77.0460),
        "Rohini": (28.7495, 77.0565),
        "Greater Kailash": (28.5494, 77.2381)
    }
    grid_enabled = st.checkbox("Show Delhi prediction grid", value=True)
    if grid_enabled:
        grid_lats = np.linspace(28.48, 28.86, 7)
        grid_lons = np.linspace(76.84, 77.35, 8)
        for row_index, grid_lat in enumerate(grid_lats):
            for column_index, grid_lon in enumerate(grid_lons):
                prediction_points[f"Delhi grid {row_index + 1}-{column_index + 1}"] = (grid_lat, grid_lon)
    base_prediction = predicted_pm25 if predicted_pm25 is not None else current_pm25
    map_df = pd.DataFrame([
        {"Point": point, "lat": lat, "lon": lon}
        for point, (lat, lon) in prediction_points.items()
    ])
    # The historical file has one monitor and no station coordinates. Apply a
    # documented spatial proxy so the dashboard can show threshold-based colors.
    map_df["Predicted PM2.5"] = (
        base_prediction * (0.42 + 1.23 * np.exp(-(((map_df["lat"] - 28.64) / 0.16) ** 2
                                                  + ((map_df["lon"] - 77.18) / 0.20) ** 2)))
    ).round(1)
    map_df["Risk"] = map_df["Predicted PM2.5"].apply(classify_risk)

    air_map = folium.Map(
        location=[28.62, 77.20],
        zoom_start=9,
        tiles="OpenStreetMap",
        control_scale=True,
        width="100%",
        height=560
    )
    for _, point in map_df.iterrows():
        risk_color = RISK_LEVELS[point["Risk"]]["color"]
        folium.CircleMarker(
            location=[point["lat"], point["lon"]],
            radius=max(7, min(24, 7 + point["Predicted PM2.5"] / 14)),
            color=risk_color,
            fill=True,
            fill_color=risk_color,
            fill_opacity=0.62,
            weight=1,
            tooltip=point["Point"],
            popup=(f"<b>{point['Point']}</b><br>"
                   f"Predicted PM2.5: {point['Predicted PM2.5']:.1f} µg/m³<br>"
                   f"Risk: {point['Risk']}<br>{selected_horizon} forecast")
        ).add_to(air_map)

    legend_html = """
    <div style="position: fixed; bottom: 24px; right: 18px; z-index: 9999;
                background: white; padding: 10px 12px; border-radius: 6px;
                box-shadow: 0 1px 6px #555; font: 12px Arial; color: #222;">
        <b>PM2.5 forecast risk</b><br>
        <span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:#2ecc71;"></span> LOW<br>
        <span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:#f1c40f;"></span> MODERATE<br>
        <span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:#e67e22;"></span> HIGH<br>
        <span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:#e74c3c;"></span> SEVERE
    </div>
    """
    air_map.get_root().html.add_child(folium.Element(legend_html))
    st_folium(air_map, use_container_width=True, height=560, returned_objects=[])

    st.caption(
        f"{selected_horizon} ML prediction range: {map_df['Predicted PM2.5'].min():.1f}-{map_df['Predicted PM2.5'].max():.1f} µg/m³ | "
        f"Risk colors are based on PM2.5 thresholds; spatial values are a Delhi-monitor proxy, not independent sensors | "
        f"{len(prediction_points)} map points | Baseline trained from historical Delhi monitor data ending "
        f"{latest_row['Datetime'].strftime('%d %b %Y, %H:%M')}"
        if predicted_pm25 is not None else
        "Models unavailable for this horizon; showing the latest observed PM2.5 value."
    )

    st.markdown("<div class='section-title'>PREDICTION POINT SUMMARY</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for col, point in zip(cols, list(prediction_points)[:4]):
        with col:
            point_result = map_df.loc[map_df["Point"] == point].iloc[0]
            point_value = point_result["Predicted PM2.5"]
            point_risk = point_result["Risk"]
            st.markdown(f"""
            <div class="panel">
                <div class="kpi-label">{point.upper()}</div>
                <div style="font-size:13px; color:#a9b2bd; margin-top:6px;">{selected_horizon} predicted PM2.5</div>
                <div class="kpi-value" style="font-size:22px;">{point_value:.1f}</div>
                <div style="margin-top:8px;">{risk_badge_html(point_risk)}</div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# PAGE: ABOUT PROJECT
# =========================================================
elif page == "About Project":
    render_header("About the Project", "Delhi NCR Air Quality Intelligence and Pollution Forecasting System")

    st.markdown("""
    <div class="panel">
        <p style="font-size:14.5px; line-height:1.8; color:#cbd5e1;">
        The Delhi NCR Air Quality Intelligence and Pollution Forecasting System is an environmental
        decision-support platform designed to move beyond traditional pollution monitoring. Rather than
        simply reporting current air quality, this system integrates historical pollution and weather
        data with machine learning models to deliver forward-looking, actionable intelligence.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>CORE CAPABILITIES</div>", unsafe_allow_html=True)

    capabilities = [
        ("Predictive Forecasting", "Machine learning models trained on historical pollution and weather data to anticipate future PM2.5 levels."),
        ("24-Hour Forecasting", "Short-term PM2.5 prediction to support immediate operational and public health decisions."),
        ("48-Hour Forecasting", "Medium-term outlook enabling proactive planning for institutions and municipal bodies."),
        ("72-Hour Forecasting", "Extended horizon forecasting to anticipate multi-day pollution episodes."),
        ("Weather Intelligence", "Analysis of the relationship between meteorological variables and pollution behaviour."),
        ("Early Warning", "Automated risk detection across all forecast horizons to flag elevated pollution episodes."),
        ("Risk Classification", "A structured LOW / MODERATE / HIGH / SEVERE framework applied consistently across the platform."),
        ("Scenario Simulation", "Interactive what-if analysis using the trained models to evaluate the impact of changing environmental conditions."),
        ("Environmental Decision Support", "Consolidated intelligence intended to support preventive and responsive environmental action.")
    ]

    for title, desc in capabilities:
        st.markdown(f"""
        <div class="panel" style="margin-bottom:12px;">
            <div style="font-weight:700; color:#f8fafc; font-size:14.5px;">{title}</div>
            <div style="font-size:13.5px; color:#a9b2bd; margin-top:6px; line-height:1.6;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>TECHNOLOGY STACK</div>", unsafe_allow_html=True)
    tech_cols = st.columns(5)
    for col, tech in zip(tech_cols, ["Python", "Streamlit", "Pandas / NumPy", "Plotly", "Joblib / Scikit-learn"]):
        with col:
            st.markdown(f"""
            <div class="panel" style="text-align:center;">
                <div style="font-size:13.5px; font-weight:600; color:#22d3ee;">{tech}</div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div class="footer-note">
    DELHI NCR AIR QUALITY INTELLIGENCE SYSTEM &nbsp;•&nbsp; PREDICTIVE ENVIRONMENTAL MONITORING PLATFORM
</div>
""", unsafe_allow_html=True)
st.stop()
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Delhi NCR Air Quality Intelligence System",
    page_icon="AQ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# GLOBAL CONSTANTS
# =========================================================
DATA_FILE = "combined_pollution_weather.csv"
MODEL_FILES = {
    "24h": "model_24h.pkl",
    "48h": "model_48h.pkl",
    "72h": "model_72h.pkl"
}

RISK_LEVELS = {
    "LOW": {
        "color": "#2ecc71",
        "bg": "rgba(46, 204, 113, 0.12)",
        "message": "No immediate pollution risk detected. Current environmental conditions are stable and preventive monitoring continues."
    },
    "MODERATE": {
        "color": "#f1c40f",
        "bg": "rgba(241, 196, 15, 0.12)",
        "message": "Moderate pollution conditions detected. Enhanced environmental monitoring is recommended."
    },
    "HIGH": {
        "color": "#e67e22",
        "bg": "rgba(230, 126, 34, 0.12)",
        "message": "High pollution risk detected. Preventive action and public awareness measures are recommended."
    },
    "SEVERE": {
        "color": "#e74c3c",
        "bg": "rgba(231, 76, 60, 0.14)",
        "message": "Severe pollution risk detected. Immediate environmental response and public safety measures are recommended."
    }
}

NCR_LOCATIONS = {
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Noida": {"lat": 28.5355, "lon": 77.3910},
    "Gurugram": {"lat": 28.4595, "lon": 77.0266},
    "Ghaziabad": {"lat": 28.6692, "lon": 77.4538},
    "Faridabad": {"lat": 28.4089, "lon": 77.3178}
}

ACCENT = "#22d3ee"

# =========================================================
# CUSTOM CSS - PREMIUM DARK THEME
# =========================================================
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: "Times New Roman", Times, serif;
    }

    .stApp {
        background-color: #0a0b0d;
        color: #e5e7eb;
    }

    section[data-testid="stSidebar"] {
        background-color: #0f1113;
        border-right: 1px solid #1f2226;
    }

    section[data-testid="stSidebar"] .stRadio label {
        color: #cbd5e1;
        font-size: 14px;
        font-weight: 500;
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #f8fafc;
    }

    h1, h2, h3, h4 {
        color: #f8fafc !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    p, span, div, label {
        color: #cbd5e1;
    }

    .platform-header {
        padding: 28px 32px;
        background: linear-gradient(180deg, #101215 0%, #0c0d0f 100%);
        border: 1px solid #1f2226;
        border-radius: 14px;
        margin-bottom: 28px;
    }

    .platform-header h1 {
        font-size: 28px !important;
        margin: 0 0 6px 0 !important;
    }

    .platform-header .subtitle {
        color: #8b95a1;
        font-size: 14px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-weight: 500;
    }

    .kpi-card {
        background: #121417;
        border: 1px solid #22262b;
        border-radius: 12px;
        padding: 20px 22px;
        transition: border-color 0.2s ease, transform 0.2s ease;
        height: 100%;
    }

    .kpi-card:hover {
        border-color: #34383f;
        transform: translateY(-2px);
    }

    .kpi-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #8b95a1;
        font-weight: 600;
        margin-bottom: 10px;
    }

    .kpi-value {
        font-size: 30px;
        font-weight: 700;
        color: #f8fafc;
        font-family: "Times New Roman", Times, serif;
        line-height: 1.1;
    }

    .kpi-unit {
        font-size: 13px;
        color: #8b95a1;
        font-weight: 500;
        margin-left: 4px;
    }

    .kpi-delta {
        font-size: 12px;
        margin-top: 8px;
        color: #8b95a1;
    }

    .status-banner {
        border-radius: 12px;
        padding: 20px 24px;
        border: 1px solid;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .status-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .status-text-title {
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 2px;
    }

    .status-text-body {
        font-size: 13.5px;
        color: #a9b2bd;
    }

    .section-title {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
        color: #8b95a1;
        margin: 8px 0 14px 0;
        border-left: 3px solid #22d3ee;
        padding-left: 10px;
    }

    .panel {
        background: #121417;
        border: 1px solid #22262b;
        border-radius: 12px;
        padding: 20px;
    }

    .stButton > button {
        background: linear-gradient(180deg, #1a1d21 0%, #131518 100%);
        color: #e5e7eb;
        border: 1px solid #2c3138;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #22d3ee;
        color: #22d3ee;
    }

    .stButton > button:focus {
        box-shadow: none !important;
    }

    div[data-testid="stMetric"] {
        background: #121417;
        border: 1px solid #22262b;
        border-radius: 12px;
        padding: 14px 18px;
    }

    .stSlider label, .stSelectbox label, .stNumberInput label {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
        font-size: 13.5px !important;
    }

    hr {
        border-color: #1f2226 !important;
    }

    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0b0d;
    }
    ::-webkit-scrollbar-thumb {
        background: #2c3138;
        border-radius: 4px;
    }

    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.03em;
    }

    .footer-note {
        color: #5c6570;
        font-size: 12px;
        text-align: center;
        margin-top: 40px;
        padding-top: 18px;
        border-top: 1px solid #1f2226;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# COLUMN NAME CANDIDATES (handles common variations)
# =========================================================
COLUMN_CANDIDATES = {
    "datetime": ["datetime", "date_time", "timestamp"],
    "date": ["date"],
    "time": ["time"],
    "pm25": ["pm2.5", "pm25", "pm_2_5", "pm2_5", "pm2.5 (ug/m3)", "pm2.5(ug/m3)", "pm25(ug/m3)"],
    "temperature": ["temperature", "temp", "temp_c", "temperature_c"],
    "humidity": ["humidity", "rh", "relative_humidity"],
    "rainfall": ["rainfall", "rain", "precipitation", "precip"],
    "pressure": ["pressure", "atm_pressure", "sea_level_pressure", "slp"],
    "wind_speed": ["wind_speed", "windspeed", "wind speed", "ws"],
    "wind_direction": ["wind_direction", "winddirection", "wind direction", "wd"]
}


def find_column(df, key):
    """Find the actual column name in df matching a standard key."""
    candidates = COLUMN_CANDIDATES.get(key, [key])
    cols_lower = {c.lower().strip(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    for cand in candidates:
        for col_lower, original in cols_lower.items():
            if cand.lower() in col_lower:
                return original
    return None


# =========================================================
# DATA LOADING
# =========================================================
@st.cache_data(show_spinner=False)
def load_data():
    if not os.path.exists(DATA_FILE):
        return None, f"Data file not found: {DATA_FILE}. Please ensure it is placed in the project directory."

    try:
        df = pd.read_csv(DATA_FILE)
    except Exception as e:
        return None, f"Failed to read {DATA_FILE}: {e}"

    if df.empty:
        return None, f"{DATA_FILE} is empty."

    df.columns = [c.strip() for c in df.columns]

    # Resolve datetime column safely
    dt_col = find_column(df, "datetime")
    date_col = find_column(df, "date")
    time_col = find_column(df, "time")

    try:
        if dt_col is not None:
            df["Datetime"] = pd.to_datetime(df[dt_col], errors="coerce")
        elif date_col is not None and time_col is not None:
            df["Datetime"] = pd.to_datetime(
                df[date_col].astype(str) + " " + df[time_col].astype(str),
                errors="coerce"
            )
        elif date_col is not None:
            df["Datetime"] = pd.to_datetime(df[date_col], errors="coerce")
        else:
            df["Datetime"] = pd.date_range(
                end=datetime.now(), periods=len(df), freq="h"
            )
    except Exception:
        df["Datetime"] = pd.date_range(end=datetime.now(), periods=len(df), freq="h")

    # Remove timezone info to avoid merge/comparison problems
    try:
        if pd.api.types.is_datetime64tz_dtype(df["Datetime"]):
            df["Datetime"] = df["Datetime"].dt.tz_localize(None)
    except Exception:
        pass

    df = df.dropna(subset=["Datetime"]).sort_values("Datetime").reset_index(drop=True)

    # Standardize key columns (create standard aliases without deleting originals)
    pm25_col = find_column(df, "pm25")
    if pm25_col is not None:
        df["PM2.5"] = pd.to_numeric(df[pm25_col], errors="coerce")
    else:
        return None, "Could not detect a PM2.5 column in the dataset."

    for key, alias in [
        ("temperature", "Temperature"),
        ("humidity", "Humidity"),
        ("rainfall", "Rainfall"),
        ("pressure", "Pressure"),
        ("wind_speed", "WindSpeed"),
        ("wind_direction", "WindDirection"),
    ]:
        col = find_column(df, key)
        if col is not None:
            df[alias] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[alias] = np.nan

    # Safe missing value handling
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isna().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val if pd.notna(median_val) else 0)

    df["PM2.5"] = df["PM2.5"].clip(lower=0)

    return df, None


@st.cache_resource(show_spinner=False)
def load_models():
    models = {}
    errors = []
    for horizon, filename in MODEL_FILES.items():
        if not os.path.exists(filename):
            errors.append(f"Model file not found: {filename}")
            continue
        try:
            models[horizon] = joblib.load(filename)
        except Exception as e:
            errors.append(f"Failed to load {filename}: {e}")
    return models, errors


# =========================================================
# RISK CLASSIFICATION
# =========================================================
def classify_risk(pm25_value):
    if pm25_value is None or pd.isna(pm25_value):
        return "LOW"
    if pm25_value <= 60:
        return "LOW"
    elif pm25_value <= 120:
        return "MODERATE"
    elif pm25_value <= 250:
        return "HIGH"
    else:
        return "SEVERE"


def risk_badge_html(risk_level):
    info = RISK_LEVELS[risk_level]
    return f"""<span class="badge" style="background:{info['bg']}; color:{info['color']}; border:1px solid {info['color']}55;">{risk_level}</span>"""


# =========================================================
# FEATURE ALIGNMENT FOR MODEL PREDICTION
# =========================================================
def build_feature_vector(model, df, overrides=None):
    """
    Build a single-row feature dataframe matching the model's expected
    input features. Uses the most recent data row as the baseline and
    applies any overrides (used by the Scenario Simulator).
    """
    overrides = overrides or {}
    latest = df.iloc[-1]

    alias_map = {
        "temperature": "Temperature",
        "temp": "Temperature",
        "humidity": "Humidity",
        "rh": "Humidity",
        "rainfall": "Rainfall",
        "rain": "Rainfall",
        "pressure": "Pressure",
        "wind_speed": "WindSpeed",
        "windspeed": "WindSpeed",
        "wind_direction": "WindDirection",
        "winddirection": "WindDirection",
        "pm2.5": "PM2.5",
        "pm25": "PM2.5"
    }

    if hasattr(model, "feature_names_in_"):
        feature_names = list(model.feature_names_in_)
    else:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        feature_names = [c for c in numeric_cols if c != "PM2.5"]

    row_data = {}
    for feat in feature_names:
        feat_lower = feat.lower().strip()

        value = None
        if feat in overrides:
            value = overrides[feat]
        elif feat_lower in overrides:
            value = overrides[feat_lower]
        elif feat_lower in alias_map and alias_map[feat_lower] in overrides:
            value = overrides[alias_map[feat_lower]]
        elif feat in df.columns:
            value = latest[feat]
        elif feat_lower in alias_map and alias_map[feat_lower] in df.columns:
            value = latest[alias_map[feat_lower]]
        else:
            matched_col = None
            for col in df.columns:
                if col.lower().strip() == feat_lower:
                    matched_col = col
                    break
            if matched_col is not None:
                value = latest[matched_col]
            else:
                if feat in df.select_dtypes(include=[np.number]).columns:
                    value = df[feat].mean()
                else:
                    value = 0

        if value is None or (isinstance(value, float) and pd.isna(value)):
            value = 0

        row_data[feat] = value

    feature_df = pd.DataFrame([row_data], columns=feature_names)
    return feature_df


def safe_predict(model, feature_df):
    try:
        pred = model.predict(feature_df)
        return float(np.ravel(pred)[0]), None
    except Exception as e:
        return None, str(e)


# =========================================================
# LOAD DATA & MODELS
# =========================================================
df, data_error = load_data()
models, model_errors = load_models()

if data_error:
    st.error(data_error)
    st.stop()

if model_errors:
    for err in model_errors:
        st.warning(err)

latest_row = df.iloc[-1]
current_pm25 = float(latest_row["PM2.5"])
current_temp = float(latest_row["Temperature"]) if pd.notna(latest_row["Temperature"]) else None
current_humidity = float(latest_row["Humidity"]) if pd.notna(latest_row["Humidity"]) else None
current_risk = classify_risk(current_pm25)

# =========================================================
# GENERATE FORECASTS (used across multiple pages)
# =========================================================
def generate_all_forecasts():
    results = {}
    for horizon in ["24h", "48h", "72h"]:
        model = models.get(horizon)
        if model is None:
            results[horizon] = {"value": None, "risk": None, "error": "Model not loaded"}
            continue
        feature_df = build_feature_vector(model, df)
        pred, err = safe_predict(model, feature_df)
        if err:
            results[horizon] = {"value": None, "risk": None, "error": err}
        else:
            pred = max(0, pred)
            results[horizon] = {"value": pred, "risk": classify_risk(pred), "error": None}
    return results


forecasts = generate_all_forecasts()

HORIZON_HOURS = {"24h": 24, "48h": 48, "72h": 72}

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
with st.sidebar:
    st.markdown("### AQI INTELLIGENCE")
    st.markdown(
        "<div style='color:#8b95a1; font-size:12px; margin-bottom:20px;'>DELHI NCR CONTROL CENTRE</div>",
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Forecast Centre",
            "Early Warning",
            "Weather Intelligence",
            "Scenario Simulator",
            "Analytics",
            "Delhi NCR View",
            "About Project"
        ],
        label_visibility="collapsed"
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style='font-size:12px; color:#8b95a1; line-height:1.8;'>
        SYSTEM STATUS: <span style='color:#2ecc71;'>ONLINE</span><br>
        MODELS LOADED: {len(models)}/3<br>
        RECORDS: {len(df):,}<br>
        LAST UPDATE: {latest_row['Datetime'].strftime('%d %b, %H:%M')}
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# SHARED HEADER
# =========================================================
def render_header(title, subtitle):
    st.markdown(f"""
    <div class="platform-header">
        <h1>{title}</h1>
        <div class="subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def kpi_card(label, value, unit="", delta=None):
    delta_html = f"<div class='kpi-delta'>{delta}</div>" if delta else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}<span class="kpi-unit">{unit}</span></div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def status_banner(risk_level, custom_message=None):
    info = RISK_LEVELS[risk_level]
    message = custom_message if custom_message else info["message"]
    st.markdown(f"""
    <div class="status-banner" style="border-color:{info['color']}55; background:{info['bg']};">
        <div class="status-dot" style="background:{info['color']};"></div>
        <div>
            <div class="status-text-title" style="color:{info['color']};">{risk_level} RISK LEVEL</div>
            <div class="status-text-body">{message}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# PAGE: DASHBOARD
# =========================================================
if page == "Dashboard":
    render_header("Delhi NCR Air Quality Intelligence System", "Real-Time Environmental Monitoring & Predictive Analytics")

    status_banner(current_risk)

    st.markdown("<div class='section-title'>CURRENT ENVIRONMENTAL SNAPSHOT</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Current PM2.5", f"{current_pm25:.1f}", "µg/m³")
    with c2:
        kpi_card("Risk Level", current_risk, "")
    with c3:
        kpi_card("Temperature", f"{current_temp:.1f}" if current_temp is not None else "N/A", "°C")
    with c4:
        kpi_card("Humidity", f"{current_humidity:.1f}" if current_humidity is not None else "N/A", "%")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>PM2.5 FORECAST OVERVIEW</div>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    for col, horizon, label in zip([f1, f2, f3], ["24h", "48h", "72h"], ["24-HOUR FORECAST", "48-HOUR FORECAST", "72-HOUR FORECAST"]):
        with col:
            res = forecasts[horizon]
            if res["value"] is not None:
                risk = res["risk"]
                kpi_card(label, f"{res['value']:.1f}", "µg/m³", delta=risk_badge_html(risk))
            else:
                kpi_card(label, "N/A", "", delta=f"<span style='color:#e74c3c;'>{res['error']}</span>")

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("<div class='section-title'>HISTORICAL POLLUTION TREND</div>", unsafe_allow_html=True)
        recent_df = df.tail(500)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=recent_df["Datetime"], y=recent_df["PM2.5"],
            mode="lines", line=dict(color=ACCENT, width=2),
            fill="tozeroy", fillcolor="rgba(34, 211, 238, 0.08)",
            name="PM2.5"
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#121417",
            plot_bgcolor="#121417",
            font=dict(color="#cbd5e1", family="Times New Roman"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=340,
            xaxis=dict(gridcolor="#1f2226"),
            yaxis=dict(gridcolor="#1f2226", title="PM2.5 (µg/m³)")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("<div class='section-title'>FORECAST COMPARISON</div>", unsafe_allow_html=True)
        horizons_valid = [h for h in ["24h", "48h", "72h"] if forecasts[h]["value"] is not None]
        values_valid = [forecasts[h]["value"] for h in horizons_valid]
        colors_valid = [RISK_LEVELS[forecasts[h]["risk"]]["color"] for h in horizons_valid]

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=horizons_valid, y=values_valid,
            marker_color=colors_valid,
            text=[f"{v:.1f}" for v in values_valid],
            textposition="outside"
        ))
        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor="#121417",
            plot_bgcolor="#121417",
            font=dict(color="#cbd5e1", family="Times New Roman"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=340,
            yaxis=dict(gridcolor="#1f2226", title="PM2.5 (µg/m³)"),
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>EARLY WARNING STATUS</div>", unsafe_allow_html=True)
    warn_cols = st.columns(3)
    for col, horizon, label in zip(warn_cols, ["24h", "48h", "72h"], ["24H", "48H", "72H"]):
        with col:
            res = forecasts[horizon]
            if res["value"] is not None and res["risk"] in ["HIGH", "SEVERE"]:
                st.markdown(f"""
                <div class="panel" style="border-color:{RISK_LEVELS[res['risk']]['color']}55;">
                    <div style="font-weight:700; color:{RISK_LEVELS[res['risk']]['color']};">{label} WARNING ACTIVE</div>
                    <div style="font-size:13px; color:#a9b2bd; margin-top:6px;">Predicted PM2.5: {res['value']:.1f} µg/m³ — {res['risk']} risk expected.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="panel">
                    <div style="font-weight:700; color:#2ecc71;">{label} NORMAL</div>
                    <div style="font-size:13px; color:#a9b2bd; margin-top:6px;">No elevated risk expected in this horizon.</div>
                </div>
                """, unsafe_allow_html=True)


# =========================================================
# PAGE: FORECAST CENTRE
# =========================================================
elif page == "Forecast Centre":
    render_header("Forecast Centre", "Machine Learning Based PM2.5 Prediction — 24H / 48H / 72H")

    cols = st.columns(3)
    for col, horizon in zip(cols, ["24h", "48h", "72h"]):
        with col:
            res = forecasts[horizon]
            target_time = latest_row["Datetime"] + timedelta(hours=HORIZON_HOURS[horizon])
            if res["value"] is not None:
                st.markdown(f"""
                <div class="panel">
                    <div class="kpi-label">FORECAST HORIZON</div>
                    <div style="font-size:20px; font-weight:700; color:#f8fafc; margin-bottom:14px;">{horizon.upper()}</div>
                    <div class="kpi-label">PREDICTED PM2.5</div>
                    <div class="kpi-value">{res['value']:.1f}<span class="kpi-unit">µg/m³</span></div>
                    <div style="margin:12px 0;">{risk_badge_html(res['risk'])}</div>
                    <div class="kpi-label">TARGET TIME</div>
                    <div style="font-size:13.5px; color:#cbd5e1;">{target_time.strftime('%d %b %Y, %H:%M')}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="panel">
                    <div class="kpi-label">FORECAST HORIZON</div>
                    <div style="font-size:20px; font-weight:700; color:#f8fafc;">{horizon.upper()}</div>
                    <div style="color:#e74c3c; margin-top:14px; font-size:13px;">Unable to generate forecast: {res['error']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>FORECAST TRAJECTORY</div>", unsafe_allow_html=True)

    valid_horizons = [h for h in ["24h", "48h", "72h"] if forecasts[h]["value"] is not None]
    if valid_horizons:
        x_points = [latest_row["Datetime"]] + [latest_row["Datetime"] + timedelta(hours=HORIZON_HOURS[h]) for h in valid_horizons]
        y_points = [current_pm25] + [forecasts[h]["value"] for h in valid_horizons]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_points, y=y_points, mode="lines+markers",
            line=dict(color=ACCENT, width=3),
            marker=dict(size=10, color=[RISK_LEVELS[current_risk]["color"]] + [RISK_LEVELS[forecasts[h]["risk"]]["color"] for h in valid_horizons]),
            name="PM2.5 Trajectory"
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#121417",
            plot_bgcolor="#121417",
            font=dict(color="#cbd5e1"),
            margin=dict(l=10, r=10, t=20, b=10),
            height=380,
            xaxis=dict(gridcolor="#1f2226", title="Time"),
            yaxis=dict(gridcolor="#1f2226", title="PM2.5 (µg/m³)")
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>RECENT HISTORICAL CONTEXT</div>", unsafe_allow_html=True)
    recent = df.tail(200)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=recent["Datetime"], y=recent["PM2.5"], mode="lines",
                               line=dict(color="#8b95a1", width=1.5), name="Historical PM2.5"))
    fig3.update_layout(
        template="plotly_dark", paper_bgcolor="#121417", plot_bgcolor="#121417",
        font=dict(color="#cbd5e1"), margin=dict(l=10, r=10, t=20, b=10), height=300,
        xaxis=dict(gridcolor="#1f2226"), yaxis=dict(gridcolor="#1f2226", title="PM2.5 (µg/m³)")
    )
    st.plotly_chart(fig3, use_container_width=True)


# =========================================================
# PAGE: EARLY WARNING
# =========================================================
elif page == "Early Warning":
    render_header("Early Warning System", "Automated Risk Detection Across Forecast Horizons")

    status_banner(current_risk, custom_message=f"Current observed PM2.5 is {current_pm25:.1f} µg/m³.")

    st.markdown("<div class='section-title'>WARNING TIMELINE</div>", unsafe_allow_html=True)
    for horizon, label in zip(["24h", "48h", "72h"], ["24-HOUR HORIZON", "48-HOUR HORIZON", "72-HOUR HORIZON"]):
        res = forecasts[horizon]
        if res["value"] is None:
            st.markdown(f"""
            <div class="panel" style="margin-bottom:14px;">
                <div style="font-weight:700; color:#e74c3c;">{label} — DATA UNAVAILABLE</div>
                <div style="font-size:13px; color:#a9b2bd; margin-top:4px;">{res['error']}</div>
            </div>
            """, unsafe_allow_html=True)
            continue

        risk = res["risk"]
        info = RISK_LEVELS[risk]
        target_time = latest_row["Datetime"] + timedelta(hours=HORIZON_HOURS[horizon])
        st.markdown(f"""
        <div class="panel" style="margin-bottom:14px; border-color:{info['color']}55;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-weight:700; color:#f8fafc; font-size:15px;">{label}</div>
                    <div style="font-size:13px; color:#a9b2bd; margin-top:4px;">Target: {target_time.strftime('%d %b, %H:%M')} — Predicted PM2.5: {res['value']:.1f} µg/m³</div>
                </div>
                <div>{risk_badge_html(risk)}</div>
            </div>
            <div style="font-size:13.5px; color:#cbd5e1; margin-top:12px;">{info['message']}</div>
        </div>
        """, unsafe_allow_html=True)

    active_warnings = sum(1 for h in ["24h", "48h", "72h"] if forecasts[h]["value"] is not None and forecasts[h]["risk"] in ["HIGH", "SEVERE"])
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>SUMMARY</div>", unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    with s1:
        kpi_card("Active Warnings", str(active_warnings), "of 3")
    with s2:
        kpi_card("Current Status", current_risk, "")
    with s3:
        worst = max(
            [forecasts[h]["risk"] for h in ["24h", "48h", "72h"] if forecasts[h]["value"] is not None] + [current_risk],
            key=lambda r: ["LOW", "MODERATE", "HIGH", "SEVERE"].index(r)
        )
        kpi_card("Peak Risk Expected", worst, "")


# =========================================================
# PAGE: WEATHER INTELLIGENCE
# =========================================================
elif page == "Weather Intelligence":
    render_header("Weather Intelligence", "Relationship Between Meteorological Factors and PM2.5")

    weather_vars = {
        "Temperature": "°C",
        "Humidity": "%",
        "Rainfall": "mm",
        "Pressure": "hPa",
        "WindSpeed": "m/s",
        "WindDirection": "°"
    }

    available_vars = [v for v in weather_vars if df[v].notna().any() and df[v].nunique() > 1]

    if not available_vars:
        st.warning("No usable weather variables were detected in the dataset.")
    else:
        selected_var = st.selectbox("Select Weather Parameter", available_vars)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='section-title'>PM2.5 vs {selected_var.upper()}</div>", unsafe_allow_html=True)
            fig = px.scatter(
                df, x=selected_var, y="PM2.5",
                color="PM2.5", color_continuous_scale="Turbo",
                opacity=0.6
            )
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#121417", plot_bgcolor="#121417",
                font=dict(color="#cbd5e1"), margin=dict(l=10, r=10, t=10, b=10), height=380,
                xaxis=dict(gridcolor="#1f2226"), yaxis=dict(gridcolor="#1f2226")
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(f"<div class='section-title'>{selected_var.upper()} TREND OVER TIME</div>", unsafe_allow_html=True)
            recent = df.tail(300)
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=recent["Datetime"], y=recent[selected_var], mode="lines",
                                       line=dict(color=ACCENT, width=2)))
            fig2.update_layout(
                template="plotly_dark", paper_bgcolor="#121417", plot_bgcolor="#121417",
                font=dict(color="#cbd5e1"), margin=dict(l=10, r=10, t=10, b=10), height=380,
                xaxis=dict(gridcolor="#1f2226"), yaxis=dict(gridcolor="#1f2226")
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>CORRELATION MATRIX</div>", unsafe_allow_html=True)
        corr_cols = ["PM2.5"] + available_vars
        corr_matrix = df[corr_cols].corr()
        fig3 = px.imshow(
            corr_matrix, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1
        )
        fig3.update_layout(
            template="plotly_dark", paper_bgcolor="#121417", plot_bgcolor="#121417",
            font=dict(color="#cbd5e1"), margin=dict(l=10, r=10, t=10, b=10), height=420
        )
        st.plotly_chart(fig3, use_container_width=True)


# =========================================================
# PAGE: SCENARIO SIMULATOR
# =========================================================
elif page == "Scenario Simulator":
    render_header("Scenario Simulator", "Interactive What-If Analysis Using the 24-Hour Forecasting Model")

    model_24h = models.get("24h")
    if model_24h is None:
        st.error("The 24-hour model is not available. Scenario simulation requires model_24h.pkl.")
    else:
        st.markdown("<div class='section-title'>ADJUST ENVIRONMENTAL PARAMETERS</div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            sim_temp = st.slider(
                "Temperature (°C)",
                float(df["Temperature"].min()), float(df["Temperature"].max()),
                float(current_temp) if current_temp is not None else float(df["Temperature"].mean())
            )
            sim_humidity = st.slider(
                "Humidity (%)",
                float(df["Humidity"].min()), float(df["Humidity"].max()),
                float(current_humidity) if current_humidity is not None else float(df["Humidity"].mean())
            )
        with col2:
            sim_rainfall = st.slider(
                "Rainfall (mm)",
                float(df["Rainfall"].min()), float(df["Rainfall"].max()),
                float(latest_row["Rainfall"])
            )
            sim_pressure = st.slider(
                "Pressure (hPa)",
                float(df["Pressure"].min()), float(df["Pressure"].max()),
                float(latest_row["Pressure"])
            )
        with col3:
            sim_wind_speed = st.slider(
                "Wind Speed (m/s)",
                float(df["WindSpeed"].min()), float(df["WindSpeed"].max()),
                float(latest_row["WindSpeed"])
            )
            sim_wind_dir = st.slider(
                "Wind Direction (°)",
                float(df["WindDirection"].min()), float(df["WindDirection"].max()),
                float(latest_row["WindDirection"])
            )

        st.markdown("<br>", unsafe_allow_html=True)
        run_sim = st.button("▶ RUN SCENARIO SIMULATION", use_container_width=False)

        if run_sim:
            overrides = {
                "Temperature": sim_temp,
                "Humidity": sim_humidity,
                "Rainfall": sim_rainfall,
                "Pressure": sim_pressure,
                "WindSpeed": sim_wind_speed,
                "WindDirection": sim_wind_dir
            }

            baseline_features = build_feature_vector(model_24h, df)
            baseline_pred, base_err = safe_predict(model_24h, baseline_features)

            scenario_features = build_feature_vector(model_24h, df, overrides=overrides)
            scenario_pred, sim_err = safe_predict(model_24h, scenario_features)

            if base_err or sim_err:
                st.error(f"Simulation failed: {base_err or sim_err}")
            else:
                baseline_pred = max(0, baseline_pred)
                scenario_pred = max(0, scenario_pred)
                diff = scenario_pred - baseline_pred
                scenario_risk = classify_risk(scenario_pred)
                baseline_risk = classify_risk(baseline_pred)

                st.markdown("<div class='section-title'>SIMULATION RESULT</div>", unsafe_allow_html=True)
                r1, r2, r3 = st.columns(3)
                with r1:
                    kpi_card("Baseline Forecast (24H)", f"{baseline_pred:.1f}", "µg/m³", delta=risk_badge_html(baseline_risk))
                with r2:
                    kpi_card("Simulated Forecast (24H)", f"{scenario_pred:.1f}", "µg/m³", delta=risk_badge_html(scenario_risk))
                with r3:
                    direction = "increase" if diff > 0 else ("decrease" if diff < 0 else "no change")
                    color = "#e74c3c" if diff > 0 else ("#2ecc71" if diff < 0 else "#8b95a1")
                    kpi_card("Predicted Difference", f"{diff:+.1f}", "µg/m³", delta=f"<span style='color:{color};'>{direction}</span>")

                st.markdown("<br>", unsafe_allow_html=True)
                interpretation = (
                    f"Under the simulated environmental conditions, PM2.5 is projected to {direction} "
                    f"by {abs(diff):.1f} µg/m³ relative to the current baseline forecast, shifting the "
                    f"expected risk classification from {baseline_risk} to {scenario_risk}. "
                    f"This suggests that the adjusted meteorological parameters have a "
                    f"{'notable' if abs(diff) > 10 else 'moderate' if abs(diff) > 3 else 'minor'} "
                    f"influence on near-term air quality under current conditions."
                )
                st.markdown(f"""
                <div class="panel">
                    <div class="kpi-label">PROFESSIONAL INTERPRETATION</div>
                    <div style="font-size:14px; color:#cbd5e1; margin-top:8px; line-height:1.6;">{interpretation}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='section-title'>BASELINE VS SCENARIO COMPARISON</div>", unsafe_allow_html=True)
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=["Baseline Forecast", "Scenario Forecast"],
                    y=[baseline_pred, scenario_pred],
                    marker_color=[RISK_LEVELS[baseline_risk]["color"], RISK_LEVELS[scenario_risk]["color"]],
                    text=[f"{baseline_pred:.1f}", f"{scenario_pred:.1f}"],
                    textposition="outside"
                ))
                fig.update_layout(
                    template="plotly_dark", paper_bgcolor="#121417", plot_bgcolor="#121417",
                    font=dict(color="#cbd5e1"), margin=dict(l=10, r=10, t=20, b=10), height=380,
                    yaxis=dict(gridcolor="#1f2226", title="PM2.5 (µg/m³)"), showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Adjust the parameters above and click 'Run Scenario Simulation' to generate a prediction using the trained 24-hour model.")


# =========================================================
# PAGE: ANALYTICS
# =========================================================
elif page == "Analytics":
    render_header("Analytics", "Model Performance & Historical Data Insights")

    st.markdown("<div class='section-title'>MODEL PERFORMANCE (MEAN ABSOLUTE ERROR)</div>", unsafe_allow_html=True)
    mae_values = {"24h": 15.69, "48h": 15.71, "72h": 16.58}
    m1, m2, m3 = st.columns(3)
    for col, horizon in zip([m1, m2, m3], ["24h", "48h", "72h"]):
        with col:
            kpi_card(f"{horizon.upper()} MODEL MAE", f"{mae_values[horizon]:.2f}", "µg/m³")

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("<div class='section-title'>MAE COMPARISON</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(mae_values.keys()), y=list(mae_values.values()),
            marker_color=ACCENT,
            text=[f"{v:.2f}" for v in mae_values.values()],
            textposition="outside"
        ))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#121417", plot_bgcolor="#121417",
            font=dict(color="#cbd5e1"), margin=dict(l=10, r=10, t=20, b=10), height=360,
            yaxis=dict(gridcolor="#1f2226", title="MAE (µg/m³)"), showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("<div class='section-title'>HISTORICAL PM2.5 DISTRIBUTION</div>", unsafe_allow_html=True)
        fig2 = px.histogram(df, x="PM2.5", nbins=40, color_discrete_sequence=[ACCENT])
        fig2.update_layout(
            template="plotly_dark", paper_bgcolor="#121417", plot_bgcolor="#121417",
            font=dict(color="#cbd5e1"), margin=dict(l=10, r=10, t=20, b=10), height=360,
            xaxis=dict(gridcolor="#1f2226"), yaxis=dict(gridcolor="#1f2226")
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>DATASET SUMMARY STATISTICS</div>", unsafe_allow_html=True)
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        kpi_card("Average PM2.5", f"{df['PM2.5'].mean():.1f}", "µg/m³")
    with d2:
        kpi_card("Maximum PM2.5", f"{df['PM2.5'].max():.1f}", "µg/m³")
    with d3:
        kpi_card("Minimum PM2.5", f"{df['PM2.5'].min():.1f}", "µg/m³")
    with d4:
        kpi_card("Total Measurements", f"{len(df):,}", "")


# =========================================================
# PAGE: DELHI NCR VIEW
# =========================================================
elif page == "Delhi NCR View":
    render_header("Delhi NCR Geographic Intelligence", "Prototype Coverage View")

    st.markdown("""
    <div class="panel" style="margin-bottom:20px; border-color:#f1c40f55;">
        <div style="color:#f1c40f; font-weight:700; font-size:13.5px;">PROTOTYPE NOTICE</div>
        <div style="font-size:13px; color:#a9b2bd; margin-top:6px;">
        This is a prototype geographic coverage view illustrating the NCR region monitored by this system.
        It does not represent real-time sensor readings for every individual location — current PM2.5
        and forecast values are derived from the primary monitored dataset.
        </div>
    </div>
    """, unsafe_allow_html=True)

    map_df = pd.DataFrame([
        {
            "City": city,
            "lat": coords["lat"],
            "lon": coords["lon"],
            "PM2.5": current_pm25,
            "Risk": current_risk
        }
        for city, coords in NCR_LOCATIONS.items()
    ])

    fig = px.scatter_mapbox(
        map_df, lat="lat", lon="lon", hover_name="City",
        hover_data={"PM2.5": True, "Risk": True, "lat": False, "lon": False},
        color="PM2.5", color_continuous_scale="Turbo",
        size=[20] * len(map_df), size_max=22, zoom=8.3
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        paper_bgcolor="#121417",
        font=dict(color="#cbd5e1"),
        margin=dict(l=0, r=0, t=0, b=0),
        height=520
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>REGIONAL COVERAGE SUMMARY</div>", unsafe_allow_html=True)
    cols = st.columns(len(NCR_LOCATIONS))
    for col, (city, _) in zip(cols, NCR_LOCATIONS.items()):
        with col:
            st.markdown(f"""
            <div class="panel">
                <div class="kpi-label">{city.upper()}</div>
                <div style="font-size:13px; color:#a9b2bd; margin-top:6px;">Reference PM2.5</div>
                <div class="kpi-value" style="font-size:22px;">{current_pm25:.1f}</div>
                <div style="margin-top:8px;">{risk_badge_html(current_risk)}</div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# PAGE: ABOUT PROJECT
# =========================================================
elif page == "About Project":
    render_header("About the Project", "Delhi NCR Air Quality Intelligence and Pollution Forecasting System")

    st.markdown("""
    <div class="panel">
        <p style="font-size:14.5px; line-height:1.8; color:#cbd5e1;">
        The Delhi NCR Air Quality Intelligence and Pollution Forecasting System is an environmental
        decision-support platform designed to move beyond traditional pollution monitoring. Rather than
        simply reporting current air quality, this system integrates historical pollution and weather
        data with machine learning models to deliver forward-looking, actionable intelligence.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>CORE CAPABILITIES</div>", unsafe_allow_html=True)

    capabilities = [
        ("Predictive Forecasting", "Machine learning models trained on historical pollution and weather data to anticipate future PM2.5 levels."),
        ("24-Hour Forecasting", "Short-term PM2.5 prediction to support immediate operational and public health decisions."),
        ("48-Hour Forecasting", "Medium-term outlook enabling proactive planning for institutions and municipal bodies."),
        ("72-Hour Forecasting", "Extended horizon forecasting to anticipate multi-day pollution episodes."),
        ("Weather Intelligence", "Analysis of the relationship between meteorological variables and pollution behaviour."),
        ("Early Warning", "Automated risk detection across all forecast horizons to flag elevated pollution episodes."),
        ("Risk Classification", "A structured LOW / MODERATE / HIGH / SEVERE framework applied consistently across the platform."),
        ("Scenario Simulation", "Interactive what-if analysis using the trained models to evaluate the impact of changing environmental conditions."),
        ("Environmental Decision Support", "Consolidated intelligence intended to support preventive and responsive environmental action.")
    ]

    for title, desc in capabilities:
        st.markdown(f"""
        <div class="panel" style="margin-bottom:12px;">
            <div style="font-weight:700; color:#f8fafc; font-size:14.5px;">{title}</div>
            <div style="font-size:13.5px; color:#a9b2bd; margin-top:6px; line-height:1.6;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>TECHNOLOGY STACK</div>", unsafe_allow_html=True)
    tech_cols = st.columns(5)
    for col, tech in zip(tech_cols, ["Python", "Streamlit", "Pandas / NumPy", "Plotly", "Joblib / Scikit-learn"]):
        with col:
            st.markdown(f"""
            <div class="panel" style="text-align:center;">
                <div style="font-size:13.5px; font-weight:600; color:#22d3ee;">{tech}</div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div class="footer-note">
    DELHI NCR AIR QUALITY INTELLIGENCE SYSTEM &nbsp;•&nbsp; PREDICTIVE ENVIRONMENTAL MONITORING PLATFORM
</div>
# >>>>>>> f7f87c7d9431ba76418b9176ec3543b83ba303cf
""", unsafe_allow_html=True)