import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593

# --- 1. डेटाबेस फंक्शन्स ---
def get_conn(): return sqlite3.connect("bot_database.db")

def create_tables():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS keys (id INTEGER PRIMARY KEY AUTOINCREMENT, game TEXT, plan TEXT, key TEXT, used INTEGER DEFAULT 0, user_id INTEGER)")
    conn.commit(); conn.close()

def save_key(game, key, plan):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO keys (game, plan, key) VALUES (?, ?, ?)", (game, plan, key))
    conn.commit(); conn.close()

def approve_and_assign_key(uid, game, plan):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT id, key FROM keys WHERE game=? AND plan=? AND used=0 LIMIT 1", (game, plan))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE keys SET used=1, user_id=? WHERE id=?", (uid, row[0]))
        conn.commit(); conn.close(); return row[1]
    conn.close(); return None

# --- 2. कीबोर्ड फंक्शन्स ---
def admin_keyboard(): return ReplyKeyboardMarkup([["🔑 Add Keys"], ["🔙 Back"]], resize_keyboard=True)
def main_keyboard(is_admin):
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if is_admin: kb.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

# --- 3. मेन लॉजिक ---
GAME_PLANS = {"👑 KING iOS": {"1 Day": "200"}, "WINIOS": {"1 Day": "200"}} # अपना पूरा मैप यहाँ रखें
GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN"}

async def start(update, context):
    await update.message.reply_text("👋 Welcome!", reply_markup=main_keyboard(update.effective_user.id == ADMIN_ID))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "🛠 Admin Panel": await update.message.reply_text("Admin:", reply_markup=admin_keyboard())
    elif text == "🔙 Back": await start(update, context)
    elif text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_MAP.keys()]
        await update.message.reply_text("Select:", reply_markup=InlineKeyboardMarkup(kb))
    elif update.message.photo and user_id != ADMIN_ID:
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, 
            caption=f"Payment from {user_id}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_KING_1D")]]))
        await update.message.reply_text("✅ Sent!")

async def button_click(update, context):
    query = update.callback_query
    data = query.data
    if data.startswith("acc_"):
        _, uid, g, p = data.split("_")
        key = approve_and_assign_key(int(uid), g, p)
        if key: 
            await context.bot.send_message(int(uid), f"🔑 Key: {key}")
            await query.edit_message_caption("✅ Approved.")
        else: await query.edit_message_caption("⚠️ Out of stock!")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
