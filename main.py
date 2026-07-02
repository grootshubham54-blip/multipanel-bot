import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Import custom modules
from database import (
    create_tables, add_user, update_payment_status, save_key, 
    get_stock, get_total_users, get_total_purchases, DB_NAME, get_user_keys
)
from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0)) 

GAME_MAPPING = {"👑 KING iOS": "king", "WINIOS": "win", "NEXT IOS": "next", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "mars", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀": "dead", "DOLPHIN IOS": "dolphin"}
REVERSE_GAME_MAPPING = {v: k for k, v in GAME_MAPPING.items()}

# --- HELPER FUNCTIONS ---
def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text("👑 Welcome to KING iOS Bot!", reply_markup=get_main_keyboard(user.id))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # FEATURE: My Keys - पुरानी कीज दिखाना
    if text == "🔑 My Keys":
        keys = get_user_keys(user.id)
        if keys:
            msg = "🔑 *Your Purchased Keys:*\n\n" + "\n".join([f"• `{k}`" for k in keys])
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No keys found. Purchase one to see it here.")
        return

    # एडमिन और अन्य लॉजिक...
    # (बाकी पुराना लॉजिक यहाँ वैसे ही रहेगा)
    if user.id == ADMIN_ID and text == "⚙️ Admin Panel":
        await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
        return
    
    # [यहाँ अन्य सभी कंडीशन्स वैसी ही रहें]

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # फीचर: मल्टीपल पेमेंट रिक्वेस्ट को रोकना
    if context.user_data.get("payment_in_progress"):
        await update.message.reply_text("⏳ Please wait! Your previous request is already under verification.")
        return

    # बाकी फोटो हैंडलर लॉजिक यहाँ लिखें...
    context.user_data["payment_in_progress"] = True
    # ... (बाकी कोडिंग)

def main():
    if not TOKEN:
        print("Error: TOKEN missing!")
        return

    create_tables()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(CallbackQueryHandler(admin_action))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
