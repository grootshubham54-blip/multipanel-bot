import sqlite3
from datetime import datetime


DB_NAME = "bot_data.db"


# =========================
# DATABASE CONNECTION
# =========================

def get_conn():
    return sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )


# =========================
# CREATE TABLES
# =========================

def create_tables():

    conn = get_conn()
    cur = conn.cursor()


    # USERS

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        banned INTEGER DEFAULT 0,
        joined TEXT
    )
    """)


    # KEYS

    cur.execute("""
    CREATE TABLE IF NOT EXISTS keys(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game TEXT,
        plan TEXT,
        key TEXT,
        used INTEGER DEFAULT 0,
        user_id INTEGER
    )
    """)


    # ORDERS

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        game TEXT,
        plan TEXT,
        status TEXT DEFAULT 'pending',
        created TEXT
    )
    """)


    conn.commit()
    conn.close()



# =========================
# USER FUNCTIONS
# =========================

def save_user(user_id, username):

    conn = get_conn()
    cur = conn.cursor()


    cur.execute("""
    INSERT OR IGNORE INTO users
    (user_id, username, joined)
    VALUES (?, ?, ?)
    """,
    (
        user_id,
        username,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))


    conn.commit()
    conn.close()



def is_banned(user_id):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT banned FROM users WHERE user_id=?",
        (user_id,)
    )

    row = cur.fetchone()

    conn.close()


    if row and row[0] == 1:
        return True

    return False



def get_total_users():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM users"
    )

    count = cur.fetchone()[0]

    conn.close()

    return count



# =========================
# KEY FUNCTIONS
# =========================


def save_key(game, plan, key):

    conn = get_conn()
    cur = conn.cursor()


    cur.execute("""
    INSERT INTO keys
    (game, plan, key)
    VALUES (?, ?, ?)
    """,
    (
        game,
        plan,
        key
    ))


    conn.commit()
    conn.close()



def approve_order(order_id, game, plan):

    conn = get_conn()
    cur = conn.cursor()


    cur.execute("""
    SELECT id,key FROM keys
    WHERE game=? 
    AND plan=?
    AND used=0
    LIMIT 1
    """,
    (
        game,
        plan
    ))


    row = cur.fetchone()


    if not row:
        conn.close()
        return None



    key_id = row[0]
    key = row[1]


    cur.execute("""
    UPDATE keys
    SET used=1
    WHERE id=?
    """,
    (key_id,))


    cur.execute("""
    UPDATE orders
    SET status='approved'
    WHERE id=?
    """,
    (order_id,))


    conn.commit()
    conn.close()


    return key



def get_user_keys(user_id):

    conn = get_conn()
    cur = conn.cursor()


    cur.execute("""
    SELECT game,plan,key
    FROM keys
    WHERE user_id=?
    """,
    (user_id,))


    data = cur.fetchall()

    conn.close()

    return data



def get_stock():

    conn = get_conn()
    cur = conn.cursor()


    cur.execute("""
    SELECT game,plan,COUNT(*)
    FROM keys
    WHERE used=0
    GROUP BY game,plan
    """)


    data = cur.fetchall()

    conn.close()

    return data



def delete_key(key_id):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM keys WHERE id=?",
        (key_id,)
    )

    conn.commit()
    conn.close()



# =========================
# ORDER FUNCTIONS
# =========================


def save_order(user_id, username, game, plan):

    conn = get_conn()
    cur = conn.cursor()


    cur.execute("""
    INSERT INTO orders
    (user_id,username,game,plan,status,created)
    VALUES (?,?,?,?,?,?)
    """,
    (
        user_id,
        username,
        game,
        plan,
        "pending",
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))


    order_id = cur.lastrowid


    conn.commit()
    conn.close()


    return order_id



def get_order(order_id):

    conn = get_conn()
    cur = conn.cursor()


    cur.execute("""
    SELECT 
    id,user_id,username,game,plan,status
    FROM orders
    WHERE id=?
    """,
    (order_id,))


    row = cur.fetchone()

    conn.close()


    if not row:
        return None


    return {
        "id": row[0],
        "user_id": row[1],
        "username": row[2],
        "game": row[3],
        "plan": row[4],
        "status": row[5]
    }



def reject_order(order_id):

    conn = get_conn()
    cur = conn.cursor()


    cur.execute("""
    UPDATE orders
    SET status='rejected'
    WHERE id=?
    """,
    (order_id,))


    conn.commit()
    conn.close()



# =========================
# STATISTICS
# =========================


def get_statistics():

    conn = get_conn()
    cur = conn.cursor()


    cur.execute(
        "SELECT COUNT(*) FROM users"
    )
    users = cur.fetchone()[0]


    cur.execute(
        "SELECT COUNT(*) FROM orders"
    )
    orders = cur.fetchone()[0]


    cur.execute(
        "SELECT COUNT(*) FROM orders WHERE status='approved'"
    )
    approved = cur.fetchone()[0]


    cur.execute(
        "SELECT COUNT(*) FROM orders WHERE status='pending'"
    )
    pending = cur.fetchone()[0]


    cur.execute(
        "SELECT COUNT(*) FROM keys WHERE used=0"
    )
    keys = cur.fetchone()[0]


    conn.close()


    return {
        "users": users,
        "orders": orders,
        "approved": approved,
        "pending": pending,
        "keys": keys
    }