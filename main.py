import os
import logging
import sqlite3

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from database import (
    create_tables,
    add_user,
    update_payment_status,
    save_key,
    get_stock,
    get_total_users,
    get_total_purchases,
    DB_NAME
)

from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

GAME_MAPPING = {
    "👑 KING iOS": "king", "WINIOS": "win", "NEXT IOS": "next",
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "mars", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀": "dead", "DOLPHIN IOS": "dolphin"
}
REVERSE_GAME_MAPPING = {v: k for k, v in GAME_MAPPING.items()}

def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID: keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard(target: str = "Main") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[f"🔙 Back to {target}"]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text("👑 Welcome to KING iOS Bot\n\nSelect an option:", reply_markup=get_main_keyboard(user.id))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # BROADCAST LOGIC
    if context.user_data.get("broadcasting"):
        msg = text
        context.user_data["broadcasting"] = False
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        conn.close()
        for u in users:
            try: await context.bot.send_message(chat_id=u[0], text=f"📢 *Announcement:*\n\n{msg}", parse_mode="Markdown")
            except: continue
        await update.message.reply_text("✅ Announcement sent!", reply_markup=admin_keyboard())
        return

    # ADMIN ADD KEY LOGIC (WITH PLAN SELECTION)
    if user.id == ADMIN_ID and context.user_data.get("adding_key"):
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
            return
        
        # Step 1: Select Game
        if not context.user_data.get("selected_game"):
            context.user_data["selected_game"] = text
            await update.message.reply_text("🎯 Select Plan:", reply_markup=ReplyKeyboardMarkup([["1 DAY", "1 WEEK", "1 MONTH"], ["🔙 Back to Admin"]], resize_keyboard=True))
            return
        # Step 2: Select Plan
        elif not context.user_data.get("selected_plan"):
            context.user_data["selected_plan"] = text
            await update.message.reply_text("🔑 Now send the License Key:", reply_markup=get_back_keyboard("Admin"))
            return
        # Step 3: Save Key
        else:
            save_key(context.user_data["selected_game"], text, context.user_data["selected_plan"])
            await update.message.reply_text(f"✅ Key Added!\nGame: {context.user_data['selected_game']}\nPlan: {context.user_data['selected_plan']}\nKey: {text}", reply_markup=get_back_keyboard("Admin"))
            context.user_data.pop("adding_key", None)
            context.user_data.pop("selected_game", None)
            context.user_data.pop("selected_plan", None)
            return

    # NAVIGATION
    if text in ["🔙 Back to Main", "❌ Cancel Payment"]:
        context.user_data.clear()
        await update.message.reply_text("👑 Main Menu", reply_markup=get_main_keyboard(user.id))
        return

    if text == "🎮 Games":
        await update.message.reply_text("🎮 Games:", reply_markup=ReplyKeyboardMarkup([
            ["👑 KING iOS"], ["WINIOS", "NEXT IOS"], ["𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"], 
            ["DOLPHIN IOS", "ESING CERTIFICATE"], ["🔙 Back to Main"]
        ], resize_keyboard=True))
        return

    # ADMIN PANEL ROUTES
    if user.id == ADMIN_ID:
        if text == "⚙️ Admin Panel": await update.message.reply_text("👑 Admin Panel", reply_markup=admin_keyboard())
        elif text == "📢 Broadcast":
            context.user_data["broadcasting"] = True
            await update.message.reply_text("📢 Send announcement message:", reply_markup=get_back_keyboard("Admin"))
        elif text == "🔑 Add Keys":
            context.user_data["adding_key"] = True
            await update.message.reply_text("🎯 Select Game:", reply_markup=admin_game_selection_keyboard())
        
        # (बाकी एडमिन कमांड्स जैसे Stock, Statistics यहाँ रहने दें)

    # USER COMMANDS
    elif text == "ESING CERTIFICATE":
        await update.message.reply_text("📄 ESING CERTIFICATE section.")
    
    # [यहाँ अपने बाकी सारे पुराने elif plans पेस्ट करें]

# (अपनी photo_handler, payment_info, admin_action और main फंक्शन को यहाँ नीचे रखें)
