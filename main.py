import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, add_user, get_user_keys, save_pending_payment, approve_and_assign_key
from admin_panel import admin_keyboard, admin_game_selection_keyboard

TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_ID = 7908981593

def get_main_keyboard(user_id):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id, update.effective_user.username)
    await update.message.reply_text("👋 Welcome!", reply_markup=get_main_keyboard(update.effective_user.id))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = update.effective_user.id
    
    if text == "🎮 Games":
        await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
    elif text == "🔑 My Keys":
        keys = get_user_keys(uid)
        msg = "\n".join([f"🎮 {k[0]} ({k[1]}) -> `{k[2]}`" for k in keys]) if keys else "❌ No keys found."
        await update.message.reply_text(msg, parse_mode="Markdown")
    elif text == "📞 Support":
        await update.message.reply_text("📞 Contact @YourSupport")
    elif text == "💳 Payment":
        await update.message.reply_text("💳 Please choose a game first.")
    elif text == "🛠 Admin Panel" and uid == ADMIN_ID:
        await update.message.reply_text("Admin:", reply_markup=admin_keyboard())
    else:
        await update.message.reply_text("Menu:", reply_markup=get_main_keyboard(uid))

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
