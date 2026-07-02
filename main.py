import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, approve_and_assign_key
from admin_panel import admin_keyboard, admin_game_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7908981593"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)

    # 1. फोटो हैंडलिंग (पेमेंट)
    if update.message.photo:
        if user_id != ADMIN_ID:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, 
                caption=f"👤 Payment from {user_id}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve", callback_data=f"acc_{user_id}"), 
                                                   InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]))
            await update.message.reply_text("✅ Screenshot sent to Admin.")
        return

    # 2. एडमिन बटन्स
    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel":
            await update.message.reply_text("🛠 Admin Panel:", reply_markup=admin_keyboard())
            return
        elif text in ["🔑 Add Keys", "📦 Stock", "📢 Broadcast", "👥 Total Users", "📊 Statistics"]:
            await update.message.reply_text(f"Admin menu: {text} (Feature ready to code!)")
            return
        elif text == "🔙 Back to Main":
            await start(update, context)
            return

    # 3. यूजर बटन्स
    if text == "🎮 Games":
        await update.message.reply_text("Choose a game:", reply_markup=admin_game_selection_keyboard())
    elif text == "🔑 My Keys":
        await update.message.reply_text("Your keys: None")
    elif text == "📞 Support":
        await update.message.reply_text("Contact: @IOS_HACK_S")
    elif text == "💳 Payment":
        await update.message.reply_text("Send screenshot to pay.")
    else:
        await start(update, context)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("acc_"):
        uid = query.data.split("_")[1]
        key = approve_and_assign_key(uid, "👑 KING iOS", "1 Day")
        await context.bot.send_message(uid, f"✅ Payment Approved! Key: {key}")
        await query.edit_message_caption("✅ Approved.")
    elif query.data.startswith("rej_"):
        uid = query.data.split("_")[1]
        await context.bot.send_message(uid, "❌ Rejected.")
        await query.edit_message_caption("❌ Rejected.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
