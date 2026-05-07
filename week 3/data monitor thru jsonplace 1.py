import mysql.connector as mysql
import requests
from datetime import datetime

# --- 1. CONNECTION CONFIG ---
# Replace 'yourpassword' with your actual MySQL password
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Admin2026!" 
}

def setup_database():
    """Creates the database and tables if they don't exist."""
    try:
        conn = mysql.connect(**db_config)
        cursor = conn.cursor()
        
        # Create Database
        cursor.execute("CREATE DATABASE IF NOT EXISTS monitor_db")
        cursor.execute("USE monitor_db")
        
        # Create Table for Posts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INT PRIMARY KEY,
                userId INT,
                title TEXT,
                body TEXT
            )
        """)
        
        # Create Table for Change Logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS change_log (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                post_id INT,
                change_type VARCHAR(20),
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        return conn, cursor
    except mysql.Error as e:
        print(f"❌ Database Setup Error: {e}")
        return None, None

def monitor_api():
    conn, cursor = setup_database()
    if not conn:
        return

    # --- 2. FETCH API DATA ---
    try:
        print("🌐 Fetching data from API...")
        response = requests.get("https://jsonplaceholder.typicode.com/posts")
        api_posts = response.json()
    except Exception as e:
        print(f"❌ API Error: {e}")
        return

    # --- 3. COMPARE AND DETECT CHANGES ---
    try:
        for post in api_posts:
            # Check if we already have this post
            cursor.execute("SELECT title, body FROM posts WHERE id = %s", (post['id'],))
            row = cursor.fetchone()

            if row is None:
                # Case: NEW Post (doesn't exist in DB yet)
                cursor.execute("INSERT INTO posts (id, userId, title, body) VALUES (%s, %s, %s, %s)",
                               (post['id'], post['userId'], post['title'], post['body']))
                cursor.execute("INSERT INTO change_log (post_id, change_type) VALUES (%s, 'NEW')", (post['id'],))
            
            else:
                # Case: Check if existing post was MODIFIED
                # row[0] is title, row[1] is body
                if row[0] != post['title'] or row[1] != post['body']:
                    cursor.execute("UPDATE posts SET title=%s, body=%s WHERE id=%s", 
                                   (post['title'], post['body'], post['id']))
                    cursor.execute("INSERT INTO change_log (post_id, change_type) VALUES (%s, 'MODIFIED')", (post['id'],))
        
        conn.commit()
        print("✅ Sync complete. Generating reports...")

        # --- 4. REQUIRED REPORTS ---

        # Report A: Post count per user
        print("\n📊 --- POST COUNT PER USER ---")
        cursor.execute("SELECT userId, COUNT(*) FROM posts GROUP BY userId")
        for u_id, count in cursor.fetchall():
            print(f"User {u_id}: {count} posts")

        # Report B: All change log entries from the latest run
        # (Using a timestamp window or just showing recent entries)
        print("\n📜 --- LATEST CHANGE LOG ENTRIES ---")
        cursor.execute("SELECT * FROM change_log ORDER BY changed_at DESC LIMIT 10")
        logs = cursor.fetchall()
        for log in logs:
            print(f"ID: {log[1]} | Action: {log[2]} | Time: {log[3]}")

        # Report C: Which user triggered the most change events
        print("\n🏆 --- USER WITH MOST CHANGE EVENTS ---")
        cursor.execute("""
            SELECT p.userId, COUNT(*) as change_count 
            FROM change_log c 
            JOIN posts p ON c.post_id = p.id 
            GROUP BY p.userId 
            ORDER BY change_count DESC LIMIT 1
        """)
        top_user = cursor.fetchone()
        if top_user:
            print(f"User {top_user[0]} triggered {top_user[1]} total change events.")

    except mysql.Error as e:
        print(f"❌ DB Operation Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    monitor_api()
