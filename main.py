import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, add_user, get_user_keys

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593

# आपकी पूरी पुरानी लिस्ट (कुछ रिमूव नहीं किया है)
GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}
GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN", "NEXT IOS": "NEXT", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "MARS", "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": "DEAD", "DOLPHIN IOS": "DOLP"}

async def start(update, context):
    add_user(update.effective_user.id, update.effective_user.username or "User")
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if update.effective_user.id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    # 1. एडमिन पैनल
    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("Admin:", reply_markup=ReplyKeyboardMarkup([["🔑 Add Keys", "📦 Stock"], ["🔙 Back"]], resize_keyboard=True))
        elif text == "🔙 Back": await start(update, context)
        elif text == "🔑 Add Keys": await update.message.reply_text("Enter Game Name:")
    
    # 2. यूजर फ्लो (Games Button)
    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    
    # 3. पेमेंट स्क्रीनशॉट हैंडलर (एक्सेप्ट/रिजेक्ट बटन के साथ)
    elif update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("sel_game", "KING")
        p = context.user_data.get("sel_plan", "1D")
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, 
            caption=f"👤 Payment from {user_id}\n🎮 {g}\n📦 {p}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}")], [InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]))
        await update.message.reply_text("✅ Screenshot sent to Admin!")

async def button_click(update, context):
    query = update.callback_query
    data = query.data
    if data.startswith("game_"):
        game = data.split("_")[1]
        context.user_data["sel_game"] = GAME_MAP[game]
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"plan_{p}")] for p, pr in GAME_PLANS[game].items()]
        await query.message.reply_text("Select Plan:", reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("plan_"):
        context.user_data["sel_plan"] = "1D" if "Day" in data else "1W"
        with open("qr.JPG", "rb") as qr: await query.message.reply_photo(qr, caption="Pay and send screenshot.")
    elif data.startswith("acc_"):
        _, uid, g, p = data.split("_")
        key = approve_and_assign_key(int(uid), g, p)
        if key: 
            await context.bot.send_message(int(uid), f"✅ Approved! 🔑 Key: `{key}`", parse_mode="Markdown")
            await query.edit_message_caption("✅ Approved and Key delivered.")
        else: await query.edit_message_caption("⚠️ No keys in stock!")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
