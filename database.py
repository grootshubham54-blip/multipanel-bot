import sqlite3
from datetime import datetime


DB_NAME = "bot.db"


# ==========================
# DATABASE CONNECT
# ==========================

def connect():
    return sqlite3.connect(DB_NAME)



# ==========================
# CREATE TABLES
# ==========================

def create_tables():

    con = connect()
    cur = con.cursor()


    # USERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
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
        status TEXT DEFAULT 'available'
    )
    """)


    # USER KEYS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_keys(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        game TEXT,
        plan TEXT,
        key TEXT,
        date TEXT
    )
    """)


    # PAYMENTS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        game TEXT,
        plan TEXT,
        amount INTEGER,
        status TEXT DEFAULT 'pending',
        date TEXT
    )
    """)


    # ==========================
    # GAME MANAGEMENT TABLES
    # ==========================


    cur.execute("""
    CREATE TABLE IF NOT EXISTS games(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_name TEXT UNIQUE,
        status TEXT DEFAULT 'active'
    )
    """)


    cur.execute("""
    CREATE TABLE IF NOT EXISTS game_plans(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_name TEXT,
        plan_name TEXT,
        price INTEGER
    )
    """)



    con.commit()
    con.close()



# ==========================
# USERS
# ==========================

def add_user(user_id, username):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    INSERT OR IGNORE INTO users
    (
        user_id,
        username,
        joined
    )
    VALUES(?,?,?)
    """,
    (
        user_id,
        username,
        datetime.now().strftime("%Y-%m-%d")
    ))


    con.commit()
    con.close()



def get_total_users():

    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM users"
    )

    result = cur.fetchone()[0]

    con.close()

    return result



def get_all_users():

    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT user_id FROM users"
    )

    data = cur.fetchall()

    con.close()

    return data



# ==========================
# KEY MANAGEMENT
# ==========================

def add_key(game, plan, key):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    INSERT INTO keys
    (
        game,
        plan,
        key,
        status
    )
    VALUES(?,?,?,'available')
    """,
    (
        game,
        plan,
        key
    ))


    con.commit()
    con.close()



def get_available_key(game, plan):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    SELECT id,key
    FROM keys
    WHERE game=?
    AND plan=?
    AND status='available'
    LIMIT 1
    """,
    (
        game,
        plan
    ))


    result = cur.fetchone()


    if not result:

        con.close()
        return None


    key_id = result[0]
    key = result[1]


    cur.execute("""
    UPDATE keys
    SET status='sold'
    WHERE id=?
    """,
    (key_id,))


    con.commit()
    con.close()


    return key
    
    
# ==========================
# USER KEYS
# ==========================

def save_user_key(user_id, game, plan, key):

    con = connect()
    cur = con.cursor()

    cur.execute("""
    INSERT INTO user_keys
    (
        user_id,
        game,
        plan,
        key,
        date
    )
    VALUES(?,?,?,?,?)
    """,
    (
        user_id,
        game,
        plan,
        key,
        datetime.now().strftime("%Y-%m-%d")
    ))

    con.commit()
    con.close()



def get_user_keys(user_id):

    con = connect()
    cur = con.cursor()

    cur.execute("""
    SELECT game,plan,key
    FROM user_keys
    WHERE user_id=?
    """,
    (user_id,))


    data = cur.fetchall()

    con.close()

    return data



# ==========================
# PAYMENTS
# ==========================

def save_payment(user_id, game, plan, amount):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    INSERT INTO payments
    (
        user_id,
        game,
        plan,
        amount,
        date
    )
    VALUES(?,?,?,?,?)
    """,
    (
        user_id,
        game,
        plan,
        amount,
        datetime.now().strftime("%Y-%m-%d")
    ))


    payment_id = cur.lastrowid


    con.commit()
    con.close()


    return payment_id




def get_payment(payment_id):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    SELECT
    user_id,
    game,
    plan,
    amount,
    status

    FROM payments

    WHERE id=?
    """,
    (payment_id,))


    data = cur.fetchone()


    con.close()

    return data




def update_payment(payment_id,status):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    UPDATE payments
    SET status=?
    WHERE id=?
    """,
    (
        status,
        payment_id
    ))


    con.commit()
    con.close()




def get_payment_history():

    con = connect()
    cur = con.cursor()


    cur.execute("""
    SELECT
    id,
    user_id,
    game,
    plan,
    amount,
    status,
    date

    FROM payments

    ORDER BY id DESC
    """)


    data = cur.fetchall()


    con.close()

    return data





# ==========================
# STATISTICS
# ==========================

def get_statistics():

    con = connect()
    cur = con.cursor()


    cur.execute("""
    SELECT
    COUNT(*),
    COALESCE(SUM(amount),0)

    FROM payments

    WHERE status='accepted'
    """)


    data = cur.fetchone()


    con.close()


    return data[0], data[1]





# ==========================
# GAME MANAGEMENT
# ==========================


def add_game(game_name):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    INSERT OR IGNORE INTO games
    (
        game_name,
        status
    )
    VALUES(?,?)
    """,
    (
        game_name,
        "active"
    ))


    con.commit()
    con.close()




def delete_game(game_name):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    DELETE FROM games
    WHERE game_name=?
    """,
    (game_name,))


    cur.execute("""
    DELETE FROM game_plans
    WHERE game_name=?
    """,
    (game_name,))


    con.commit()
    con.close()




def set_game_status(game_name,status):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    UPDATE games
    SET status=?
    WHERE game_name=?
    """,
    (
        status,
        game_name
    ))


    con.commit()
    con.close()




def add_game_plan(game_name,plan_name,price):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    INSERT INTO game_plans
    (
        game_name,
        plan_name,
        price
    )
    VALUES(?,?,?)
    """,
    (
        game_name,
        plan_name,
        price
    ))


    con.commit()
    con.close()




def update_game_price(plan_id,price):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    UPDATE game_plans
    SET price=?
    WHERE id=?
    """,
    (
        price,
        plan_id
    ))


    con.commit()
    con.close()




def get_games():

    con = connect()
    cur = con.cursor()


    cur.execute("""
    SELECT
    game_name,
    status

    FROM games
    """)


    data = cur.fetchall()


    con.close()

    return data




def get_game_plans(game_name):

    con = connect()
    cur = con.cursor()


    cur.execute("""
    SELECT
    id,
    plan_name,
    price

    FROM game_plans

    WHERE game_name=?
    """,
    (game_name,))


    data = cur.fetchall()


    con.close()

    return data