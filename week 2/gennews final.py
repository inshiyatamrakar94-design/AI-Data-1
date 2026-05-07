
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta, timezone

# --- SIMULATED DATA REPLICATING GNEWS API STRUCTURE ---
# This mimics the structure of the API response for the 5 requested countries.
raw_api_data = [
    {"country": "Nepal", "title": "Everest climbers reach summit in record time today", "publishedAt": "2024-05-20T10:00:00Z", "source": "Kathmandu Post"},
    {"country": "Nepal", "title": "New hydropower plant opens in western district", "publishedAt": "2024-05-20T14:30:00Z", "source": "Nepal News"},
    {"country": "India", "title": "Tech stocks rally as market opens in Mumbai", "publishedAt": "2024-05-20T09:00:00Z", "source": "The Hindu"},
    {"country": "India", "title": "Monsoon rains expected to hit Kerala coast early", "publishedAt": "2024-05-20T11:00:00Z", "source": "Times of India"},
    {"country": "India", "title": "World Cup: India vs Australia final highlights", "publishedAt": "2024-05-20T15:00:00Z", "source": "Sports Daily"},
    {"country": "USA", "title": "SpaceX launches latest satellite batch from Cape Canaveral", "publishedAt": "2024-05-20T08:00:00Z", "source": "Reuters"},
    {"country": "USA", "title": "World Cup: India vs Australia final highlights", "publishedAt": "2024-05-20T15:10:00Z", "source": "CNN"}, # Global headline
    {"country": "UK", "title": "London weather: Unusually warm weekend ahead for residents", "publishedAt": "2024-05-20T07:00:00Z", "source": "BBC News"},
    {"country": "UK", "title": "UK economy shows signs of steady growth in Q1", "publishedAt": "2024-05-19T22:00:00Z", "source": "The Guardian"}, # Older than 6 hrs
    {"country": "Australia", "title": "Great Barrier Reef health improves according to latest study", "publishedAt": "2024-05-20T12:00:00Z", "source": "ABC News"},
    {"country": "Australia", "title": "World Cup: India vs Australia final highlights", "publishedAt": "2024-05-20T15:05:00Z", "source": "Sydney Morning Herald"} # Global headline
]

# --- PIPELINE START ---

# 1. Processing and Saving to CSV
# Rules: No spaces in cols, lowercase, handle missing, filter > 6 words, no duplicates.
processed_data = []
for item in raw_api_data:
    processed_data.append({
        "country": item.get("country", "N/A"),
        "title": item.get("title", "N/A"),
        "published_at": item.get("publishedAt", "N/A"),
        "source": item.get("source", "N/A")
    })

df = pd.DataFrame(processed_data)

# Filter: Titles longer than 6 words
df['word_count'] = df['title'].str.split().str.len()
df_filtered = df[df['word_count'] > 6].drop(columns=['word_count'])

# Save to CSV (Simulating idempotency by dropping duplicates before saving)
# This prevents duplicates if the script runs twice.
CSV_NAME = 'headlines.csv'
df_filtered.drop_duplicates(subset=['title', 'country']).to_csv(CSV_NAME, index=False)

# --- ANALYSIS (Reading from CSV) ---
data = pd.read_csv(CSV_NAME)

# Q1: Country with most headlines
most_headlines = data['country'].value_counts().idxmax()

# Q2: Average words per headline title per country
data['words'] = data['title'].str.split().str.len()
avg_words = data.groupby('country')['words'].mean()

# Q3: Headlines in more than one country
dupes = data[data.duplicated(subset=['title'], keep=False)]
shared_headlines = dupes['title'].unique()

# Q4: Top source
top_source = data['source'].value_counts().idxmax()

# Q5: Time percentage (Ref time: 2024-05-20T16:00:00Z for this simulation)
ref_time = datetime(2024, 5, 20, 16, 0, 0, tzinfo=timezone.utc)
data['dt'] = pd.to_datetime(data['published_at'])
six_hours_ago = ref_time - timedelta(hours=6)
new_count = len(data[data['dt'] >= six_hours_ago])
old_count = len(data[data['dt'] < six_hours_ago])
total = len(data)
pct_new = (new_count / total) * 100

# Q8: Longest/Shortest avg country
longest_avg = avg_words.idxmax()
shortest_avg = avg_words.idxmin()

print(f"Most Headlines: {most_headlines}")
print(f"Avg Words: \n{avg_words}")
print(f"Shared Headlines: {shared_headlines}")
print(f"Top Source: {top_source}")
print(f"Percentage Last 6h: {pct_new}%")
print(f"Count > 6 words: {total}")
print(f"Longest Avg Country: {longest_avg}")
print(f"Shortest Avg Country: {shortest_avg}")