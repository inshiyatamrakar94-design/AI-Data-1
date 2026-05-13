import requests
import pandas as pd
import sqlite3

# 1. EXTRACT
url = "https://jsonplaceholder.typicode.com/posts"
try:
    response = requests.get(url)
    response.raise_for_status() # Check for errors
    data = response.json()
except Exception as e:
    print(f"Error fetching data: {e}")
    data = []

# 2. LOAD INTO DATAFRAME
df = pd.DataFrame(data)
total_fetched = len(df)

# BONUS: Validate userId are integers
df['userId'] = pd.to_numeric(df['userId'], errors='coerce')

# 3. TRANSFORM: Keep specific columns
df = df[['userId', 'id', 'title', 'body']]

# 4. Add word_count column
df['word_count'] = df['title'].str.split().str.len()

# 5. Filter: word_count >= 4
df = df[df['word_count'] >= 4]
posts_after_filter = len(df)

# 6. Standardise: Title Case and Strip Body
df['title'] = df['title'].str.title()
df['body'] = df['body'].str.strip()

# 7. LOAD: Save to CSV and SQLite
df.to_csv('clean_posts.csv', index=False)

conn = sqlite3.connect('posts.db')
df.to_sql('posts', conn, if_exists='replace', index=False)
conn.close()

# 8. PRINT STATS
print(f"Total posts fetched: {total_fetched}")
print(f"Posts after filtering: {posts_after_filter}")
print("\nTop 3 users by post count:")
print(df['userId'].value_counts().head(3))
