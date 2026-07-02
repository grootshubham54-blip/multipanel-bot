import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7908981593"

GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN", "NEXT IOS": "NEXT", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "MARS", "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": "DEAD", "DOLPHIN IOS": "DOLP"}
REV_GAME_MAP = {v: k for k, v in GAME_MAP.items()}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id, update.effective_user.username or "User")
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if str(update.effective_user.id) == ADMIN_ID: keyboard.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    # 1. Payment Screenshot
    if update.message.photo and user_id != ADMIN_ID:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, 
            caption=f"Payment from {user_id}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}"), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]))
        await update.message.reply_text("✅ Screenshot received!")
        return

    # 2. Customer Buttons
    if text == "🎮 Games":
        await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_MAP:
        context.user_data["u_game"] = text
        await update.message.reply_text("Choose plan:", reply_markup=admin_plan_selection_keyboard())
    
    # 3. Admin Buttons (Matching your admin_panel.py)
    elif user_id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("Panel:", reply_markup=admin_keyboard())
        elif text == "🔑 Add Keys": 
            context.user_data["state"] = "awaiting_game"
            await update.message.reply_text("Choose game:", reply_markup=admin_game_selection_keyboard())
        elif text == "📦 Stock": await update.message.reply_text("Checking stock...")
        elif text == "🔙 Back to Admin": await update.message.reply_text("Panel:", reply_markup=admin_keyboard())
        elif text == "🔙 Back to Main": await start(update, context)
        # Add logic for Broadcast, Total Users, Statistics here...

    else: await start(update, context)

# Button click remains similar, just ensure 'acc_' and 'rej_' match
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("acc_"):
        await context.bot.send_message(query.data.split("_")[1], "✅ Payment Approved!")
        await query.edit_message_caption(caption="✅ Approved.")
    elif query.data.startswith("rej_"):
        await context.bot.send_message(query.data.split("_")[1], "❌ Rejected.")
        await query.edit_message_caption(caption="❌ Rejected.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
