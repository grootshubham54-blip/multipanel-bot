import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

# Logging setup
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593 
SUPPORT_USERNAME = "@IOS_HACK_S" 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

# Game Plans
GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

# Admin Keyboard
def admin_keyboard():
    return ReplyKeyboardMarkup([
        ["🔑 Add Keys", "📊 Stock"], 
        ["📊 Sales Dashboard", "👥 Total Users"], 
        ["📜 Key Report", "🔄 Resend Key"],
        ["📂 Export Data", "📢 Broadcast"],
        ["💾 Backup DB", "🗑 Delete Key"],
        ["🔙 Back"]
    ], resize_keyboard=True)

# Start Command with Premium Welcome Message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # DB entry
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username or "N/A"))
    conn.commit()
    conn.close()
    
    # Premium Message
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
    if user.id == ADMIN_ID: 
        kb.append(["🛠 Admin Panel"])
        
    await update.message.reply_text(
        welcome_text, 
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), 
        parse_mode="Markdown"
    )

# [NOTE: Baaki message_handler aur button_click function aapke purane code wale hi rahenge]
# Agar aapko unmein bhi changes chahiye toh batayein.

def main():
    create_tables()
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    # ... (Baaki handlers yahan add karein)
    app.run_polling()

if __name__ == "__main__":
    main()