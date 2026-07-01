import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, add_user, update_payment_status, save_key, get_stock, get_total_users, get_total_purchases, DB_NAME
from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

GAME_MAPPING = {"👑 KING iOS": "king", "WINIOS": "win", "NEXT IOS": "next", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "mars", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀": "dead", "DOLPHIN IOS": "dolphin"}
REVERSE_GAME_MAPPING = {v: k for k, v in GAME_MAPPING.items()}

def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID: keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard(target: str = "Main") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[f"🔙 Back to {target}"]], resize_keyboard=True)

def get_payment_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["❌ Cancel Payment"]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text("👑 Welcome to KING iOS Bot", reply_markup=get_main_keyboard(user.id))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # 1. ब्रॉडकास्ट लॉजिक
    if context.user_data.get("broadcasting"):
        msg = text
        context.user_data["broadcasting"] = False
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        conn.close()
        for u in users:
            try: await context.bot.send_message(chat_id=u[0], text=f"📢 *अनाउंसमेंट:*\n\n{msg}", parse_mode="Markdown")
            except: continue
        await update.message.reply_text("✅ अनाउंसमेंट भेज दी गई है!", reply_markup=get_main_keyboard(user.id))
        return

    # 2. नेविगेशन और एडमिन पैनल
    if text in ["🔙 Back to Main", "❌ Cancel Payment"]:
        context.user_data.clear()
        await update.message.reply_text("👑 Main Menu", reply_markup=get_main_keyboard(user.id))
    elif text == "⚙️ Admin Panel" and user.id == ADMIN_ID:
        await update.message.reply_text("👑 Admin Panel", reply_markup=admin_keyboard())
    elif text == "📢 Broadcast" and user.id == ADMIN_ID:
        context.user_data["broadcasting"] = True
        await update.message.reply_text("📢 मैसेज टाइप करें:", reply_markup=get_back_keyboard("Admin"))
    
    # 3. बाकी पुराना लॉजिक (Games, Plans, Admin Actions)
    elif text == "🎮 Games":
        await update.message.reply_text("🎮 Games List:", reply_markup=ReplyKeyboardMarkup([["👑 KING iOS"], ["WINIOS", "NEXT IOS"], ["𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"], ["DOLPHIN IOS"], ["🔙 Back to Main"]], resize_keyboard=True))
    
    # बाकी सारे Plans और बटन्स यहाँ वैसे ही लिखें जैसे आपके पास थे (मैंने कोड को छोटा रखने के लिए यहाँ स्किप किया है)
    # आप अपना पुराना 'elif' वाला पूरा हिस्सा यहाँ पेस्ट कर सकते हैं।
    else:
        await update.message.reply_text("चुनाव करें:", reply_markup=get_main_keyboard(user.id))

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
