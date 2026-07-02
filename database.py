Import sqlite3

DB_NAME = "bot_database.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT
    )
    """)
    
    # Keys Table (Updated with plan column)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_name TEXT,
        key_code TEXT,
        plan TEXT,
        is_used INTEGER DEFAULT 0
    )
    """)
    
    # Payments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        plan TEXT,
        amount TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)
    
    # Automatically add 'plan' column if the database already exists on Railway
    try:
        cursor.execute("ALTER TABLE keys ADD COLUMN plan TEXT")
    except sqlite3.OperationalError:
        # Column already exists, do nothing
        pass
    
    conn.commit()
    conn.close()

def add_user(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

# Updated to take 3 parameters (game_name, key_code, plan)
def save_key(game_name, key_code, plan):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO keys (game_name, key_code, plan) VALUES (?, ?, ?)", (game_name, key_code, plan))
    conn.commit()
    conn.close()

def get_stock(game_name=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if game_name:
        cursor.execute("SELECT COUNT(*) FROM keys WHERE game_name = ? AND is_used = 0", (game_name,))
        count = cursor.fetchone()[0]
    else:
        # Total stock of all games
        cursor.execute("SELECT COUNT(*) FROM keys WHERE is_used = 0")
        count = cursor.fetchone()[0]
    conn.close()
    return count

def get_total_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_total_purchases():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM payments WHERE status = 'approved'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def update_payment_status(payment_id, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE payments SET status = ? WHERE id = ?", (status, payment_id))
    conn.commit()
    conn.close()