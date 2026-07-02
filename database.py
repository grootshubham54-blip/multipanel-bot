import sqlite3

DB_PATH = "bot_database.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS keys (id INTEGER PRIMARY KEY AUTOINCREMENT, game TEXT, plan TEXT, key TEXT, used INTEGER DEFAULT 0, user_id INTEGER)")
    # पेंडिंग पेमेंट्स के लिए नया टेबल
    cur.execute("""CREATE TABLE IF NOT EXISTS pending_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER, 
                    game TEXT, 
                    plan TEXT, 
                    photo_file_id TEXT
                  )""")
    conn.commit()
    conn.close()

def save_pending_payment(user_id, game, plan, photo_file_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO pending_payments (user_id, game, plan, photo_file_id) VALUES (?, ?, ?, ?)", 
                (user_id, game, plan, photo_file_id))
    payment_id = cur.lastrowid
    conn.commit()
    conn.close()
    return payment_id

def approve_and_assign_key(pending_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id, game, plan FROM pending_payments WHERE id=?", (pending_id,))
    payment = cur.fetchone()
    
    if payment:
        uid, game, plan = payment
        cur.execute("SELECT id, key FROM keys WHERE game=? AND plan=? AND used=0 LIMIT 1", (game, plan))
        key_row = cur.fetchone()
        if key_row:
            kid, key = key_row
            cur.execute("UPDATE keys SET used=1, user_id=? WHERE id=?", (uid, kid))
            cur.execute("DELETE FROM pending_payments WHERE id=?", (pending_id,))
            conn.commit()
            conn.close()
            return key, uid
    conn.close()
    return None, None

def add_user(user_id, username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def save_key(game, key, plan):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO keys (game, plan, key) VALUES (?, ?, ?)", (game, plan, key))
    conn.commit()
    conn.close()
