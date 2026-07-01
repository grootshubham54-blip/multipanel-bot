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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE,
        status TEXT DEFAULT 'available'
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


def save_key(key):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO keys (key)
        VALUES (?)
        """,
        (key,)
    )

    conn.commit()
    conn.close()


def get_stock():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) FROM keys
        WHERE status='available'
        """
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count


def delete_key(key):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM keys
        WHERE key=?
        """,
        (key,)
    )

    conn.commit()
    conn.close()


def update_payment_status(payment_id, status):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE payments
        SET status=?
        WHERE id=?
        """,
        (status, payment_id)
    )

    conn.commit()
    conn.close()


def get_total_users():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count


def get_total_purchases():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) FROM payments
        WHERE status='approved'
        """
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count