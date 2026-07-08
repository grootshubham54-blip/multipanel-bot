import sqlite3, shutil, os

# गेम और प्लान का डेटा
GAME_PLANS = {
    "👑 ✦ 𝕂𝕀ℕ𝔾 𝕚𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "⭐️ ✦ 𝕎𝕀ℕ𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "🚀 ✦ ℕ𝔼𝕏𝕋 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800"},
    "🪐 ✦ 𝕄𝕒𝕣𝕤 𝕃𝕠𝕒𝕕𝕖𝕣 ✦": {"1 Day": "130", "1 Week": "599"},
    "💀 ✦ 𝔻𝔼𝔸𝔻𝔼𝕐𝔼 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "🐬 ✦ 𝔻𝕆𝕃ℙℍ𝕀ℕ 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

def get_conn(): 
    return sqlite3.connect("bot_data.db", check_same_thread=False)

def create_tables():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS keys (id INTEGER PRIMARY KEY, game TEXT, plan TEXT, key TEXT, used INTEGER DEFAULT 0, user_id INTEGER)")
    conn.commit(); conn.close()

def save_user_to_db(user_id, username):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit(); conn.close()

def save_key(game, key, plan):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO keys (game, plan, key) VALUES (?, ?, ?)", (game, plan, key))
    conn.commit(); conn.close()

def get_stock_count(game, plan):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM keys WHERE game=? AND plan=? AND used=0", (game, plan))
    count = cur.fetchone()[0]; conn.close(); return count

def get_stock_count_all():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM keys WHERE used=0")
    count = cur.fetchone()[0]; conn.close(); return count

def approve_and_assign_key(user_id, game, plan):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT id, key FROM keys WHERE game=? AND plan=? AND used=0 LIMIT 1", (game, plan))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE keys SET used=1, user_id=? WHERE id=?", (user_id, row[0]))
        conn.commit(); conn.close(); return row[1]
    conn.close(); return None

def get_user_keys(user_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT game, plan, key FROM keys WHERE user_id=?", (user_id,)); rows = cur.fetchall(); conn.close(); return rows

def get_total_users():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users"); count = cur.fetchone()[0]; conn.close(); return count

def get_sold_keys_count():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM keys WHERE used=1"); count = cur.fetchone()[0]; conn.close(); return count

def create_backup():
    if os.path.exists("bot_data.db"):
        shutil.copy("bot_data.db", "backup.db")
        return "backup.db"
    return "Error: Database not found."
