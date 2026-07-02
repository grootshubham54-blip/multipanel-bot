import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# लॉगिंग सेट करें
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593

# 1. आपकी पूरी पुरानी लिस्ट (कुछ भी डिलीट नहीं किया है)
GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN", "NEXT IOS": "NEXT", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "MARS", "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": "DEAD", "DOLPHIN IOS": "DOLP"}
REV_GAME_MAP = {v: k for k, v in GAME_MAP.items()}
PLAN_MAP = {"1 Day": "1D", "1 Week": "1W", "1 Month": "1M"}
REV_PLAN_MAP = {"1D": "1 Day", "1W": "1 Week", "1M": "1 Month"}

# 2. कीबोर्ड्स (सारे बटन्स वापस ला दिए हैं)
def admin_keyboard():
    return ReplyKeyboardMarkup([["🔑 Add Keys", "📦 Stock"], ["👥 Total Users", "🔙 Back"]], resize_keyboard=True)

def main_keyboard(is_admin):
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if is_admin: kb.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

# 3. डेटाबेस और बाकी फंक्शन्स (यह सुनिश्चित करें कि आपका database.py फाइल मौजूद है)
from database import create_tables, save_key, approve_and_assign_key, add_user, get_user_keys

async def start(update, context):
    add_user(update.effective_user.id, update.effective_user.username or "User")
    await update.message.reply_text("👋 Welcome!", reply_markup=main_keyboard(update.effective_user.id == ADMIN_ID))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    # एडमिन पैनल बटन्स (सारे बटन्स जो आपने मांगे थे)
    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "🔑 Add Keys": await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup([[g] for g in GAME_PLANS.keys()], resize_keyboard=True))
        elif text == "🔙 Back": await start(update, context)
    
    # यूजर बटन्स
    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif update.message.photo and user_id != ADMIN_ID:
        # पेमेंट स्क्रीनशॉट हैंडलिंग
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}")
        await update.message.reply_text("✅ Screenshot received!")

async def button_click(update, context):
    query = update.callback_query
    data = query.data
    if data.startswith("game_"):
        game = data.split("_")[1]
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{GAME_MAP[game]}_{PLAN_MAP[p]}")] for p, pr in GAME_PLANS[game].items()]
        await query.message.reply_text("Select Plan:", reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("pay_"):
        # QR कोड वाला फीचर (जैसा था)
        with open("qr.JPG", "rb") as qr:
            await query.message.reply_photo(photo=qr, caption="Pay and send screenshot.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
