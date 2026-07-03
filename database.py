import sqlite3

def get_conn():
    return sqlite3.connect("bot_database.db")

def create_tables():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS keys (id INTEGER PRIMARY KEY AUTOINCREMENT, game TEXT, plan TEXT, key TEXT, used INTEGER DEFAULT 0, user_id INTEGER)")
    conn.commit()
    conn.close()

# ब्रॉडकास्ट फीचर
def get_all_user_ids():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    ids = [row[0] for row in cur.fetchall()]
    conn.close()
    return ids

# Delete Key फीचर - यह फंक्शन जोड़ना जरूरी है
def delete_key_by_id(key_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM keys WHERE id=?", (key_id,))
    conn.commit()
    conn.close()

# Key Report with ID - यह फंक्शन भी जरूरी है
def get_all_keys_report_with_id():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, game, plan, key, used, user_id FROM keys")
    keys = cur.fetchall()
    conn.close()
    return keys

def save_key(game, key, plan):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO keys (game, plan, key) VALUES (?, ?, ?)", (game.strip(), plan.strip(), key.strip()))
    conn.commit()
    conn.close()

def get_user_keys(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT game, plan, key FROM keys WHERE user_id=? AND used=1", (user_id,))
    keys = cur.fetchall()
    conn.close()
    return keys

def get_stock_count(game, plan):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM keys WHERE game=? AND plan=? AND used=0", (game.strip(), plan.strip()))
    count = cur.fetchone()[0]
    conn.close()
    return count

def get_total_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    conn.close()
    return count

def approve_and_assign_key(user_id, game, plan):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, key FROM keys WHERE game=? AND plan=? AND used=0 LIMIT 1", (game.strip(), plan.strip()))
    row = cur.fetchone()
    if row:
        kid, key = row
        cur.execute("UPDATE keys SET used=1, user_id=? WHERE id=?", (user_id, kid))
        conn.commit()
        conn.close()
        return key
    conn.close()
    return None
