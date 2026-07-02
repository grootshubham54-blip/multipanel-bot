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

def get_user_keys(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT game, plan, key FROM keys WHERE user_id=? AND used=1", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def add_user(user_id, username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def save_pending_payment(user_id, game, plan, photo_file_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO pending_payments (user_id, game, plan, photo_file_id) VALUES (?, ?, ?, ?)", (user_id, game, plan, photo_file_id))
    conn.commit()
    conn.close()

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
