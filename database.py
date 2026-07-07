import sqlite3
import os

# डेटाबेस फाइल का नाम
DB_NAME = "bot_data.db"

def get_conn():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn

def create_tables():
    conn = get_conn()
    cur = conn.cursor()
    # Users table
    cur.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)''')
    # Keys table
    cur.execute('''CREATE TABLE IF NOT EXISTS keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    game TEXT, 
                    plan TEXT, 
                    key_code TEXT, 
                    used INTEGER DEFAULT 0, 
                    user_id INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def save_key(game, key_code, plan):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO keys (game, plan, key_code) VALUES (?, ?, ?)", (game, plan, key_code))
    conn.commit()
    conn.close()

def get_stock_count(game, plan):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM keys WHERE game = ? AND plan = ? AND used = 0", (game, plan))
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

def get_all_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = [row[0] for row in cur.fetchall()]
    conn.close()
    return users

def approve_and_assign_key(uid, game, plan):
    conn = get_conn()
    cur = conn.cursor()
    # पहली खाली की ढूंढें
    cur.execute("SELECT id, key_code FROM keys WHERE game = ? AND plan = ? AND used = 0 LIMIT 1", (game, plan))
    row = cur.fetchone()
    if row:
        kid, key = row
        cur.execute("UPDATE keys SET used = 1, user_id = ? WHERE id = ?", (uid, kid))
        conn.commit()
        conn.close()
        return key
    conn.close()
    return None

def get_user_keys(uid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT game, plan, key_code FROM keys WHERE user_id = ?", (uid,))
    data = cur.fetchall()
    conn.close()
    return data

def get_key_by_user_id(uid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT game, plan, key_code FROM keys WHERE user_id = ?", (uid,))
    data = cur.fetchall()
    conn.close()
    return data

def get_all_keys_export():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM keys")
    data = cur.fetchall()
    conn.close()
    return data

def create_backup():
    # यह डेटाबेस फाइल की कॉपी बना देगा
    import shutil
    backup_path = "backup_bot_data.db"
    shutil.copyfile(DB_NAME, backup_path)
    return backup_path

def get_sold_keys_count():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM keys WHERE used = 1")
    count = cur.fetchone()[0]
    conn.close()
    return count
