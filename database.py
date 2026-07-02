import sqlite3
import os
import threading
from datetime import datetime

DB_PATH = os.path.join(os.getcwd(), "bot_database.db")
lock = threading.Lock()


# ---------------- CONNECTION ----------------
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- INIT DB ----------------
def create_tables():
    with lock:
        conn = get_connection()
        cur = conn.cursor()

        # USERS
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # KEYS INVENTORY
        cur.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_name TEXT NOT NULL,
            plan TEXT NOT NULL,
            key_code TEXT NOT NULL UNIQUE,
            is_used INTEGER DEFAULT 0,
            user_id INTEGER,
            used_at TIMESTAMP
        )
        """)

        # PAYMENTS (STATE MACHINE)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_name TEXT NOT NULL,
            plan TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()


# ---------------- USER ----------------
def add_user(user_id, username=None):
    with lock:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO users (user_id, username)
            VALUES (?, ?)
        """, (user_id, username))
        conn.commit()
        conn.close()


# ---------------- PAYMENT ----------------
def add_payment(user_id, game, plan):
    with lock:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO payments (user_id, game_name, plan)
            VALUES (?, ?, ?)
        """, (user_id, game, plan))
        conn.commit()
        pid = cur.lastrowid
        conn.close()
        return pid


def get_payment(payment_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
    row = cur.fetchone()
    conn.close()
    return row


def approve_payment(payment_id):
    with lock:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE payments
            SET status='approved', processed_at=?
            WHERE id=?
        """, (datetime.utcnow(), payment_id))
        conn.commit()
        conn.close()


def reject_payment(payment_id):
    with lock:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE payments
            SET status='rejected', processed_at=?
            WHERE id=?
        """, (datetime.utcnow(), payment_id))
        conn.commit()
        conn.close()


# ---------------- KEYS (ATOMIC SAFE) ----------------
def assign_key(user_id, game, plan):
    """
    SAFE atomic key assignment (NO DOUBLE SELL)
    """
    with lock:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, key_code FROM keys
            WHERE game_name=? AND plan=? AND is_used=0
            LIMIT 1
        """, (game, plan))

        row = cur.fetchone()

        if not row:
            conn.close()
            return None

        key_id = row["id"]
        key_code = row["key_code"]

        cur.execute("""
            UPDATE keys
            SET is_used=1,
                user_id=?,
                used_at=?
            WHERE id=?
        """, (user_id, datetime.utcnow(), key_id))

        conn.commit()
        conn.close()

        return key_code


def save_key(game, plan, key_code):
    with lock:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO keys (game_name, plan, key_code)
            VALUES (?, ?, ?)
        """, (game, plan, key_code))
        conn.commit()
        conn.close()


# ---------------- STATS ----------------
def get_stock_count(game, plan):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) as cnt FROM keys
        WHERE game_name=? AND plan=? AND is_used=0
    """, (game, plan))
    result = cur.fetchone()
    conn.close()
    return result["cnt"]


def get_total_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM users")
    result = cur.fetchone()
    conn.close()
    return result["cnt"]