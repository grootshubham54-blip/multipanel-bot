import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, add_user, save_pending_payment, approve_and_assign_key, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593

def get_main_keyboard(user_id):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id, update.effective_user.username or "No Username")
    await update.message.reply_text("👋 Welcome!", reply_markup=get_main_keyboard(user_id))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("u_game", "Unknown")
        p = context.user_data.get("u_plan", "Unknown")
        pay_id = save_pending_payment(user_id, g, p, update.message.photo[-1].file_id)
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, 
            caption=f"👤 Payment from {user_id}\n🎮 {g} - {p}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve", callback_data=f"acc_{pay_id}")]]))
        await update.message.reply_text("✅ Payment sent!")
        return

    # बटन्स का लॉजिक (नामों की स्पेलिंग पर ध्यान दें)
    if text == "🎮 Games":
        await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
    elif text == "🔑 My Keys":
        keys = get_user_keys(user_id)
        msg = "\n".join([f"🎮 {k[0]} | {k[1]} | Key: `{k[2]}`" for k in keys]) if keys else "❌ No keys found."
        await update.message.reply_text(f"Your Keys:\n{msg}", parse_mode="Markdown")
    elif text == "📞 Support":
        await update.message.reply_text("📞 Contact: @YourSupport")
    elif text == "💳 Payment":
        await update.message.reply_text("💳 Please select a game first.")
    elif text == "🛠 Admin Panel" and user_id == ADMIN_ID:
        await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
    elif text == "🔑 Add Keys" and user_id == ADMIN_ID:
        await update.message.reply_text("Send keys: Game|Plan|Key")
    elif text == "📦 Stock" and user_id == ADMIN_ID:
        await update.message.reply_text("📊 Checking stock...")
    elif text == "👥 Total Users" and user_id == ADMIN_ID:
        await update.message.reply_text("👥 Total users: Calculating...")
    elif text == "🔙 Back to Admin":
        await update.message.reply_text("Main menu:", reply_markup=get_main_keyboard(user_id))
    else:
        # अगर कोई बटन मैच न हो
        await update.message.reply_text("Welcome back!", reply_markup=get_main_keyboard(user_id))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("plan|"):
        context.user_data["u_plan"] = query.data.split("|")[1]
        await query.message.reply_text("Send payment screenshot.")
    elif query.data.startswith("acc_"):
        pay_id = int(query.data.split("_")[1])
        key, uid = approve_and_assign_key(pay_id)
        if key:
            await context.bot.send_message(uid, f"✅ Key: `{key}`")
            await query.edit_message_caption(caption="✅ Approved.")
        else: await query.edit_message_caption(caption="❌ No stock.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
