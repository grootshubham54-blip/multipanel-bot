import sqlite3

def get_conn():
    return sqlite3.connect("bot_database.db")

def create_tables():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS keys (id INTEGER PRIMARY KEY AUTOINCREMENT, game TEXT, plan TEXT, key TEXT, used INTEGER DEFAULT 0, user_id INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS pending_payments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, game TEXT, plan TEXT, photo_file_id TEXT)")
    conn.commit()
    conn.close()

def add_user(user_id, username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def save_key(game, plan, key):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO keys (game, plan, key) VALUES (?, ?, ?)", (game, plan, key))
    conn.commit()
    conn.close()

def get_user_keys(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT game, plan, key FROM keys WHERE user_id=? AND used=1", (user_id,))
    keys = cur.fetchall()
    conn.close()
    return keys

# फिक्स: जो फंक्शन्स missing थे
def get_stock_count():
    return 0 

def get_total_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    conn.close()
    return count

def approve_and_assign_key(pending_id):
    # यह आपका मौजूदा अप्रूवल लॉजिक होगा
    return None, None
