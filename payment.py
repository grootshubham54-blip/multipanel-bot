import sqlite3
import os

# Railway पर पाथ सिंक करने के लिए वही पाथ इस्तेमाल करें जो database.py में है
DB_PATH = os.path.join(os.getcwd(), "bot_database.db")

def save_payment(user_id, plan, amount):
    conn = sqlite3.connect(DB_PATH)
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
