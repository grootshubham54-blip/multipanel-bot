import sqlite3

DB_NAME = "bot.db"


def save_payment(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO payments (user_id, amount, status)
        VALUES (?, ?, ?)
        """,
        (user_id, amount, "pending")
    )

    conn.commit()
    conn.close()