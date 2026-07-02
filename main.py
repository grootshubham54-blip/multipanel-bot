import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, get_user_keys, add_user
from admin_panel import admin_keyboard, admin_game_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593

# मेन कीबोर्ड
def get_main_keyboard(user_id):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id, update.effective_user.username or "User")
    await update.message.reply_text("👋 Welcome!", reply_markup=get_main_keyboard(user_id))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    # बटन्स लॉजिक
    if text == "🎮 Games":
        await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
    elif text == "🔑 My Keys":
        keys = get_user_keys(user_id)
        msg = "\n".join([f"🎮 {k[0]} - {k[2]}" for k in keys]) if keys else "No keys."
        await update.message.reply_text(f"Your Keys:\n{msg}")
    elif text == "📞 Support":
        await update.message.reply_text("Contact: @Support")
    elif text == "💳 Payment":
        await update.message.reply_text("Send payment.")
    elif text == "🛠 Admin Panel" and user_id == ADMIN_ID:
        await update.message.reply_text("Admin:", reply_markup=admin_keyboard())
    else:
        await update.message.reply_text("Welcome!", reply_markup=get_main_keyboard(user_id))

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # TEXT हैंडलर को सबसे ऊपर रखें
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
