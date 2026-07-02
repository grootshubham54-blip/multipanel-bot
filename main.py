import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, get_stock, get_total_users
from admin_panel import admin_keyboard, admin_game_selection_keyboard

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7908981593" # आपकी ID

# पुरानी प्राइसिंग लिस्ट
GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "199", "1 Week": "600", "1 Month": "1299"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # एडमिन के लिए अलग कीबोर्ड, यूजर के लिए अलग
    if str(update.effective_user.id) == ADMIN_ID:
        keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"], ["🛠 Admin Panel"]]
    else:
        keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)

    # 1. एडमिन पैनल ओपनिंग
    if text == "🛠 Admin Panel" and user_id == ADMIN_ID:
        await update.message.reply_text("🛠 Admin Panel:", reply_markup=admin_keyboard())
    
    # 2. गेम्स और प्राइसिंग (आपका पुराना फीचर)
    elif text == "🎮 Games":
        await update.message.reply_text("गेम चुनें:", reply_markup=admin_game_selection_keyboard())
    
    elif text in GAME_PLANS:
        keyboard = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"qr_{pr}")] for p, pr in GAME_PLANS[text].items()]
        await update.message.reply_text(f"🎮 {text} का प्लान चुनें:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    # 3. सपोर्ट और अन्य
    elif text == "📞 Support":
        await update.message.reply_text("📞 Contact us at: @YOUR_SUPPORT_USERNAME") # यहाँ अपना सपोर्ट लिंक डालें
    
    elif text == "💳 Payment":
        await update.message.reply_text("पेमेंट करने के लिए गेम सेक्शन से प्लान चुनें।")
    
    elif text == "🔑 My Keys":
        await update.message.reply_text("आपकी खरीदी गई Keys यहाँ दिखेंगी।")
    
    # एडमिन फीचर्स (Add Keys आदि)
    elif user_id == ADMIN_ID and text in ["🔑 Add Keys", "📦 Stock", "📢 Broadcast", "👥 Total Users"]:
        await update.message.reply_text(f"Admin feature: {text} (Coming soon...)")

    else:
        await start(update, context)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("qr_"):
        price = query.data.split("_")[1]
        with open("qr.JPG", "rb") as qr:
            await query.message.reply_photo(photo=qr, caption=f"✅ QR पर ₹{price} पे करें और स्क्रीनशॉट भेजें।")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
