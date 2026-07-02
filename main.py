import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from database import (create_tables, add_user, update_payment_status, save_key, 
                      get_stock, get_total_users, get_total_purchases, DB_NAME)
from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0)) 

# Keyboard Helpers
def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID: keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard(target: str = "Main"): return ReplyKeyboardMarkup([[f"🔙 Back to {target}"]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text("👑 Welcome!", reply_markup=get_main_keyboard(user.id))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # --- 1. ADMIN LOGIC ---
    if user.id == ADMIN_ID:
        # Add Key Flow
        if text == "🔑 Add Keys":
            context.user_data.update({"adding_key": True})
            await update.message.reply_text("🎯 Select game:", reply_markup=admin_game_selection_keyboard())
            return
        
        if context.user_data.get("adding_key"):
            if text in ["👑 KING iOS", "WINIOS", "NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀", "DOLPHIN IOS"]:
                context.user_data["selected_game"] = text
                await update.message.reply_text("Select Plan:", reply_markup=ReplyKeyboardMarkup([["1 DAY", "1 WEEK", "1 MONTH"]], resize_keyboard=True))
                return
            elif text in ["1 DAY", "1 WEEK", "1 MONTH"]:
                context.user_data["selected_plan"] = text
                await update.message.reply_text("Send Key:", reply_markup=get_back_keyboard("Admin"))
                return
            elif text != "🔙 Back to Admin":
                save_key(context.user_data["selected_game"], text, context.user_data["selected_plan"])
                await update.message.reply_text("✅ Key saved! Send another or Back.", reply_markup=get_back_keyboard("Admin"))
                return

        # Regular Admin Buttons
        if text == "⚙️ Admin Panel":
            await update.message.reply_text("👑 Admin Panel", reply_markup=admin_keyboard())
            return
        elif text == "👥 Total Users":
            await update.message.reply_text(f"Users: {get_total_users()}")
            return
        # (यहाँ आप अपने अन्य पुराने एडमिन बटन भी जोड़ सकते हैं)

    # --- 2. USER LOGIC ---
    if text == "🎮 Games":
        await update.message.reply_text("🎮 Games:", reply_markup=ReplyKeyboardMarkup([["👑 KING iOS"], ["WINIOS"], ["🔙 Back to Main"]], resize_keyboard=True))
    elif text == "🔙 Back to Main":
        context.user_data.clear()
        await update.message.reply_text("Main Menu", reply_markup=get_main_keyboard(user.id))
    # (यहाँ अपना पुराना यूजर वाला सारा elif कोड लगा दें)

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
