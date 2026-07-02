import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), "bot_database.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    # Users Table
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
    # Keys Table
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
    # Payments Table
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

# कीज़ ऐड करने के लिए
def save_key(game_name, key_code, plan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO keys (game_name, key_code, plan, is_used) VALUES (?, ?, ?, 0)", (game_name, key_code, plan))
    conn.commit()
    conn.close()

# स्टॉक चेक करने के लिए
def get_stock(game_name, plan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM keys WHERE game_name = ? AND plan = ? AND is_used = 0", (game_name, plan))
    count = cursor.fetchone()[0]
    conn.close()
    return count

# पेमेंट स्टेटस अपडेट करने के लिए
def update_payment_status(payment_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE payments SET status = ? WHERE id = ?", (status, payment_id))
    conn.commit()
    conn.close()

# यूजर की खरीदी हुई कीज़ देखने के लिए
def get_user_keys(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key_code FROM keys WHERE user_id = ?", (user_id,))
    keys = [row[0] for row in cursor.fetchall()]
    conn.close()
    return keys

# टोटल यूज़र्स गिनने के लिए
def get_total_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count
