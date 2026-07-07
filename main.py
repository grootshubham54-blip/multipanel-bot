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
        ["🔑 Add Keys", "📊 Stock"], 
        ["📊 Sales Dashboard", "👥 Total Users"], 
        ["📜 Key Report", "🔄 Resend Key"],
        ["📂 Export Data", "📢 Broadcast"],
        ["💾 Backup DB", "🗑 Delete Key"],
        [f"Maintenance: {status}"],
        ["🔙 Back"]
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_bot_active
    if not is_bot_active and update.effective_user.id != ADMIN_ID: return
    
    user = update.effective_user
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username or "N/A"))
    conn.commit()
    conn.close()
    
    welcome_text = "🎮 Welcome to IOS SHUBHAM License Store\n\n🚀 Select an option below."
    kb = [["🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦", "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦"], ["🎧 ✦ 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 ✦", "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦"]]
    if user.id == ADMIN_ID: kb.append(["⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦"])
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_bot_active
    text = update.message.text
    user_id = update.effective_user.id
    
    if not is_bot_active and user_id != ADMIN_ID: return

    # Maintenance Toggle Fix
    if user_id == ADMIN_ID and text.startswith("Maintenance:"):
        is_bot_active = not is_bot_active
        await update.message.reply_text(f"✅ बोट मेंटेनेंस मोड {'ON' if is_bot_active else 'OFF'} कर दिया गया है!", reply_markup=admin_keyboard())
        return

    if context.user_data.get("state") == "broadcasting":
        users = get_all_users()
        for u in users:
            try: await context.bot.send_message(u[0], text)
            except: pass
        await update.message.reply_text("✅ Broadcast Sent!", reply_markup=admin_keyboard())
        context.user_data.clear()
        return

    if text == "🔙 Back":
        context.user_data.clear()
        await start(update, context)
        return

    if user_id == ADMIN_ID:
        if text == "⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "📢 Broadcast":
            context.user_data["state"] = "broadcasting"
            await update.message.reply_text("Send your Broadcast message:")
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "select_game"
            kb = [[g] for g in GAME_PLANS.keys()] + [["🔙 Back"]]
            await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        elif context.user_data.get("state") == "select_game":
            if text in GAME_PLANS:
                context.user_data["add_game"] = text
                context.user_data["state"] = "select_plan"
                kb = [[p] for p in GAME_PLANS[text].keys()] + [["🔙 Back"]]
                await update.message.reply_text("Select Plan:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        elif context.user_data.get("state") == "select_plan":
            context.user_data["add_plan"] = text
            context.user_data["state"] = "add_keys"
            await update.message.reply_text("Enter keys (one per line):", reply_markup=ReplyKeyboardMarkup([["🔙 Back"]], resize_keyboard=True))
        elif context.user_data.get("state") == "add_keys":
            for k in text.split("\n"):
                if k.strip(): save_key(context.user_data["add_game"], k.strip(), context.user_data["add_plan"])
            await update.message.reply_text("✅ Keys Saved!", reply_markup=admin_keyboard())
            context.user_data.clear()
        elif text == "📊 Stock":
            msg = "📊 *Current Stock:*\n\n"
            for g, plans in GAME_PLANS.items():
                msg += f"*{g}:*\n"
                for p in plans: msg += f"  - {p}: {get_stock_count(g, p)} keys\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
        # अन्य एडमिन फीचर्स...

    # User side handling
    if text == "🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("game", "Unknown")
        p = context.user_data.get("plan", "Unknown")
        btns = [[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), 
                 InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}_{g}_{p}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, 
                                     caption=f"Payment from {user_id}\nGame: {g}\nPlan: {p}", 
                                     reply_markup=InlineKeyboardMarkup(btns))
        await update.message.reply_text("✅ Screenshot sent!")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    if query.data.startswith("game_"):
        game = query.data.split("_", 1)[1]
        context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{p}_{pr}_{game}")] for p, pr in GAME_PLANS[game].items()]
        await query.edit_message_text(f"🎮 *{game}*\nSelect your plan:", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    elif query.data.startswith("pay_"):
        data = query.data.split("_")
        context.user_data["plan"], context.user_data["game"] = data[1], data[3]
        await query.message.reply_text(f"Please send screenshot for {data[3]} ({data[1]})")
    elif query.data.startswith("acc_"):
        data = query.data.split("_")
        uid, game, plan = int(data[1]), data[2], data[3]
        key = approve_and_assign_key(uid, game, plan) # सुनिश्चित करें कि यह function सही key रिटर्न कर रहा है
        if key:
            await context.bot.send_message(uid, f"🎉 *Success!*\nKey: `{key}`", parse_mode="Markdown")
            await query.edit_message_caption(caption=f"✅ Approved! Key: {key}")
        else:
            await query.edit_message_caption(caption="⚠️ Error: No keys left in DB!")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
