import sqlite3, shutil, os

def get_conn(): return sqlite3.connect("bot_data.db", check_same_thread=False)

def create_tables():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS keys (id INTEGER PRIMARY KEY, game TEXT, plan TEXT, key TEXT, used INTEGER DEFAULT 0, user_id INTEGER)")
    conn.commit(); conn.close()

def save_key(game, key, plan):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO keys (game, plan, key) VALUES (?, ?, ?)", (game, plan, key))
    conn.commit(); conn.close()

def get_stock_count(game, plan):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM keys WHERE game=? AND plan=? AND used=0", (game, plan))
    count = cur.fetchone()[0]; conn.close(); return count

def approve_and_assign_key(user_id, game, plan):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT id, key FROM keys WHERE game=? AND plan=? AND used=0 LIMIT 1", (game, plan))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE keys SET used=1, user_id=? WHERE id=?", (user_id, row[0]))
        conn.commit(); conn.close(); return row[1]
    conn.close(); return None

def save_user_to_db(user_id, username):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit(); conn.close()

def get_all_users():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT user_id FROM users"); users = [r[0] for r in cur.fetchall()]; conn.close(); return users

def get_total_users():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users"); count = cur.fetchone()[0]; conn.close(); return count

def get_user_keys(user_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT game, plan, key FROM keys WHERE user_id=?", (user_id,)); rows = cur.fetchall(); conn.close(); return rows

def get_key_by_user_id(user_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT game, plan, key FROM keys WHERE user_id=?", (user_id,)); rows = cur.fetchall(); conn.close(); return rows

def get_all_keys_export():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT * FROM keys"); rows = cur.fetchall(); conn.close(); return rows

def get_sold_keys_count():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM keys WHERE used=1"); count = cur.fetchone()[0]; conn.close(); return count

def create_backup():
    shutil.copy("bot_data.db", "backup.db"); return "backup.db"
