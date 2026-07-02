import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import (create_tables, add_user, update_payment_status, save_key, 
                      get_stock, get_total_users, get_total_purchases, DB_NAME)
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
    context.user_data.clear()  
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text("👑 Welcome to KING iOS Bot\n\nSelect an option:", reply_markup=get_main_keyboard(user.id))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # Admin Logic with Plan Selection
    if user.id == ADMIN_ID:
        # --- ADD KEYS FLOW START ---
        if text == "🔑 Add Keys":
            context.user_data["adding_key"] = True
            await update.message.reply_text("🎯 Select the game:", reply_markup=admin_game_selection_keyboard())
            return

        # Game Selection Logic
        GAMES_LIST = ["👑 KING iOS", "WINIOS", "NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀", "DOLPHIN IOS"]
        if text in GAMES_LIST and context.user_data.get("adding_key"):
            context.user_data["selected_game"] = text
            plan_kb = ReplyKeyboardMarkup([["1 DAY", "1 WEEK", "1 MONTH"], ["🔙 Back to Admin"]], resize_keyboard=True)
            await update.message.reply_text(f"Selected: {text}\nअब प्लान चुनें:", reply_markup=plan_kb)
            context.user_data["selecting_plan"] = True
            return

        # Plan Selection Logic
        if context.user_data.get("selecting_plan") and text in ["1 DAY", "1 WEEK", "1 MONTH"]:
            context.user_data["selected_plan"] = text
            context.user_data["selecting_plan"] = False
            context.user_data["awaiting_key"] = True
            await update.message.reply_text(f"✅ Plan: {text}\n\nअब लाइसेंस की (Key) भेजें:", reply_markup=get_back_keyboard("Admin"))
            return

        # Key Saving Logic
        if context.user_data.get("awaiting_key"):
            save_key(context.user_data["selected_game"], text, context.user_data["selected_plan"])
            await update.message.reply_text(f"✅ Key added for {context.user_data['selected_game']} ({context.user_data['selected_plan']}). Send another:", reply_markup=get_back_keyboard("Admin"))
            return
        
        # --- OTHER ADMIN COMMANDS (Broadcast, Stock, etc.) ---
        # ... (आपका बाकी पुराना एडमिन लॉजिक यहाँ रहने दें)
        if text == "⚙️ Admin Panel":
            context.user_data.clear()
            await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
            return

    # User Logic remains same...
    # (यहाँ आपका पुराना 'CORE USER MENUS' वाला कोड पेस्ट कर दें)
    # ...

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    # ... (बाकी हैंडलर्स)
    app.run_polling()

if __name__ == "__main__":
    main()
