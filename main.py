import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# इम्पोर्ट्स (सुनिश्चित करें कि database.py उसी फोल्डर में है)
from database import (
    create_tables, add_user, update_payment_status, save_key, 
    get_stock, get_total_users, get_total_purchases, get_user_keys, DB_PATH
)

# Logging Setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text("👑 Welcome to KING iOS Bot\nSelect an option:", reply_markup=get_main_keyboard(user.id))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # KEY Feature: My Keys
    if text == "🔑 My Keys":
        keys = get_user_keys(user.id)
        if keys:
            await update.message.reply_text(f"🔑 *Your Keys:*\n" + "\n".join([f"`{k}`" for k in keys]), parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No keys found for your account.")
        return

    # एडमिन के लिए स्टॉप/ब्रॉडकास्ट लॉजिक यहाँ आएगा...
    
    # बाकी मेनू (Games, Profile, आदि) यहाँ जोड़ें
    if text == "🎮 Games":
        # अपना गेम का कीबोर्ड यहाँ डालें
        pass

def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def main():
    if not TOKEN:
        logger.error("BOT_TOKEN missing!")
        return

    create_tables() # डेटाबेस टेबल चेक/क्रिएट करें
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    logger.info("Bot started successfully!")
    app.run_polling()

if __name__ == "__main__":
    main()
