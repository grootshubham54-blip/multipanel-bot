import os, logging
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
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
    global is_bot_active
    if not is_bot_active and update.effective_user.id != ADMIN_ID: return
    user = update.effective_user
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username or "N/A"))
    conn.commit(); conn.close()
    
    kb = [["🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦", "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦"], ["🎧 ✦ 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 ✦", "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦"]]
    if user.id == ADMIN_ID: kb.append(["⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦"])
    await update.message.reply_text("🎮 Welcome to IOS SHUBHAM License Store", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "🔙 Back": context.user_data.clear(); await start(update, context); return

    if user_id == ADMIN_ID:
        if text == "⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "select_game"
            kb = [[g] for g in GAME_PLANS.keys()] + [["🔙 Back"]]
            await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        elif context.user_data.get("state") == "select_game":
            context.user_data["add_game"] = text; context.user_data["state"] = "select_plan"
            kb = [[p] for p in GAME_PLANS[text].keys()] + [["🔙 Back"]]
            await update.message.reply_text("Select Plan:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        elif context.user_data.get("state") == "select_plan":
            context.user_data["add_plan"] = text; context.user_data["state"] = "add_keys"
            await update.message.reply_text("Enter keys (one per line):")
        elif context.user_data.get("state") == "add_keys":
            for k in text.split("\n"):
                if k.strip(): save_key(context.user_data["add_game"], k.strip(), context.user_data["add_plan"])
            await update.message.reply_text("✅ Keys Saved!", reply_markup=admin_keyboard()); context.user_data.clear()
        elif text == "📊 Stock":
            msg = "📊 *Stock:*\n"
            for g, plans in GAME_PLANS.items():
                for p in plans: msg += f"{g} ({p}): {get_stock_count(g, p)}\n"
            await update.message.reply_text(msg, parse_mode="Markdown")

    if text == "🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("game", "N/A"); p = context.user_data.get("plan", "N/A")
        btns = [[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}_{g}_{p}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Pay by {user_id}\nGame: {g}\nPlan: {p}", reply_markup=InlineKeyboardMarkup(btns))
        await update.message.reply_text("✅ Screenshot sent!")

async def button_click(update, context):
    query = update.callback_query; await query.answer()
    data = query.data
    if data.startswith("game_"):
        game = data.split("_")[1]; context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p}", callback_data=f"pay_{p}_{pr}")] for p, pr in GAME_PLANS[game].items()]
        await query.edit_message_text(f"🎮 {game}\nSelect plan:", reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("pay_"):
        context.user_data["plan"] = data.split("_")[1]
        await query.message.reply_text("Send screenshot now.")
    elif data.startswith("acc_"):
        d = data.split("_"); uid, game, plan = int(d[1]), d[2], d[3]
        key = approve_and_assign_key(uid, game, plan)
        if key: await context.bot.send_message(uid, f"🎉 Key: `{key}`", parse_mode="Markdown"); await query.edit_message_caption(caption="✅ Approved")
        else: await query.edit_message_caption(caption="⚠️ Stock Empty!")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
