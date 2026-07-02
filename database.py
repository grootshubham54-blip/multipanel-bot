import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), "bot_database.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_name TEXT,
        key_code TEXT,
        plan TEXT,
        is_used INTEGER DEFAULT 0,
        user_id INTEGER DEFAULT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        game_name TEXT,
        plan TEXT,
        amount TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)
    conn.commit()
    conn.close()

def add_user(user_id, username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def save_key(game_name, key_code, plan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO keys (game_name, key_code, plan, is_used) VALUES (?, ?, ?, 0)", (game_name, key_code, plan))
    conn.commit()
    conn.close()

def approve_and_assign_key(user_id, game_name, plan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, key_code FROM keys WHERE game_name = ? AND plan = ? AND is_used = 0 LIMIT 1", (game_name, plan))
    row = cursor.fetchone()
    if row:
        key_id, key_code = row
        cursor.execute("UPDATE keys SET is_used = 1, user_id = ? WHERE id = ?", (user_id, key_id))
        conn.commit()
        conn.close()
        return key_code
    conn.close()
    return None

def get_stock_count(game_name, plan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM keys WHERE game_name = ? AND plan = ? AND is_used = 0", (game_name, plan))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_total_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_user_keys(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT game_name, plan, key_code FROM keys WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
