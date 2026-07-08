import os, logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
if not TOKEN: raise ValueError("❌ BOT_TOKEN missing!")

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
    save_user_to_db(user.id, user.username)
    welcome_text = "🎮 Welcome to IOS SHUBHAM License Store\n\nYour trusted destination for premium gaming licenses."
    kb = [["🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦", "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦"], ["🎧 ✦ 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 ✦", "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦"]]
    if user.id == ADMIN_ID: kb.append(["⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦"])
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    global is_bot_active
    text = update.message.text
    user_id = update.effective_user.id
    if not is_bot_active and user_id != ADMIN_ID: return
    if user_id == ADMIN_ID and text.startswith("Maintenance:"):
        is_bot_active = not is_bot_active
        await update.message.reply_text(f"✅ Maintenance: {'ON' if is_bot_active else 'OFF'}", reply_markup=admin_keyboard()); return
    
    # एडमिन कमांड्स
    if user_id == ADMIN_ID:
        if text == "⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "📢 Broadcast": context.user_data["state"] = "broadcasting"; await update.message.reply_text("Send message:")
        elif text == "🔑 Add Keys": context.user_data["state"] = "select_game"; await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup([[g] for g in GAME_PLANS.keys()], resize_keyboard=True))
        elif context.user_data.get("state") == "select_game": context.user_data["add_game"] = text; context.user_data["state"] = "select_plan"; await update.message.reply_text("Select Plan:", reply_markup=ReplyKeyboardMarkup([[p] for p in GAME_PLANS[text].keys()], resize_keyboard=True))
        elif context.user_data.get("state") == "select_plan": context.user_data["add_plan"] = text; context.user_data["state"] = "add_keys"; await update.message.reply_text("Enter keys (new line):")
        elif context.user_data.get("state") == "add_keys":
            for k in text.split("\n"):
                if k.strip(): save_key(context.user_data["add_game"], k.strip(), context.user_data["add_plan"])
            await update.message.reply_text("✅ Saved!", reply_markup=admin_keyboard()); context.user_data.clear()
        elif text == "📊 Stock":
            msg = "📊 *Stock:*\n"; [msg := msg + f"*{g}:* {p}: {get_stock_count(g, p)} left\n" for g, pl in GAME_PLANS.items() for p in pl]
            await update.message.reply_text(msg, parse_mode="Markdown")

    if text == "🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦": await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]))
    elif text == "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦": keys = get_user_keys(user_id); await update.message.reply_text("\n".join([f"{g} ({p}): {k}" for g, p, k in keys]) if keys else "No keys!")
    elif text == "🎧 ✦ 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 ✦": await update.message.reply_text(f"Support: {SUPPORT_USERNAME}")
    elif text == "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦": await update.message.reply_text(f"Details: {PAYMENT_DETAILS}")
    elif update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("game", "N/A"); p = context.user_data.get("plan", "N/A")
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}\nGame: {g}\nPlan: {p}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}_{g}_{p}")]]))
        await update.message.reply_text("✅ Sent!")

async def button_click(update, context):
    query = update.callback_query; await query.answer()
    if query.data.startswith("game_"):
        game = query.data.split("_")[1]; context.user_data["game"] = game
        await query.edit_message_text(f"🎮 *{game}*\nSelect plan:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"{p} - ₹{pr} ({get_stock_count(game, p)} Left)", callback_data=f"pay_{p}_{pr}")] for p, pr in GAME_PLANS[game].items()]), parse_mode="Markdown")
    elif query.data.startswith("pay_"): 
        if os.path.exists("qr.JPG"): await query.message.reply_photo(photo=open("qr.JPG", "rb"))
    elif query.data.startswith(("acc_", "rej_")):
        data = query.data.split("_"); action, uid, game, plan = data[0], int(data[1]), data[2], data[3]
        if action == "acc": key = approve_and_assign_key(uid, game, plan); await context.bot.send_message(uid, f"🎉 Key: `{key}`" if key else "⚠️ No keys!"); await query.edit_message_caption(caption="✅ Approved!")
        else: await context.bot.send_message(uid, "❌ Rejected."); await query.edit_message_caption(caption="❌ Rejected!")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
