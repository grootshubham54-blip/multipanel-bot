import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, add_user, get_user_keys

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

async def start(update, context):
    add_user(update.effective_user.id, update.effective_user.username or "User")
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if update.effective_user.id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    state = context.user_data.get("state")

    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("Admin:", reply_markup=ReplyKeyboardMarkup([["🔑 Add Keys"], ["🔙 Back"]], resize_keyboard=True))
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "select_game"
            await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup([[g] for g in GAME_PLANS.keys()] + [["🔙 Back"]], resize_keyboard=True))
        elif state == "select_game" and text in GAME_PLANS:
            context.user_data.update({"add_game": text, "state": "select_plan"})
            await update.message.reply_text("Select Plan:", reply_markup=ReplyKeyboardMarkup([[p] for p in GAME_PLANS[text].keys()] + [["🔙 Back"]], resize_keyboard=True))
        elif state == "select_plan":
            context.user_data.update({"add_plan": text, "state": "add_keys"})
            await update.message.reply_text("Enter keys (one per line):")
        elif state == "add_keys":
            for k in text.split("\n"): save_key(context.user_data["add_game"], k.strip(), context.user_data["add_plan"])
            await update.message.reply_text("✅ Saved!")
            context.user_data.clear()
        elif text == "🔙 Back": context.user_data.clear(); await start(update, context)

    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif update.message.photo and user_id != ADMIN_ID:
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}")]]))
        await update.message.reply_text("✅ Screenshot sent!")

async def button_click(update, context):
    query = update.callback_query
    await query.answer() # फास्ट रिस्पॉन्स के लिए
    if query.data.startswith("game_"):
        game = query.data.split("_")[1]
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{game}_{p}")] for p, pr in GAME_PLANS[game].items()]
        await query.message.reply_text("Select Plan:", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data.startswith("acc_"):
        uid = query.data.split("_")[1]
        key = approve_and_assign_key(int(uid), "KING", "1 Day") # यहाँ गेम/प्लान लॉजिक डायनामिक रखें
        await query.edit_message_caption(f"✅ Approved. Key: {key}" if key else "⚠️ No keys!")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
