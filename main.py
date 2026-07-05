import os, logging
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from database import *

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593 
SUPPORT_USERNAME = "@IOS_HACK_S" 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

# एडमिन कीबोर्ड
def admin_keyboard():
    return ReplyKeyboardMarkup([
        ["🔑 Add Keys", "📊 Stock"], 
        ["📊 Sales Dashboard", "👥 Total Users"], 
        ["📜 Key Report", "🔄 Resend Key"],
        ["📂 Export Data", "📢 Broadcast"],
        ["💾 Backup DB", "🗑 Delete Key"],
        ["🔙 Back"]
    ], resize_keyboard=True)

# मुख्य यूजर कीबोर्ड
def main_keyboard(user_id):
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

async def start(update, context):
    user = update.effective_user
    # डेटाबेस में यूजर सेव करें
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username or "N/A"))
    conn.commit()
    conn.close()
    
    # आपका वेलकम मैसेज
    welcome_text = (
        "🎮 *Welcome to IOS SHUBHAM License Store*\n\n"
        "Your trusted destination for premium gaming licenses.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "📦 *Available Products*\n• KINGIOS\n• WINIOS\n• NEXT IOS\n• Mars Loader\n• DEADEYE\n• DOLPHIN IOS\n\n"
        "⏳ *License Durations*\n• 1 Day License\n• 7 Days License\n• 30 Days License\n\n"
        "✨ *Why Choose Us?*\n✅ Instant QR Code Generation\n✅ Automatic Payment Verification\n✅ Instant License Delivery\n✅ Real-Time Order Tracking\n✅ Fast & Reliable Support\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "🚀 Select an option from the menu below to get started.\n\n"
        "Thank you for choosing IOS SHUBHAM License Store."
    )
    
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=main_keyboard(user.id))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    # यहाँ आपके पुराने सभी बटन्स का लॉजिक है
    if text == "🎮 Games":
        # अगर आपके 'Games' के लिए कोई इनलाइन बटन हैं तो वो दिखाएं
        await update.message.reply_text("Select a Game from the list above or contact support.")
    elif text == "🔑 My Keys":
        keys = get_user_keys(user_id)
        if not keys: await update.message.reply_text("No keys found!")
        else: await update.message.reply_text("\n".join([f"{g} ({p}): {k}" for g, p, k in keys]))
    elif text == "📞 Support": 
        await update.message.reply_text(f"📞 Contact: {SUPPORT_USERNAME}")
    elif text == "💳 Payment": 
        await update.message.reply_text(f"💳 Payment Details:\n{PAYMENT_DETAILS}")
    elif text == "🛠 Admin Panel" and user_id == ADMIN_ID:
        await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
    elif text == "🔙 Back":
        await start(update, context)
    # बाकी एडमिन कमांड्स यहाँ जोड़ें (Add Keys, Stock आदि)
    
def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, message_handler))
    # अगर आप फोटो से पेमेंट ले रहे हैं
    app.add_handler(MessageHandler(filters.PHOTO, message_handler)) 
    app.run_polling()

if __name__ == "__main__":
    main()
