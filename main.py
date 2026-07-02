import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from database import (
    create_tables, add_user, update_payment_status, save_key, 
    get_stock, get_total_users, get_total_purchases, get_user_keys, DB_PATH
)
from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# --- KEYBOARD HELPERS ---
def get_main_keyboard(user_id):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- HANDLER ---
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # 1. My Keys Logic
    if text == "🔑 My Keys":
        keys = get_user_keys(user.id)
        await update.message.reply_text(f"🔑 Your Keys: \n{', '.join(keys) if keys else 'No keys found.'}")

    # 2. Admin Panel Entry
    elif text == "⚙️ Admin Panel" and user.id == ADMIN_ID:
        await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())

    # 3. Admin: Stock & Stats
    elif text == "📦 Stock" and user.id == ADMIN_ID:
        await update.message.reply_text(f"📦 Total Stock: {get_stock()}", reply_markup=admin_game_selection_keyboard())

    elif text == "👥 Total Users" and user.id == ADMIN_ID:
        await update.message.reply_text(f"👥 Total Users: {get_total_users()}")

    # 4. Games Menu
    elif text == "🎮 Games":
        await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard())

    # (यहाँ अपने बाकी के सभी if-elif लॉजिक जोड़ें जो गेम सिलेक्शन और पेमेंट के लिए हैं)

# --- MAIN ---
def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Welcome!", reply_markup=get_main_keyboard(u.effective_user.id))))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    app.run_polling()

if __name__ == "__main__":
    main()
