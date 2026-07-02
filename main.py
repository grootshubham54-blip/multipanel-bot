import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# 1. डेटाबेस का सही पाथ सेट करें (रेलवे के लिए)
DB_PATH = os.path.join(os.getcwd(), "bot_database.db")

# Logging Setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Mappings
GAME_MAPPING = {
    "👑 KING iOS": "king", "WINIOS": "win", "NEXT IOS": "next",
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "mars", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀": "dead", "DOLPHIN IOS": "dolphin"
}
REVERSE_GAME_MAPPING = {v: k for k, v in GAME_MAPPING.items()}

# --- DATABASE HELPERS ---
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# (बाकी आपके database.py वाले फंक्शन यहीं होने चाहिए, सुनिश्चित करें कि वे DB_PATH का उपयोग कर रहे हैं)

# --- KEYBOARD HELPERS ---
def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # add_user(user.id, user.username or "No Username") # सुनिश्चित करें यह फंक्शन import है
    await update.message.reply_text("👑 Welcome to KING iOS Bot\nSelect an option:", reply_markup=get_main_keyboard(user.id))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    
    # यहाँ आपका पूरा लॉजिक वही रहेगा जो आपने दिया था
    # बस सुनिश्चित करें कि सभी SQL कॉल्स get_db_connection() का उपयोग कर रही हैं
    if text == "🎮 Games":
        await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup([["👑 KING iOS"], ["WINIOS"], ["🔙 Back to Main"]], resize_keyboard=True))
    # ... बाकी का कोड वैसे ही रहने दें ...

def main():
    if not TOKEN:
        logger.error("BOT_TOKEN missing in environment variables!")
        return

    # App build
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
