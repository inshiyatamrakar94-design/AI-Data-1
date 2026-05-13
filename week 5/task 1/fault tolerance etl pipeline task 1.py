import json
import logging
import sqlite3
import time
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# ==========================================
# 1. EXTRACT: Resilient Data Fetching
# ==========================================
def create_requests_session() -> requests.Session:
    """Creates a requests session with automated retry logic."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False,
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


def fetch_api_data(url: str, timeout: int = 10) -> List[Dict]:
    """Fetches data from an API endpoint with error handling."""
    session = create_requests_session()
    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP Error for {url}: {e}")
        return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Connection Error for {url}: {e}")
        return []


def generate_mock_csv() -> None:
    """Generates a messy local CSV file for simulation."""
    data = """email,name,signup_date,score
Sincere@april.biz,Leanne Graham-Updated,2025-01-01,95
Shanna@melissa.tv, Ervin Howell ,2025-02-02,150
messy_user@test.com,John Doe,2026/05/01,
Sincere@april.biz,Leanne Graham-Duplicate,2025-01-01,95
 Nathan@yesenia.net,Nathan Howell,2025-03-03,-50
"""
    with open("messy_data.csv", "w") as f:
        f.write(data)
    logging.info("Generated messy_data.csv")


# ==========================================
# 2. TRANSFORM: Normalize, Merge, & Clean
# ==========================================
def transform_data(
    api_users: List[Dict], csv_path: str
) -> Optional[DataFrame]:
    """Normalizes, merges, and cleans data from both sources."""
    if not api_users:
        logging.error("No API data available. Aborting transformation.")
        return None

    # Step A: Normalize JSON
    df_api = pd.json_normalize(api_users)
    df_api = df_api[["email", "name"]].rename(columns={"name": "name_api"})

    # Step B: Load CSV
    try:
        df_csv = pd.read_csv(csv_path)
    except FileNotFoundError:
        logging.error(f"CSV file not found at {csv_path}")
        return None

    # Step C: Pre-merge whitespace cleanup on keys
    df_api["email"] = df_api["email"].str.strip().str.lower()
    df_csv["email"] = df_csv["email"].str.strip().str.lower()

    # Step D: Merge and Conflict Resolution
    # Rule: API data is the "source of truth". If names differ, keep API name.
    df_merged = pd.merge(df_csv, df_api, on="email", how="left")
    df_merged["name"] = df_merged["name_api"].fillna(df_merged["name"])
    df_merged.drop(columns=["name_api"], inplace=True)

    # Step E: Apply 6 Cleaning Techniques
    # 1. Whitespace
    df_merged["name"] = df_merged["name"].astype(str).str.strip()

    # 2. Casing
    df_merged["name"] = df_merged["name"].str.title()

    # 3. Types
    df_merged["signup_date"] = pd.to_datetime(
        df_merged["signup_date"], errors="coerce"
    )

    # 4. Outliers (Winsorization/clipping for score field)
    if "score" in df_merged.columns:
        df_merged["score"] = pd.to_numeric(df_merged["score"], errors="coerce")
        df_merged["score"] = df_merged["score"].clip(lower=0, upper=100)

    # 5. Nulls handling
    df_merged["score"] = df_merged["score"].fillna(0)
    df_merged["signup_date"] = df_merged["signup_date"].fillna(
        pd.Timestamp.now()
    )

    # 6. Duplicates
    df_merged.drop_duplicates(subset=["email"], keep="first", inplace=True)

    return df_merged


# ==========================================
# 3. LOAD: SQLite (Idempotent) & CSV
# ==========================================
def load_data(df: pd.DataFrame, db_name: str, csv_output: str) -> None:
    """Loads dataframe to CSV and SQLite with duplicate prevention."""
    # Save to CSV
    df.to_csv(csv_output, index=False)
    logging.info(f"Saved cleaned data to CSV: {csv_output}")

    # Save to SQLite using Upsert logic via a staging table
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create target schema
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT,
            signup_date TEXT,
            score REAL
        )
    """
    )

    # Convert DataFrame dates to string for SQLite compatibility
    df_to_load = df.copy()
    df_to_load["signup_date"] = df_to_load["signup_date"].astype(str)

    # Write to a temporary staging table
    df_to_load.to_sql("staging_users", conn, if_exists="replace", index=False)

    # Idempotent upsert transaction
    cursor.execute(
        """
        INSERT INTO users (email, name, signup_date, score)
        SELECT email, name, signup_date, score FROM staging_users
        WHERE 1
        ON CONFLICT(email) DO UPDATE SET
            name=excluded.name,
            signup_date=excluded.signup_date,
            score=excluded.score;
    """
    )
    cursor.execute("DROP TABLE staging_users;")

    conn.commit()
    conn.close()
    logging.info("Saved data idempotently to SQLite database.")


# ==========================================
# Execution Pipeline
# ==========================================
if __name__ == "__main__":
    generate_mock_csv()

    # Step 1: Extract (Fetch BOTH endpoints using full URLs)
    logging.info("Fetching API Users...")
    api_users = fetch_api_data("https://jsonplaceholder.typicode.com/users")

    logging.info("Fetching API Posts...")
    api_posts = fetch_api_data("https://jsonplaceholder.typicode.com/posts")

    # Step 2: Transform
    logging.info("Transforming and cleaning data...")
    
    # Process users first
    cleaned_df = transform_data(api_users, "messy_data.csv")

    # Merge posts into the cleaned dataset (aggregating post counts per user)
    if cleaned_df is not None and api_posts:
        df_posts = pd.DataFrame(api_posts)
        
        # Count how many posts each user has based on their user ID mapping
        # JSONPlaceholder users have IDs 1 to 10. We map API emails to their IDs.
        api_df_raw = pd.json_normalize(api_users)
        if "id" in api_df_raw.columns and "email" in api_df_raw.columns:
            api_df_raw["email"] = api_df_raw["email"].str.strip().str.lower()
            id_to_email = dict(zip(api_df_raw["id"], api_df_raw["email"]))
            
            # Map post owner IDs to emails, then count posts
            df_posts["email"] = df_posts["userId"].map(id_to_email)
            post_counts = df_posts.groupby("email").size().reset_index(name="post_count")
            
            # Combine post counts into our main cleaned dataframe
            cleaned_df = pd.merge(cleaned_df, post_counts, on="email", how="left")
            cleaned_df["post_count"] = cleaned_df["post_count"].fillna(0).astype(int)

    # Step 3: Load
    if cleaned_df is not None:
        load_data(cleaned_df, "production.db", "cleaned_users.csv")
        print("\nFinal Unified Processed Data:")
        print(cleaned_df.to_string())
