import sqlite3
from datetime import datetime

DB_NAME = "bot_data.db"

# =========================
# DATABASE CONNECTION
# =========================
def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

# =========================
# CREATE TABLES
# =========================
def create_tables():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        banned INTEGER DEFAULT 0,
        joined TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS keys(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game TEXT,
        plan TEXT,
        key TEXT,
        used INTEGER DEFAULT 0,
        user_id INTEGER
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        game TEXT,
        plan TEXT,
        status TEXT DEFAULT 'pending',
        created TEXT
    )""")

    conn.commit()
    conn.close()

# =========================
# USER FUNCTIONS
# =========================
def save_user(user_id, username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username, joined) VALUES (?, ?, ?)", 
                (user_id, username, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def get_total_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    conn.close()
    return count

# =========================
# KEY FUNCTIONS
# =========================
def save_key(game, plan, key):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO keys (game, plan, key) VALUES (?, ?, ?)", (game, plan, key))
    conn.commit()
    conn.close()

def approve_and_assign_key(uid, game, plan):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, key FROM keys WHERE game=? AND plan=? AND used=0 LIMIT 1", (game, plan))
    row = cur.fetchone()
    if row:
        key_id, key = row
        cur.execute("UPDATE keys SET used=1, user_id=? WHERE id=?", (uid, key_id))
        conn.commit()
        conn.close()
        return key
    conn.close()
    return None

def get_sold_keys_count():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM keys WHERE used=1")
    count = cur.fetchone()[0]
    conn.close()
    return count

def get_stock_count(game, plan):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM keys WHERE game=? AND plan=? AND used=0", (game, plan))
    count = cur.fetchone()[0]
    conn.close()
    return count

def get_user_keys(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT game, plan, key FROM keys WHERE user_id=?", (user_id,))
    data = cur.fetchall()
    conn.close()
    return data

# =========================
# ORDER FUNCTIONS
# =========================
def save_order(user_id, username, game, plan):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO orders (user_id, username, game, plan, status, created) VALUES (?,?,?,?,?,?)",
                (user_id, username, game, plan, "pending", datetime.now().strftime("%Y-%m-%d %H:%M")))
    order_id = cur.lastrowid
    conn.commit()
    conn.close()
    return order_id
