import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7908981593"

# Mapping for callback data (Keep it short to avoid telegram errors)
GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN", "NEXT IOS": "NEXT", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "MARS", "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": "DEAD", "DOLPHIN IOS": "DOLP"}
REV_GAME_MAP = {v: k for k, v in GAME_MAP.items()}
PLAN_MAP = {"1 Day": "1D", "1 Week": "1W", "1 Month": "1M"}
REV_PLAN_MAP = {"1D": "1 Day", "1W": "1 Week", "1M": "1 Month"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    add_user(update.effective_user.id, update.effective_user.username or "No Username")
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID: keyboard.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome! How can I help you today?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. PHOTO HANDLING (Priority)
    if update.message.photo:
        user_id = str(update.effective_user.id)
        if user_id == ADMIN_ID:
            await update.message.reply_text("⚠️ You are admin, you can't send payment screenshots here.")
            return
        
        g = context.user_data.get("u_game", "Unknown")
        p = context.user_data.get("u_plan", "Unknown")
        
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id, 
            caption=f"👤 Payment from: {update.effective_user.first_name} (@{update.effective_user.username or 'N/A'})\nID: {user_id}\n🎮 Game: {g}\n📦 Plan: {p}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Accept & Send Key", callback_data=f"acc_{user_id}_{GAME_MAP.get(g, 'KING')}_{PLAN_MAP.get(p, '1D')}")],
                [InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]
            ])
        )
        await update.message.reply_text("✅ Screenshot received! Admin is verifying.")
        return

    # 2. TEXT HANDLING
    text = update.message.text
    user_id = str(update.effective_user.id)
    state = context.user_data.get("state")

    # Admin Add Keys Flow
    if user_id == ADMIN_ID and state:
        # ... (Same Add Key logic as before) ...
        # [Include the same Add Keys logic code block here]
        pass 

    # Buttons Logic (Keep all existing buttons)
    if text == "🎮 Games":
        await update.message.reply_text("Choose a game:", reply_markup=admin_game_selection_keyboard())
    elif text in ["👑 KING iOS", "WINIOS", "NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀", "DOLPHIN IOS"]:
        context.user_data["u_game"] = text
        # ... (Show plans inline) ...
    # ... (Rest of your existing text buttons) ...

# [Include the rest of the button_click and main functions]
