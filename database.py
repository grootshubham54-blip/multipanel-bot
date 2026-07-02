import sqlite3
import os

DB = "bot.db"

def conn():
    return sqlite3.connect(DB)

# ---------------- INIT ----------------
def create_tables():
    c = conn()
    cur = c.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        game TEXT,
        plan TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game TEXT,
        plan TEXT,
        key TEXT,
        used INTEGER DEFAULT 0,
        used_by INTEGER
    )
    """)

    c.commit()
    c.close()

# ---------------- USERS ----------------
def add_user(uid, username=None):
    c = conn()
    cur = c.cursor()
    cur.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (uid,))
    c.commit()
    c.close()

# ---------------- PAYMENTS ----------------
def create_payment(uid, game=None, plan=None):
    c = conn()
    cur = c.cursor()

    cur.execute(
        "INSERT INTO payments(user_id, game, plan) VALUES(?,?,?)",
        (uid, game, plan)
    )

    c.commit()
    pid = cur.lastrowid
    c.close()
    return pid

def get_payment(pid):
    c = conn()
    cur = c.cursor()
    cur.execute("SELECT user_id, game, plan FROM payments WHERE id=?", (pid,))
    row = cur.fetchone()
    c.close()
    return row

def approve_payment(pid, status="approved"):
    c = conn()
    cur = c.cursor()
    cur.execute("UPDATE payments SET status=? WHERE id=?", (status, pid))
    c.commit()
    c.close()

# ---------------- KEYS ----------------
def assign_key(uid, game, plan):
    c = conn()
    cur = c.cursor()

    cur.execute("""
    SELECT id, key FROM keys
    WHERE game=? AND plan=? AND used=0
    LIMIT 1
    """, (game, plan))

    row = cur.fetchone()

    if not row:
        c.close()
        return None

    key_id, key = row

    cur.execute("""
    UPDATE keys SET used=1, used_by=? WHERE id=?
    """, (uid, key_id))

    c.commit()
    c.close()

    return key