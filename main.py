Import os
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
    "👑 KING iOS": "king",
    "WINIOS": "win",
    "NEXT IOS": "next",
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "mars",
    "𝘿𝙀𝘼𝘿𝙀𝙔𝙀": "dead",
    "DOLPHIN IOS": "dolphin"
}
REVERSE_GAME_MAPPING = {v: k for k, v in GAME_MAPPING.items()}

# Keyboard Markups
def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [
        ["🎮 Games", "🔑 My Keys"],
        ["📞 Support", "👤 Profile"],
        ["💳 Payment"]
    ]
    if user_id == ADMIN_ID:
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard(target: str = "Main") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[f"🔙 Back to {target}"]], resize_keyboard=True)

def get_payment_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["❌ Cancel Payment"]], resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()  
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text("👑 Welcome to KING iOS Bot\n\nSelect an option from below:", reply_markup=get_main_keyboard(user.id))


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # --- ADD KEY LOGIC (PLAN SELECTION ADDED) ---
    if user.id == ADMIN_ID and context.user_data.get("adding_key"):
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
            return
        
        # 1. गेम चुना
        if not context.user_data.get("selected_game"):
            context.user_data["selected_game"] = text
            await update.message.reply_text(f"🎯 Selected: {text}\nअब प्लान चुनें:", reply_markup=ReplyKeyboardMarkup([["1 DAY", "1 WEEK", "1 MONTH"], ["🔙 Back to Admin"]], resize_keyboard=True))
            return
        # 2. प्लान चुना
        elif not context.user_data.get("selected_plan"):
            context.user_data["selected_plan"] = text
            await update.message.reply_text(f"📋 Plan: {text}\nअब Key भेजें:", reply_markup=get_back_keyboard("Admin"))
            return
        # 3. Key सेव की
        else:
            save_key(context.user_data["selected_game"], text, context.user_data["selected_plan"])
            await update.message.reply_text(f"✅ Key Added for {context.user_data['selected_game']} ({context.user_data['selected_plan']}).\nSend next key or Back to Admin.", reply_markup=get_back_keyboard("Admin"))
            return

    # --- ADMIN ROUTES ---
    if user.id == ADMIN_ID:
        if text == "⚙️ Admin Panel":
            context.user_data.clear()
            await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
            return
        if text == "🔑 Add Keys":
            context.user_data["adding_key"] = True
            await update.message.reply_text("🎯 Select game:", reply_markup=admin_game_selection_keyboard())
            return
    
    # --- बाकी का आपका वही पुराना कोड (Navigation, Games, Plans, आदि) ---
    # यहाँ अपना सारा पुराना Logic (if text == "🎮 Games" ..., elif text == "👑 KING iOS" ...) पेस्ट कर दें।
    # (मैंने आपकी फाइल को छोटा रखने के लिए यहाँ का हिस्सा हटा दिया है, 
    # बस अपना पुराना कोड यहाँ चिपका दें, सब सही चलेगा)

# --- (फोटो हैंडलर, पेमेंट और मेन फंक्शन भी यहीं रहने दें) ---