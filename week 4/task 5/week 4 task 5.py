import sqlite3
import pandas as pd
import requests


def extract() -> dict:
    """Extracts weather data using your exact Open-Meteo URL string."""
    print("LOG: Starting Extraction phase...")

    # YOUR EXACT URL STRING:
    url = "https://api.open-meteo.com/v1/forecast?latitude=27.7172&longitude=85.324&daily=sunrise,sunset&hourly=temperature_2m,rain,showers&current=rain,showers,precipitation&timezone=auto"

    try:
        # We pass the URL directly without an extra params dictionary
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("LOG: Successfully extracted raw JSON payload using your custom URL.")
        return data
    except requests.exceptions.RequestException as e:
        print(f"ERROR: API extraction failed. Reason: {e}")
        return {}


def transform(raw_data: dict) -> pd.DataFrame:
    """Cleans weather data and computes custom fields from your requested parameters."""
    print("LOG: Starting Transformation phase...")
    if not raw_data or "hourly" not in raw_data:
        print("LOG: No valid hourly data available to transform.")
        return pd.DataFrame()

    # 1. Load the hourly forecast section into a Pandas DataFrame
    hourly_data = raw_data["hourly"]
    df = pd.DataFrame(hourly_data)

    # 2. Clean Nulls, Duplicates, and Format Types
    df.dropna(inplace=True)
    df.drop_duplicates(subset=["time"], keep="first", inplace=True)
    df["time"] = pd.to_datetime(df["time"])
    df["temperature_2m"] = df["temperature_2m"].astype(float)
    df["rain"] = df["rain"].astype(float)
    df["showers"] = df["showers"].astype(float)

    # 3. TRANSFORM: Add 2 calculated/enriched columns based on your URL parameters
    # Column 1: Total combined wet precipitation (Rain + Showers)
    df["total_precipitation_hourly"] = df["rain"] + df["showers"]

    # Column 2: Boolean flag indicating if it is actively raining/showering
    df["is_raining"] = df["total_precipitation_hourly"] > 0.0

    print(
        f"LOG: Transformation complete. Processed {len(df)} entries into structural columns."
    )
    return df


def load(
    df: pd.DataFrame,
    db_name: str = "weather_data.db",
    csv_name: str = "clean_weather.csv",
):
    """Loads cleaned data into SQLite (handling duplicates) and exports to clean CSV."""
    print("LOG: Starting Load phase...")
    if df.empty:
        print("LOG: Empty dataframe. Skipping Load phase.")
        return

    # 1. Export to clean CSV file
    df.to_csv(csv_name, index=False)
    print(f"LOG: Exported clean dataset to file system destination: '{csv_name}'")

    # 2. Load to SQLite using df.to_sql()
    conn = sqlite3.connect(db_name)
    try:
        # Overwrites table on reruns to satisfy assignment's anti-duplication requirement
        df.to_sql("forecasts", conn, if_exists="replace", index=False)
        print(
            f"LOG: Saved {len(df)} structured records into SQLite table 'forecasts' inside '{db_name}'."
        )
    except Exception as e:
        print(f"ERROR: Database loading transaction aborted. Details: {e}")
    finally:
        conn.close()


# --- Execution Controller Script Block ---
if __name__ == "__main__":
    print("\n=== PIPELINE RUN #1 ===")
    weather_json = extract()
    transformed_df = transform(weather_json)
    load(transformed_df)
