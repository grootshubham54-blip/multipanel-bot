import os, logging
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from database import *

logging.disable(logging.CRITICAL)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593 
SUPPORT_USERNAME = "@IOS_HACK_S" 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

is_bot_active = True 

GAME_PLANS = {
    "👑 ✦ 𝕂𝕀ℕ𝔾 𝕚𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "⭐️ ✦ 𝕎𝕀ℕ𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "🚀 ✦ ℕ𝔼𝕏𝕋 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800"},
    "🪐 ✦ 𝕄𝕒𝕣𝕤 𝕃𝕠𝕒𝕕𝕖𝕣 ✦": {"1 Day": "130", "1 Week": "599"},
    "💀 ✦ 𝔻𝔼𝔸𝔻𝔼𝕐𝔼 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "🐬 ✦ 𝔻𝕆𝕃ℙℍ𝕀ℕ 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

# --- OPTIMIZED HANDLERS ---
async def start(update, context):
    context.user_data.clear() # हर बार स्टार्ट पर डेटा क्लियर करें
    user = update.effective_user
    kb = [["🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦", "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦"], ["🎧 ✦ 𝕊𝕦𝕡𝕡𝗼𝕣𝕥 ✦", "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦"]]
    if user.id == ADMIN_ID: kb.append(["⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦"])
    await update.message.reply_text("🚀 Welcome! Select an option:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def button_click(update, context):
    query = update.callback_query
    await query.answer() # रिस्पॉन्स को तुरंत कन्फर्म करें
    
    data = query.data
    if data.startswith("game_"):
        game = data.split("_")[1]
        context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{p}_{pr}")] for p, pr in GAME_PLANS[game].items()]
        await query.edit_message_text(f"🎮 {game}\nSelect plan:", reply_markup=InlineKeyboardMarkup(kb))
    
    # बाकी लॉजिक वैसा ही है...
    elif data.startswith("pay_"):
        plan_data = data.split("_")
        context.user_data["plan"] = plan_data[1]
        await query.message.reply_text(f"Send payment screenshot for {plan_data[1]}.")

async def message_handler(update, context):
    text = update.message.text
    # एडमिन कीज ऐड करने के लिए क्विक रिस्पॉन्स मोड
    if text == "🔑 Add Keys":
        context.user_data["state"] = "select_game"
        kb = [[g] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    elif context.user_data.get("state") == "select_game":
        context.user_data["add_game"] = text
        context.user_data["state"] = "select_plan"
        kb = [[p] for p in GAME_PLANS[text].keys()]
        await update.message.reply_text("Select Plan:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    # ... (बाकी के पुराने फीचर्स यहाँ सेम रहेंगे)

def main():
    if not TOKEN: return
    create_tables()
    # 'concurrency' बढ़ा दी है ताकि बटन तुरंत काम करे
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    # timeout को बहुत कम कर दिया है (रॉकेट स्पीड)
    app.run_polling(drop_pending_updates=True, timeout=5, read_timeout=5, write_timeout=5)

if __name__ == "__main__":
    main()
