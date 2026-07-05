import os, logging
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)
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

def get_main_menu(is_admin=False):
    kb = [
        [InlineKeyboardButton("🎮 Games", callback_data="menu_games"), InlineKeyboardButton("🔑 My Keys", callback_data="menu_keys")],
        [InlineKeyboardButton("📞 Support", callback_data="menu_support"), InlineKeyboardButton("💳 Payment", callback_data="menu_payment")]
    ]
    if is_admin:
        kb.append([InlineKeyboardButton("🛠 Admin Panel", callback_data="menu_admin")])
    return InlineKeyboardMarkup(kb)

async def start(update, context):
    user = update.effective_user
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username or "N/A"))
    conn.commit()
    conn.close()
    
    # आपका नया वेलकम मैसेज
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
    
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu(user.id == ADMIN_ID))

# (बाकी button_click और message_handler कोड वही रहेगा जो पहले था)
