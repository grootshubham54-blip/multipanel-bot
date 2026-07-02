import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, add_user, save_pending_payment, approve_and_assign_key, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# 1. अपना टोकन यहाँ बदलें
TOKEN = "अपने_बोट_का_टोकन_यहाँ_डालें"
ADMIN_ID = 7908981593

# 2. मेन कीबोर्ड
def get_main_keyboard(user_id):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# 3. स्टार्ट कमांड
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id, update.effective_user.username or "User")
    await update.message.reply_text("👋 Welcome to the Bot!", reply_markup=get_main_keyboard(user_id))

# 4. मैसेज हैंडलर (बटन्स के लिए)
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    user_id = update.effective_user.id
    
    if text == "🎮 Games":
        await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
    elif text == "🔑 My Keys":
        keys = get_user_keys(user_id)
        msg = "\n".join([f"🎮 {k[0]} | {k[1]} | Key: `{k[2]}`" for k in keys]) if keys else "❌ No keys found."
        await update.message.reply_text(f"Your Keys:\n{msg}", parse_mode="Markdown")
    elif text == "📞 Support":
        await update.message.reply_text("📞 Contact: @YourSupportUsername")
    elif text == "💳 Payment":
        await update.message.reply_text("💳 Choose a game from 'Games' menu first.")
    elif text == "🛠 Admin Panel" and user_id == ADMIN_ID:
        await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
    elif text == "🔙 Back to Admin":
        await update.message.reply_text("Back to menu:", reply_markup=get_main_keyboard(user_id))
    else:
        await update.message.reply_text("Welcome!", reply_markup=get_main_keyboard(user_id))

# 5. बोट सेटअप
def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
