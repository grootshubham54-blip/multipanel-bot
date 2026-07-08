import sqlite3

GAME_PLANS = {
    "👑 ✦ 𝕂𝕀ℕ𝔾 𝕚𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "⭐️ ✦ 𝕎𝕀ℕ𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"}
}

def get_conn(): return sqlite3.connect("bot_data.db", check_same_thread=False)

def create_tables():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS keys (id INTEGER PRIMARY KEY, game TEXT, plan TEXT, key TEXT, used INTEGER DEFAULT 0, user_id INTEGER)")
    conn.commit(); conn.close()

def save_key(g, k, p):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO keys (game, plan, key) VALUES (?, ?, ?)", (g, p, k))
    conn.commit(); conn.close()

def get_total_stock():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM keys WHERE used=0")
    count = cur.fetchone()[0]; conn.close(); return count

def get_sold_keys_count():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM keys WHERE used=1"); count = cur.fetchone()[0]; conn.close(); return count

def approve_and_assign_key(uid, game, plan):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT id, key FROM keys WHERE game=? AND plan=? AND used=0 LIMIT 1", (game, plan))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE keys SET used=1, user_id=? WHERE id=?", (uid, row[0]))
        conn.commit(); conn.close(); return row[1]
    conn.close(); return None

def save_user_to_db(uid, user):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (uid, user))
    conn.commit(); conn.close()

def get_user_keys(uid):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT game, plan, key FROM keys WHERE user_id=?", (uid,)); rows = cur.fetchall(); conn.close(); return rows
