import sqlite3

DB_NAME = "bot.db"


def save_payment(user_id, plan, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO payments (user_id, plan, amount, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            plan,
            amount,
            "pending"
        )
    )

    payment_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return payment_id