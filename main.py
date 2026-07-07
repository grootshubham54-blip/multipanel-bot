import os, logging, sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import * 

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593 
SUPPORT_USERNAME = "@IOS_HACK_S" 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

GAME_PLANS = {
    "👑 ✦ 𝕂𝕀ℕ𝔾 𝕚𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "⭐️ ✦ 𝕎𝕀ℕ𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "🚀 ✦ ℕ𝔼𝕏𝕋 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800"},
    "🪐 ✦ 𝕄𝕒𝕣𝕤 𝕃𝕠𝕒𝕕𝕖𝕣 ✦": {"1 Day": "130", "1 Week": "599"},
    "💀 ✦ 𝔻𝔼𝔸𝔻𝔼𝕐𝔼 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "🐬 ✦ 𝔻𝕆𝕃ℙℍ𝕀ℕ 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

def admin_keyboard():
    return ReplyKeyboardMarkup([
        ["🔑 Add Keys", "📊 Stock"], 
        ["📊 Sales Dashboard", "👥 Total Users"], 
        ["📜 Key Report", "🔄 Resend Key"],
        ["📂 Export Data", "📢 Broadcast"],
        ["💾 Backup DB", "🗑 Delete Key"],
        ["🔙 Back"]
    ], resize_keyboard=True)

async def start(update, context):
    user = update.effective_user
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username or "N/A"))
    conn.commit()
    conn.close()
    
    # आपका ओरिजिनल वेलकम मैसेज
    welcome_text = (
        "🎮 Welcome to IOS SHUBHAM License Store\n\n"
        "Your trusted destination for premium gaming licenses.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "📦 Available Products\n"
        "• KINGIOS\n• WINIOS\n• NEXT IOS\n• Mars Loader\n• DEADEYE\n• DOLPHIN IOS\n\n"
        "⏳ License Durations\n"
        "• 1 Day License\n• 7 Days License\n• 30 Days License\n\n"
        "✨ Why Choose Us?\n"
        "✅ Instant QR Code Generation\n"
        "✅ Automatic Payment Verification\n"
        "✅ Instant License Delivery\n"
        "✅ Real-Time Order Tracking\n"
        "✅ Fast & Reliable Support\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "🚀 Select an option from the menu below to get started.\n\n"
        "Thank you for choosing IOS SHUBHAM License Store."
    )
    
    kb = [["🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦", "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦"], ["🎧 ✦ 𝕊𝕦𝕡𝕡𝚘𝕣𝕥 ✦", "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦"]]
    if user.id == ADMIN_ID: kb.append(["⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦"])
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    # --- ADMIN BUTTONS ---
    if user_id == ADMIN_ID:
        if text == "⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "👥 Total Users": await update.message.reply_text(f"👥 Total Users: {len(get_all_users())}")
        elif text == "📊 Sales Dashboard": await update.message.reply_text(f"📊 Total Keys Sold: {get_sold_keys_count()}")
        elif text == "📊 Stock":
            msg = "📊 *Current Stock:*\n"
            for g, plans in GAME_PLANS.items():
                for p in plans: msg += f"{g} ({p}): {get_stock_count(g, p)}\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
        elif text == "📜 Key Report":
            conn = get_conn()
            keys = conn.execute("SELECT game, plan, key, used FROM keys").fetchall()
            conn.close()
            msg = "📜 *Key Report:*\n" + "\n".join([f"{k[0]} ({k[1]}): {k[2]} - {'✅' if k[3] else '❌'}" for k in keys])
            await update.message.reply_text(msg[:4000], parse_mode="Markdown")
        elif text == "🗑 Delete Key":
            context.user_data["state"] = "del_key"
            await update.message.reply_text("Enter the exact key you want to delete:")
        elif context.user_data.get("state") == "del_key":
            conn = get_conn()
            conn.execute("DELETE FROM keys WHERE key=?", (text.strip(),))
            conn.commit()
            conn.close()
            await update.message.reply_text("✅ Key Deleted Successfully!")
            context.user_data.clear()
        elif text == "📢 Broadcast":
            context.user_data["state"] = "broadcast"
            await update.message.reply_text("Send your broadcast message:")
        elif context.user_data.get("state") == "broadcast":
            users = get_all_users()
            for u in users:
                try: await context.bot.send_message(u[0], text)
                except: pass
            await update.message.reply_text("✅ Broadcast Sent!")
            context.user_data.clear()
        elif text == "🔙 Back": await start(update, context)

    # --- USER BUTTONS ---
    if text == "🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦":
        keys = get_user_keys(user_id)
        if keys: await update.message.reply_text("\n".join([f"{k[0]} ({k[1]}): {k[2]}" for k in keys]))
        else: await update.message.reply_text("No keys found!")
    elif text == "🎧 ✦ 𝕊𝕦𝕡𝕡𝚘𝕣𝕥 ✦": await update.message.reply_text(f"📞 Contact: {SUPPORT_USERNAME}")
    elif text == "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦": await update.message.reply_text(f"💳 Payment Details:\n{PAYMENT_DETAILS}")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
