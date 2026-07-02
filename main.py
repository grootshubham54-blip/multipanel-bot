import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    ContextTypes, filters
)

# Database और अन्य फाइल्स इम्पोर्ट करें
from database import (
    create_tables, add_user, update_payment_status, save_key, 
    get_stock, get_total_users, get_total_purchases, get_user_keys
)
from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# --- KEYBOARD FUNCTIONS ---
def get_main_keyboard(user_id):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text("👑 Welcome to KING iOS Bot!", reply_markup=get_main_keyboard(user.id))

# --- MESSAGE HANDLER ---
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text == "🔑 My Keys":
        keys = get_user_keys(user.id)
        if keys:
            await update.message.reply_text("🔑 *Your Keys:*\n" + "\n".join([f"`{k}`" for k in keys]), parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No keys found.")
    
    elif text == "🎮 Games":
        await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard())

    # बाकी सभी बटन लॉजिक यहाँ जोड़ें...

# --- MAIN ---
def main():
    if not TOKEN:
        print("CRITICAL ERROR: BOT_TOKEN not found!")
        return

    create_tables() # टेबल बनाएँ
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
