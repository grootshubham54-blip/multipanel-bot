import os, logging
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
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

def admin_keyboard():
    return ReplyKeyboardMarkup([
        ["🔑 Add Keys", "📊 Stock"], ["📊 Sales Dashboard", "👥 Total Users"], 
        ["📜 Key Report", "🔄 Resend Key"], ["📂 Export Data", "📢 Broadcast"],
        ["💾 Backup DB", "🗑 Delete Key"], ["🔙 Main Menu"]
    ], resize_keyboard=True)

async def start(update, context):
    user = update.effective_user
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username or "N/A"))
    conn.commit()
    conn.close()
    
    welcome_text = (
        "🎮 *Welcome to IOS SHUBHAM License Store*\n\n"
        "Your trusted destination for premium gaming licenses.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "📦 *Available Products*\n• KINGIOS\n• WINIOS\n• NEXT IOS\n• Mars Loader\n• DEADEYE\n• DOLPHIN IOS\n\n"
        "🚀 Select an option from the menu below to get started."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu(user.id == ADMIN_ID))

async def button_click(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "menu_games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await query.edit_message_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data == "menu_admin":
        await query.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
    elif query.data == "menu_keys":
        keys = get_user_keys(query.from_user.id)
        msg = "\n".join([f"{g} ({p}): {k}" for g, p, k in keys]) if keys else "No keys found!"
        await query.edit_message_text(f"🔑 *Your Keys:*\n\n{msg}", parse_mode="Markdown")
    # बाकी लॉजिक वही है...
    elif query.data.startswith("game_"):
        game = query.data.split("_")[1]
        context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{p}_{pr}")] for p, pr in GAME_PLANS[game].items()]
        await query.edit_message_text(f"🎮 {game}\nSelect Plan:", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data.startswith("pay_"):
        # यहाँ फोटो और QR वाला लॉजिक आएगा
        pass

async def message_handler(update, context):
    text = update.message.text
    if text == "🔙 Main Menu":
        await start(update, context)
        return
    # यहाँ एडमिन के सारे पुराने कमांड्स का लॉजिक (Add Keys, Broadcast, आदि) डालें
    # जो आपके पिछले कोड में थे।

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
