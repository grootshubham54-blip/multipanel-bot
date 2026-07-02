import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)
from database import create_tables, save_key, get_stock, get_total_users
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "YOUR_ADMIN_ID_HERE"  # यहाँ अपनी Telegram ID डालें

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    await update.message.reply_text("👋 Welcome to the Bot!", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) == ADMIN_ID:
        await update.message.reply_text("🛠 Admin Panel Activated:", reply_markup=admin_keyboard())
    else:
        await update.message.reply_text("🚫 You are not authorized!")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Admin Navigation
    if str(update.effective_user.id) == ADMIN_ID:
        if text == "🔑 Add Keys":
            await update.message.reply_text("🎮 Select Game to add keys:", reply_markup=admin_game_selection_keyboard())
            return
        elif text == "🔙 Back to Admin":
            await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "🔙 Back to Main":
            await start(update, context)
        elif text == "📦 Stock":
            count = get_stock("ALL", "ALL") # यह फंक्शन आप बाद में और कस्टमाइज कर सकते हैं
            await update.message.reply_text(f"📦 Total Keys in Stock: {count}")
        elif text == "👥 Total Users":
            users = get_total_users()
            await update.message.reply_text(f"👥 Total registered users: {users}")

    # User Navigation
    if text == "🎮 Games":
        await update.message.reply_text("Select a game:", reply_markup=admin_game_selection_keyboard())
    elif text == "🔑 My Keys":
        await update.message.reply_text("Your keys will appear here.")
    else:
        await start(update, context)

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
