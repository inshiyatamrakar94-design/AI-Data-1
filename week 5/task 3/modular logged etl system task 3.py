import logging
import requests
import pandas as pd
from sqlalchemy import create_engine

# Configure logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract() -> list:
    """Extracts raw data from a public API with full error handling."""
    url = "https://jsonplaceholder.typicode.com/todos"
    logging.info("Starting extraction phase...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raises HTTPError for bad status codes (4xx, 5xx)
        
        raw_data = response.json()
        logging.info(f"Successfully extracted {len(raw_data)} raw records from API.")
        return raw_data
        
    except requests.exceptions.Timeout:
        logging.error("Extraction failed: The request timed out.")
        raise
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"Extraction failed: HTTP error occurred: {http_err}")
        raise
    except requests.exceptions.RequestException as err:
        logging.error(f"Extraction failed: An error occurred: {err}")
        raise

def clean(raw_data: list) -> pd.DataFrame:
    """Cleans raw data, handles missing values, and drops duplicates."""
    logging.info(f"Starting cleaning phase. Received {len(raw_data)} rows.")
    
    df = pd.DataFrame(raw_data)
    
    # Drop exact duplicates if any exist
    df = df.drop_duplicates()
    
    # Ensure critical columns have no missing values
    df = df.dropna(subset=['id', 'userId', 'title'])
    
    logging.info(f"Cleaning complete. Outputting {len(df)} rows.")
    return df

def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Engineers 3 new calculated columns and prints an aggregated summary table."""
    logging.info(f"Starting transformation phase. Received {len(df)} rows.")
    
    # 1. Calculated Column: Count words in the title
    df['title_word_count'] = df['title'].apply(lambda x: len(str(x).split()))
    
    # 2. Calculated Column: Categorize character length of title
    df['title_length_category'] = pd.cut(df['title'].str.len(), 
                                         bins=[0, 20, 50, 200], 
                                         labels=['Short', 'Medium', 'Long'])
    
    # 3. Calculated Column: Priority level based on completion status and ID
    df['priority_score'] = df.apply(lambda row: 10 if not row['completed'] and row['id'] % 2 == 0 else 5, axis=1)
    
    logging.info("Transformation metrics calculated successfully.")
    
    # Produce and print the summary table using groupby()
    summary_table = df.groupby('completed')['title_word_count'].agg(['mean', 'min', 'max'])
    print("\n--- DATA SUMMARY TABLE (Grouped by Completion Status) ---")
    print(summary_table)
    print("---------------------------------------------------------\n")
    
    logging.info(f"Transformation complete. Outputting {len(df)} rows.")
    return df

def load(df: pd.DataFrame):
    """Loads dataframe into CSV and MySQL database. Ensures idempotency."""
    logging.info(f"Starting load phase. Received {len(df)} rows.")
    
    # 1. Save to CSV (index=False)
    csv_filename = "todo_etl_output.csv"
    df.to_csv(csv_filename, index=False)
    logging.info(f"Data successfully saved to CSV: {csv_filename}")
    
    # 2. Save to MySQL with Idempotency (Using if_exists='replace' to avoid duplication)
    # Replace credentials with your actual local MySQL settings
    db_user = "root"
    db_password = "Admin2026!"
    db_host = "localhost"
    db_port = "3306"
    db_name = "sys"
    
    try:
        engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
        
        # if_exists='replace' ensures that running the pipeline twice overwrites 
        # previous data rather than duplicating rows.
        df.to_sql(name='enriched_todos', con=engine, if_exists='replace', index=False)
        logging.info("Data successfully loaded into MySQL table 'enriched_todos' with idempotency guaranteed.")
        
    except Exception as e:
        logging.error(f"Failed to load data into MySQL database: {e}")
        raise

if __name__ == "__main__":
    logging.info("--- Executing ETL Pipeline Run 1 ---")
    raw = extract()
    cleaned = clean(raw)
    transformed = transform(cleaned)
    load(transformed)
    
    logging.info("--- Executing ETL Pipeline Run 2 (Testing Idempotency) ---")
    raw_2 = extract()
    cleaned_2 = clean(raw_2)
    transformed_2 = transform(cleaned_2)
    load(transformed_2)
    
    logging.info("ETL Pipeline completed successfully without errors.")
