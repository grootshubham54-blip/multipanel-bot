import os, logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)
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

def admin_keyboard():
    global is_bot_active
    status = "ON" if is_bot_active else "OFF"
    return ReplyKeyboardMarkup([
        ["🔑 Add Keys", "📊 Stock"], ["📊 Sales Dashboard", "👥 Total Users"], 
        ["📜 Key Report", "🔄 Resend Key"], ["📂 Export Data", "📢 Broadcast"],
        ["💾 Backup DB", "🗑 Delete Key"], [f"Maintenance: {status}"], ["🔙 Back"]
    ], resize_keyboard=True)

async def start(update, context):
    user = update.effective_user
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username or "N/A"))
    conn.commit(); conn.close()
    welcome_text = "🎮 Welcome to IOS SHUBHAM License Store\n\n🚀 Select an option below to get started."
    kb = [["🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦", "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦"], ["🎧 ✦ 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 ✦", "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦"]]
    if user.id == ADMIN_ID: kb.append(["⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦"])
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    global is_bot_active
    user_id = update.effective_user.id
    
    # --- फोटो (पेमेंट) हैंडलर ---
    if update.message.photo:
        if user_id != ADMIN_ID:
            g = context.user_data.get("game", "N/A"); p = context.user_data.get("plan", "N/A")
            btns = [[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}_{g}_{p}")]]
            await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}\nGame: {g}\nPlan: {p}", reply_markup=InlineKeyboardMarkup(btns))
            await update.message.reply_text("✅ Screenshot sent!")
        return

    text = update.message.text
    if text == "🔙 Back": context.user_data.clear(); await start(update, context); return
    
    # --- एडमिन फीचर्स (सभी पुराने फीचर्स यहाँ रखें) ---
    if user_id == ADMIN_ID:
        if text == "⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard()); return
        elif text == "📊 Stock":
            msg = "📊 *Stock:*\n"
            for g, plans in GAME_PLANS.items():
                for p in plans: msg += f"{g} ({p}): {get_stock_count(g, p)}\n"
            await update.message.reply_text(msg, parse_mode="Markdown"); return
        elif text == "📢 Broadcast": context.user_data["state"] = "broadcasting"; await update.message.reply_text("Enter message:"); return
        # [यहाँ अपने बाकी पुराने फीचर्स (Backup, Export, Resend आदि) पेस्ट करें]

    # --- यूजर फीचर्स ---
    if text == "🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb)); return

async def button_click(update, context):
    query = update.callback_query; await query.answer()
    data = query.data
    # [अपना पुराना पेमेंट और की-असाइनमेंट वाला पूरा लॉजिक यहाँ रखें]

def main():
    create_tables()
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, message_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    print("Bot is running..."); app.run_polling()

if __name__ == "__main__":
    main()
