import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from database import (create_tables, add_user, update_payment_status, save_key, get_stock, get_total_users, get_total_purchases, DB_NAME)
from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# --- KEYBOARDS ---
def get_main_keyboard(user_id):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID: keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard(target="Main"):
    return ReplyKeyboardMarkup([[f"🔙 Back to {target}"]], resize_keyboard=True)

def get_payment_keyboard():
    return ReplyKeyboardMarkup([["❌ Cancel Payment"]], resize_keyboard=True)

# --- HANDLERS ---
async def start(update, context):
    user = update.effective_user
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text("👑 Welcome to KING iOS Bot", reply_markup=get_main_keyboard(user.id))

async def message_handler(update, context):
    text = update.message.text
    user = update.effective_user

    # 1. ADMIN ADD KEY LOGIC
    if user.id == ADMIN_ID and context.user_data.get("adding_key"):
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("👑 Admin Panel", reply_markup=admin_keyboard())
            return
        if not context.user_data.get("selected_game"):
            context.user_data["selected_game"] = text
            await update.message.reply_text("🎯 Select Plan:", reply_markup=ReplyKeyboardMarkup([["1 DAY", "1 WEEK", "1 MONTH"], ["🔙 Back to Admin"]], resize_keyboard=True))
            return
        elif not context.user_data.get("selected_plan"):
            context.user_data["selected_plan"] = text
            await update.message.reply_text(f"🔑 Game: {context.user_data['selected_game']} | Plan: {text}\nNow send the KEY:", reply_markup=get_back_keyboard("Admin"))
            return
        else:
            save_key(context.user_data["selected_game"], text, context.user_data["selected_plan"])
            await update.message.reply_text(f"✅ Key Added!\nSend next key or Back to Admin.", reply_markup=get_back_keyboard("Admin"))
            return

    # 2. USER & ADMIN NAVIGATION
    if text == "🎮 Games":
        await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup([["👑 KING iOS"], ["WINIOS", "NEXT IOS"], ["𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"], ["DOLPHIN IOS"], ["🔙 Back to Main"]], resize_keyboard=True))
    elif text == "🔙 Back to Main" or text == "❌ Cancel Payment":
        context.user_data.clear()
        await update.message.reply_text("👑 Main Menu", reply_markup=get_main_keyboard(user.id))
    
    # ADMIN PANEL NAVIGATION
    elif user.id == ADMIN_ID:
        if text == "⚙️ Admin Panel": await update.message.reply_text("👑 Admin Panel", reply_markup=admin_keyboard())
        elif text == "🔑 Add Keys":
            context.user_data["adding_key"] = True
            await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard())
        elif text == "👥 Total Users": await update.message.reply_text(f"Total Users: {get_total_users()}")
        # [यहाँ अपने बाकी पुराने elif जैसे 👑 KING iOS, WINIOS आदि पेस्ट कर दें]
    
    else:
        await update.message.reply_text("Please use the menu buttons.")

# --- MAIN RUNNER ---
def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()