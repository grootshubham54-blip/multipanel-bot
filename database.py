import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), "bot_database.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables():
    conn = get_conn()
    cur = conn.cursor()

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
        user_id INTEGER
    )
    """)

    conn.commit()
    conn.close()

def approve_and_assign_key(user_id, game, plan):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, key 
        FROM keys 
        WHERE game=? AND plan=? AND used=0 
        LIMIT 1
    """, (game, plan))

    row = cur.fetchone()

    if not row:
        conn.close()
        return None

    kid, key = row

    cur.execute("""
        UPDATE keys 
        SET used=1, user_id=? 
        WHERE id=?
    """, (user_id, kid))

    conn.commit()
    conn.close()
    return key