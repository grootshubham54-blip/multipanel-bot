import sqlite3
import shutil
import os

def get_conn():
    return sqlite3.connect("bot_database.db", check_same_thread=False)

def create_tables():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
    # 'used' को 0/1 में ट्रैक कर रहे हैं, ये सही है
    cur.execute("CREATE TABLE IF NOT EXISTS keys (id INTEGER PRIMARY KEY AUTOINCREMENT, game TEXT, plan TEXT, key TEXT, used INTEGER DEFAULT 0, user_id INTEGER)")
    conn.commit()
    conn.close()

def save_key(game, key, plan):
    conn = get_conn()
    cur = conn.cursor()
    # ध्यान दें: हमने यहाँ .strip() लगाया है ताकि फालतू स्पेस न हो
    cur.execute("INSERT INTO keys (game, plan, key, used) VALUES (?, ?, ?, 0)", 
                (game.strip(), plan.strip(), key.strip()))
    conn.commit()
    conn.close()

def approve_and_assign_key(user_id, game, plan):
    conn = get_conn()
    cur = conn.cursor()
    # यहाँ game.strip() और plan.strip() करना बहुत जरूरी है ताकि बोट के बटन वाले टेक्स्ट से मैच हो
    cur.execute("SELECT id, key FROM keys WHERE game=? AND plan=? AND used=0 LIMIT 1", 
                (game.strip(), plan.strip()))
    row = cur.fetchone()
    
    if row:
        kid, key = row
        # की को 'used' मार्क किया और साथ में उस यूजर की आईडी डाल दी
        cur.execute("UPDATE keys SET used=1, user_id=? WHERE id=?", (int(user_id), kid))
        conn.commit()
        conn.close()
        return key
    
    conn.close()
    return None

def get_all_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall() # यह list of tuples देता है
    conn.close()
    return users

def get_stock_count(game, plan):
    conn = get_conn()
    cur = conn.cursor()
    # यहाँ भी strip() का उपयोग किया है ताकि काउंट सही दिखे
    cur.execute("SELECT COUNT(*) FROM keys WHERE game=? AND plan=? AND used=0", 
                (game.strip(), plan.strip()))
    count = cur.fetchone()[0]
    conn.close()
    return count

# ये एक्स्ट्रा फीचर्स जो आपके मुख्य बोट कोड में इस्तेमाल हो रहे थे
def get_user_keys(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT game, plan, key FROM keys WHERE user_id=? AND used=1", (int(user_id),))
    keys = cur.fetchall()
    conn.close()
    return keys

def get_sold_keys_count():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM keys WHERE used=1")
    count = cur.fetchone()[0]
    conn.close()
    return count

def get_total_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    conn.close()
    return count
