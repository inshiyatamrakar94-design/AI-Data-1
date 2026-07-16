import mysql.connector
import os
import bcrypt
from dotenv import load_dotenv

# Load database credentials from the hidden .env file
load_dotenv()

def get_db_connection():
    """Establishes a connection to the local MySQL server."""
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
    except mysql.connector.Error as err:
        print(f"Database connection failed: {err}")
        return None

def register_user(username, email, password):
    """Encrypts a password and saves a new user into the database."""
    conn = get_db_connection()
    if not conn:
        return "Database connection error."
    
    cursor = conn.cursor()
    
    # Securely hash the plain text password before saving
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        sql = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
        cursor.execute(sql, (username, email, hashed_password))
        conn.commit()
        return "Success"
    except mysql.connector.Error as err:
        if err.errno == 1062:  # Duplicate entry error code
            return "Username or email already exists."
        return f"Registration failed: {err}"
    finally:
        cursor.close()
        conn.close()

def authenticate_user(username, password):
    """Checks credentials against stored records for login validation."""
    conn = get_db_connection()
    if not conn:
        return False
        
    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return user  # Credentials match, return user record
        return False
    finally:
        cursor.close()
        conn.close()
