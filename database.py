import sqlite3
import os

# Railway पर फाइल पाथ का सही उपयोग करने के लिए
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

# नया फीचर: यूजर की खरीदी हुई कीज़ देखने के लिए
def get_user_keys(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key_code FROM keys WHERE user_id = ?", (user_id,))
    keys = [row[0] for row in cursor.fetchall()]
    conn.close()
    return keys

def get_stock(game_name=None):
    conn = get_connection()
    cursor = conn.cursor()
    if game_name:
        cursor.execute("SELECT COUNT(*) FROM keys WHERE game_name = ? AND is_used = 0", (game_name,))
    else:
        cursor.execute("SELECT COUNT(*) FROM keys WHERE is_used = 0")
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

def get_total_purchases():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM payments WHERE status = 'approved'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def update_payment_status(payment_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE payments SET status = ? WHERE id = ?", (status, payment_id))
    conn.commit()
    conn.close()
