import sqlite3

def get_conn(): return sqlite3.connect("bot_data.db", check_same_thread=False)

def create_tables():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS keys (id INTEGER PRIMARY KEY, game TEXT, plan TEXT, key TEXT, used INTEGER DEFAULT 0, user_id INTEGER)")
    conn.commit(); conn.close()

def save_key(game, plan, key):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO keys (game, plan, key) VALUES (?, ?, ?)", (game, plan, key))
    conn.commit(); conn.close()

def get_stock_count(game, plan):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM keys WHERE game=? AND plan=? AND used=0", (game, plan))
    count = cur.fetchone()[0]; conn.close(); return count

def get_total_users():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users"); count = cur.fetchone()[0]; conn.close(); return count

def get_all_keys_report():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT game, plan, key, used, user_id FROM keys")
    rows = cur.fetchall(); conn.close(); return rows

def get_user_keys(uid):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT game, plan, key FROM keys WHERE user_id=?", (uid,)); rows = cur.fetchall(); conn.close(); return rows

def approve_and_assign_key(uid, game, plan):
    conn = get_conn(); cur = conn.cursor()
    # Corrected function to match the main.py logic
    cur.execute("SELECT id, key FROM keys WHERE game=? AND plan=? AND used=0 LIMIT 1", (game, plan))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE keys SET used=1, user_id=? WHERE id=?", (uid, row[0]))
        conn.commit(); conn.close(); return row[1]
    conn.close(); return None

def save_user(uid, uname):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (uid, uname))
    conn.commit(); conn.close()
