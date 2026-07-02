import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# अपनी फाइल्स को इम्पोर्ट करें
from database import (
    create_tables, add_user, update_payment_status, save_key, 
    get_stock, get_total_users, get_total_purchases, get_user_keys, DB_PATH
)
from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Logging Setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# --- KEYBOARD HELPERS ---
def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- START HANDLER ---
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
            await update.message.reply_text(f"🔑 *Your Keys:*\n" + "\n".join([f"`{k}`" for k in keys]), parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No keys found for your account.")
        return

    # यहाँ आप अपने पुराने लॉजिक (Broadcast, Games Menu, Payment Logic) जोड़ सकते हैं।
    # बस ध्यान रखें कि जहाँ भी डेटाबेस कॉल हो, वहाँ database.py के फंक्शन ही यूज़ करें।

    if user.id == ADMIN_ID and text == "⚙️ Admin Panel":
        await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())

# --- MAIN ---
def main():
    if not TOKEN:
        logger.error("BOT_TOKEN missing!")
        return

    create_tables() # टेबल सेटअप
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    # app.add_handler(CallbackQueryHandler(admin_action)) # इसे अनकमेंट करें जब admin_action फंक्शन जोड़ें

    logger.info("Bot started successfully!")
    app.run_polling()

if __name__ == "__main__":
    main()
