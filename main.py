import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import (create_tables, add_user, update_payment_status, save_key, get_stock, get_total_users, get_total_purchases, DB_NAME)
from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0)) 

GAME_MAPPING = {"👑 KING iOS": "king", "WINIOS": "win", "NEXT IOS": "next", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "mars", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀": "dead", "DOLPHIN IOS": "dolphin"}
REVERSE_GAME_MAPPING = {v: k for k, v in GAME_MAPPING.items()}

def get_main_keyboard(user_id):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID: keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard(target="Main"):
    return ReplyKeyboardMarkup([[f"🔙 Back to {target}"]], resize_keyboard=True)

async def start(update, context):
    add_user(update.effective_user.id, update.effective_user.username)
    await update.message.reply_text("👑 Welcome!", reply_markup=get_main_keyboard(update.effective_user.id))

async def message_handler(update, context):
    text = update.message.text
    user = update.effective_user

    # --- NEW KEY ADD LOGIC ---
    if user.id == ADMIN_ID and context.user_data.get("adding_key"):
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("👑 Admin Panel", reply_markup=admin_keyboard())
            return
        if not context.user_data.get("selected_game"):
            context.user_data["selected_game"] = text
            await update.message.reply_text("Select Plan:", reply_markup=ReplyKeyboardMarkup([["1 DAY", "1 WEEK", "1 MONTH"]], resize_keyboard=True))
            return
        elif not context.user_data.get("selected_plan"):
            context.user_data["selected_plan"] = text
            await update.message.reply_text("Send Key:", reply_markup=get_back_keyboard("Admin"))
            return
        else:
            save_key(context.user_data["selected_game"], text, context.user_data["selected_plan"])
            await update.message.reply_text("✅ Added!", reply_markup=get_back_keyboard("Admin"))
            return

    # --- OLD NAVIGATION LOGIC (सब बटन वापस आ गए) ---
    if text == "🎮 Games":
        await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup([["👑 KING iOS"], ["WINIOS", "NEXT IOS"], ["𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"], ["DOLPHIN IOS"], ["🔙 Back to Main"]], resize_keyboard=True))
    elif text == "🔙 Back to Main":
        await update.message.reply_text("Main Menu", reply_markup=get_main_keyboard(user.id))
    elif user.id == ADMIN_ID:
        if text == "⚙️ Admin Panel": await update.message.reply_text("Admin Panel", reply_markup=admin_keyboard())
        elif text == "🔑 Add Keys":
            context.user_data["adding_key"] = True
            await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard())
    # यहाँ आप अपने बाकी पुराने 'elif' (जैसे WINIOS, NEXT IOS, SUPPORT) वैसे ही पेस्ट करें...
    else:
        await update.message.reply_text("Invalid selection.")

# यहाँ अपने पुराने payment_info, photo_handler, admin_action और main फंक्शन रख दें
