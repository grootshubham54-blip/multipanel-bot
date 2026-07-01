import sqlite3

DB_NAME = "bot.db"


def connect():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        status TEXT DEFAULT 'active'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        plan TEXT,
        amount TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    conn.commit()
    conn.close()


def add_user(user_id, username):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username)
    )

    conn.commit()
    conn.close()


def update_payment_status(payment_id, status):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE payments
        SET status = ?
        WHERE id = ?
        """,
        (status, payment_id)
    )

    conn.commit()
    conn.close()


def get_payment(payment_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT user_id, plan, amount, status
        FROM payments
        WHERE id = ?
        """,
        (payment_id,)
    )

    payment = cursor.fetchone()

    conn.close()

    return payment