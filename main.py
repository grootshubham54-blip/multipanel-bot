import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from database import *

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

# KEYBOARDS
def main_kb(uid):
    kb = [["🎮 Games", "🔑 My Keys"], ["💳 Payment"]]
    if uid == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def admin_kb():
    return ReplyKeyboardMarkup([["🔑 Add Keys", "📊 Stock"], ["📊 Sales Dashboard", "👥 Total Users"], ["🔙 Back"]], resize_keyboard=True)

async def start(update, context):
    await update.message.reply_text("Welcome to Store!", reply_markup=main_kb(update.effective_user.id))

async def msg_handler(update, context):
    text = update.message.text
    uid = update.effective_user.id
    
    if text == "🔙 Back": await start(update, context)
    elif text == "🛠 Admin Panel" and uid == ADMIN_ID: await update.message.reply_text("Admin Panel:", reply_markup=admin_kb())
    elif text == "📊 Sales Dashboard" and uid == ADMIN_ID: await update.message.reply_text(f"📊 Sold: {get_sold_keys_count()}")
    elif text == "👥 Total Users" and uid == ADMIN_ID: await update.message.reply_text(f"👥 Users: {get_total_users()}")
    elif text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select:", reply_markup=InlineKeyboardMarkup(kb))

async def btn_handler(update, context):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("game_"):
        game = query.data.split("_")[1]
        kb = [[InlineKeyboardButton(p, callback_data=f"pay_{p}")] for p in GAME_PLANS[game].keys()]
        await query.edit_message_text(f"Select plan:", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data.startswith("pay_"):
        await query.message.reply_text("Pay to QR and send screenshot.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, msg_handler))
    app.add_handler(CallbackQueryHandler(btn_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
