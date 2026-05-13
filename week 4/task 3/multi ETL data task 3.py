import pandas as pd
import requests
from sqlalchemy import create_engine

# --- 1. EXTRACT ---
# Fixed the URLs and variable names to be consistent
users_data = requests.get('https://jsonplaceholder.typicode.com/users').json()
posts_data = requests.get('https://jsonplaceholder.typicode.com/posts').json()
todos_data = requests.get('https://jsonplaceholder.typicode.com/todos').json()

# --- 2. TRANSFORM (Users) ---
df_users = pd.json_normalize(users_data)
df_users = df_users[['id', 'name', 'email', 'address.city']]
df_users.columns = ['id', 'name', 'email', 'city']

# --- 3. TRANSFORM (Posts) ---
df_posts = pd.DataFrame(posts_data)[['userId', 'title']].rename(columns={'userId': 'id'})

# --- 4. MERGE & COUNT ---
post_counts = df_posts.groupby('id').size().reset_index(name='post_count')
df_users = df_users.merge(post_counts, on='id', how='left').fillna(0)

# --- 5. CLEAN ---
df_users['email'] = df_users['email'].str.lower()
df_users['name'] = df_users['name'].str.strip()
df_users['city'] = df_users['city'].str.strip()
df_users = df_users.dropna()

# --- 6. BONUS (Completion Rate) ---
df_todos = pd.DataFrame(todos_data)
# Calculate mean of 'completed' (True=1, False=0) to get the rate
completion = df_todos.groupby('userId')['completed'].mean().reset_index()
completion.columns = ['id', 'completion_rate']
df_users = df_users.merge(completion, on='id', how='left')

# --- 7. LOAD ---
df_users.to_csv('merged_data.csv', index=False)
engine = create_engine('sqlite:///merged.db')
df_users.to_sql('users', engine, if_exists='replace', index=False)

print("🏆 Top 3 Active Users:")
print(df_users.nlargest(3, 'post_count'))
