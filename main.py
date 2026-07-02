import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    ContextTypes, filters
)
from database import create_tables, get_stock, get_total_users
from admin_panel import admin_keyboard, admin_game_selection_keyboard

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "YOUR_ADMIN_ID_HERE" # यहाँ अपनी Telegram ID डालना न भूलें

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    # अगर यूजर एडमिन है, तो एडमिन का बटन भी दिखाओ
    if user_id == ADMIN_ID:
        keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"], ["🛠 Admin Panel"]]
    else:
        keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
        
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) == ADMIN_ID:
        await update.message.reply_text("🛠 Admin Panel Activated:", reply_markup=admin_keyboard())
    else:
        await update.message.reply_text("🚫 Access Denied!")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)

    # 1. एडमिन बटन चेक
    if text == "🛠 Admin Panel" and user_id == ADMIN_ID:
        await admin_panel(update, context)
        return

    # 2. एडमिन कीबोर्ड के बटन
    if user_id == ADMIN_ID:
        if text == "🔑 Add Keys":
            await update.message.reply_text("🎮 Select Game:", reply_markup=admin_game_selection_keyboard())
            return
        elif text == "📦 Stock":
            await update.message.reply_text(f"📦 Total Stock: {get_stock('ALL', 'ALL')}")
            return
        elif text == "🔙 Back to Main":
            await start(update, context)
            return

    # 3. यूजर नेविगेशन
    if text == "🎮 Games":
        await update.message.reply_text("Select a game:", reply_markup=admin_game_selection_keyboard())
    elif text in ["👑 KING iOS", "WINIOS", "NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙀𝙔𝙀", "DOLPHIN IOS"]:
        await update.message.reply_text(f"You selected {text}. Please choose a plan.")
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
