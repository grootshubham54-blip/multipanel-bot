import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

# Logging Setup - यह टर्मिनल में एरर दिखाएगा
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593 
SUPPORT_USERNAME = "@IOS_HACK_S" 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Database logic
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username or "N/A"))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB Error: {e}")

    welcome_text = (
        "🎮 **Welcome to  𝐈𝐎𝐒_𝐒𝐇𝐔𝐁𝐇𝐀𝐌 ™ License Store**\n\n"
        "Your trusted destination for premium gaming licenses.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "📦 **Available Products**\n"
        "• KING iOS | WINIOS | NEXT IOS\n"
        "• Mars Loader | DEADEYE | DOLPHIN IOS\n\n"
        "⏳ **License Durations**\n"
        "• 1 Day | 1 Week | 1 Month\n\n"
        "✨ **Why Choose Us?**\n"
        "✅ Instant QR Code Generation\n"
        "✅ Automatic Payment Verification\n"
        "✅ Instant License Delivery\n\n"
        "🚀 *Select an option from the menu below to get started.*"
    )
    
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user.id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    
    await update.message.reply_text(
        welcome_text, 
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), 
        parse_mode="Markdown"
    )

# --- यहाँ आपका message_handler और button_click वाला लॉजिक आएगा ---
# (आपका पिछला पूरा लॉजिक यहाँ पेस्ट करें)

def main():
    # डेटाबेस टेबल बनाना
    create_tables()
    
    # Application builder
    app = Application.builder().token(TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND) | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("🚀 बोट सफलतापूर्वक शुरू हो गया है!")
    app.run_polling()

if __name__ == "__main__":
    main()