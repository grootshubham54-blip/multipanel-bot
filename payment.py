import sqlite3

# इसे 'bot_database.db' करें ताकि यह डेटाबेस वाली फाइल के साथ सिंक रहे
DB_NAME = "bot_database.db" 

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
