import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)

# Make sure 'BOT_TOKEN' is set in your Railway variables
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593
PAYMENT_QR_FILE_ID = "YOUR_QR_PHOTO_FILE_ID" # Replace with your actual file_id

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

async def start(update, context):
    save_user(update.effective_user.id, update.effective_user.username)
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if update.effective_user.id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome! Select an option:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("game_"):
        game = data.split("_")[1]
        context.user_data["game"] = game
        msg = f"🎮 Selected: {game}\n\n*Available Plans:*\n"
        kb = []
        for p, price in GAME_PLANS[game].items():
            stock = get_stock_count(game, p)
            msg += f"- {p} ({price}₹): {stock} available\n"
            if stock > 0: kb.append([InlineKeyboardButton(f"{p} ({price}₹)", callback_data=f"plan_{p}")])
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("plan_"):
        plan = data.split("_")[1]
        context.user_data["plan"] = plan
        await context.bot.send_photo(chat_id=query.from_user.id, photo=PAYMENT_QR_FILE_ID, caption=f"Pay for {plan} and send screenshot.")

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Choose a game:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif update.message.photo and "game" in context.user_data:
        g, p = context.user_data["game"], context.user_data["plan"]
        kb = [[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}\nGame: {g}\nPlan: {p}", reply_markup=InlineKeyboardMarkup(kb))
        await update.message.reply_text("✅ Screenshot sent to Admin!")

if __name__ == '__main__':
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.run_polling()
