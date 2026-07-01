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

# --- KEYBOARDS ---
def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID: keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard(target: str = "Main") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[f"🔙 Back to {target}"]], resize_keyboard=True)

def get_payment_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["❌ Cancel Payment"]], resize_keyboard=True)

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text("👑 Welcome to KING iOS Bot\n\nSelect an option from below:", reply_markup=get_main_keyboard(user.id))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # 1. BROADCAST LOGIC (नया फीचर)
    if context.user_data.get("broadcasting"):
        msg_to_send = text
        context.user_data["broadcasting"] = False
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        conn.close()
        count = 0
        for u in users:
            try:
                await context.bot.send_message(chat_id=u[0], text=f"📢 *Announcement:*\n\n{msg_to_send}", parse_mode="Markdown")
                count += 1
            except: continue
        await update.message.reply_text(f"✅ Announcement sent to {count} users!", reply_markup=admin_keyboard())
        return

    # 2. NAVIGATION
    if text in ["🔙 Back to Main", "❌ Cancel Payment"]:
        context.user_data.clear()
        await update.message.reply_text("👑 Main Menu", reply_markup=get_main_keyboard(user.id))
        return

    # 3. ADMIN SECTION
    if user.id == ADMIN_ID:
        if text == "⚙️ Admin Panel":
            context.user_data.clear()
            await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
            return
        elif text == "📢 Broadcast":
            context.user_data["broadcasting"] = True
            await update.message.reply_text("📢 Send your announcement message now:", reply_markup=get_back_keyboard("Admin"))
            return
        # (आपका पुराना एडमिन लॉजिक यहाँ जारी रहेगा - Add Keys, Stock, etc.)
        # ... बाकी एडमिन लॉजिक ...

    # 4. USER MENU & GAMES (आपका पुराना लॉजिक यहाँ आएगा)
    # ... Games, Plans, Payment Info, Photo Handler etc ...
    # (आप अपना पुराना लॉजिक यहाँ जस का तस पेस्ट करें)

# बाकी functions: payment_info, photo_handler, admin_action, main वैसे ही रहने दें

