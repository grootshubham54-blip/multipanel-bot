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
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0)) 

GAME_MAPPING = {
    "👑 KING iOS": "king", "WINIOS": "win", "NEXT IOS": "next",
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "mars", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀": "dead", "DOLPHIN IOS": "dolphin"
}
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()  
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text("👑 Welcome to KING iOS Bot\n\nSelect an option:", reply_markup=get_main_keyboard(user.id))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # --- 1. BROADCAST LOGIC (यहाँ जोड़ा गया है) ---
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
            try: await context.bot.send_message(chat_id=u[0], text=f"📢 *Announcement:*\n\n{msg_to_send}", parse_mode="Markdown")
            except: continue
        await update.message.reply_text(f"✅ Announcement sent to {count} users!", reply_markup=admin_keyboard())
        return

    # --- 2. NAVIGATION ---
    if text in ["🔙 Back to Main", "❌ Cancel Payment"]:
        context.user_data.clear()
        await update.message.reply_text("👑 Main Menu", reply_markup=get_main_keyboard(user.id))
        return

    if text == "🔙 Back to Admin":
        context.user_data.update({"adding_key": False, "checking_stock": False, "selected_game": None})
        await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
        return

    if text == "🔙 Back to Games":
        await update.message.reply_text("🎮 Games:", reply_markup=ReplyKeyboardMarkup([["👑 KING iOS"], ["WINIOS", "NEXT IOS"], ["𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"], ["DOLPHIN IOS"], ["🔙 Back to Main"]], resize_keyboard=True))
        return

    # --- 3. ADMIN ROUTES ---
    if user.id == ADMIN_ID:
        if text == "⚙️ Admin Panel":
            context.user_data.clear()
            await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
            return
        elif text == "📢 Broadcast":
            context.user_data["broadcasting"] = True
            await update.message.reply_text("📢 Send announcement message:", reply_markup=get_back_keyboard("Admin"))
            return
        elif text == "🔑 Add Keys":
            context.user_data.update({"adding_key": True, "checking_stock": False})
            await update.message.reply_text("🎯 Select game for keys:", reply_markup=admin_game_selection_keyboard())
            return
        elif text == "📦 Stock":
            context.user_data.update({"checking_stock": True, "adding_key": False})
            await update.message.reply_text("🎯 Select game to check stock:", reply_markup=admin_game_selection_keyboard())
            return
        elif text in ["👑 KING iOS", "WINIOS", "NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀", "DOLPHIN IOS"]:
            if context.user_data.get("adding_key"):
                context.user_data["selected_game"] = text
                await update.message.reply_text(f"🔑 Typing keys for [{text}]. Send key:", reply_markup=get_back_keyboard("Admin"))
                return
            elif context.user_data.get("checking_stock"):
                await update.message.reply_text(f"📦 Stock for *{text}*: `{get_stock(text)}`", parse_mode="Markdown", reply_markup=admin_game_selection_keyboard())
                return
        if context.user_data.get("adding_key") and context.user_data.get("selected_game"):
            save_key(context.user_data["selected_game"], text)
            await update.message.reply_text(f"✅ Key added! Send next or Back to Admin.", reply_markup=get_back_keyboard("Admin"))
            return
        elif text == "👥 Total Users": await update.message.reply_text(f"👥 Users: {get_total_users()}")
        elif text == "💰 Purchases": await update.message.reply_text(f"💰 Purchases: {get_total_purchases()}")
        elif text == "📊 Statistics":
            await update.message.reply_text(f"📊 Stats\nUsers: {get_total_users()}\nStock: {get_stock()}\nSales: {get_total_purchases()}", parse_mode="Markdown")
            return

    # --- 4. GAMES AND PLANS ---
    if text == "🎮 Games":
        await update.message.reply_text("🎮 Select Game:", reply_markup=ReplyKeyboardMarkup([["👑 KING iOS"], ["WINIOS", "NEXT IOS"], ["𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"], ["DOLPHIN IOS"], ["🔙 Back to Main"]], resize_keyboard=True))
    elif text == "👑 KING iOS":
        await update.message.reply_text("👑 KING iOS Plans:", reply_markup=ReplyKeyboardMarkup([["👑 KING iOS 1 DAY - ₹200"], ["👑 KING iOS 1 WEEK - ₹800"], ["👑 KING iOS 1 MONTH - ₹2000"], ["🔙 Back to Games"]], resize_keyboard=True))
    elif "KING iOS" in text and "₹" in text:
        context.user_data.update({"base_game": "👑 KING iOS", "plan": text.split(" - ")[0], "amount": text.split("₹")[1], "awaiting_screenshot": True})
        await payment_info(update, context)
    # (बाकी गेम्स का लॉजिक भी ऐसे ही जुड़ा रहेगा...)

    # आप अपना बाकी का पुराना प्लान वाला लॉजिक यहाँ वैसे ही रहने दें, मैंने यहाँ सिर्फ KING का दिखाया है।

# (बाकी का payment_info, photo_handler, admin_action और main फंक्शन जैसा है वैसा ही रखें)
