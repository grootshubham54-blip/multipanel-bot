import os, logging
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from database import *

logging.disable(logging.CRITICAL)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

GAME_PLANS = {
    "👑 ✦ 𝕂𝕀ℕ𝔾 𝕚𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "⭐️ ✦ 𝕎𝕀ℕ𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "🚀 ✦ ℕ𝔼𝕏𝕋 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800"},
    "🪐 ✦ 𝕄𝕒𝕣𝕤 𝕃𝕠𝕒𝕕𝕖𝕣 ✦": {"1 Day": "130", "1 Week": "599"},
    "💀 ✦ 𝔻𝔼𝔸𝔻𝔼𝕐𝔼 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "🐬 ✦ 𝔻𝕆𝕃ℙℍ𝕀ℕ 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

async def start(update, context):
    context.user_data.clear()
    kb = [["🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦", "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦"], ["🎧 ✦ 𝕊𝕦𝕡𝕡𝗼𝕣𝕥 ✦", "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦"]]
    if update.effective_user.id == ADMIN_ID: kb.append(["⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦"])
    await update.message.reply_text("🚀 स्वागत है!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🔙 Back": context.user_data.clear(); await start(update, context); return

    # Admin Logic: Add Keys Flow
    if user_id == ADMIN_ID:
        if text == "⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦": 
            kb = [["🔑 Add Keys", "📊 Stock"], ["🔙 Back"]]
            await update.message.reply_text("Admin Panel:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "select_game"
            kb = [[g] for g in GAME_PLANS.keys()] + [["🔙 Back"]]
            await update.message.reply_text("गेम चुनें:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
            
        elif context.user_data.get("state") == "select_game":
            context.user_data["add_game"] = text
            context.user_data["state"] = "select_plan"
            kb = [[p] for p in GAME_PLANS[text].keys()] + [["🔙 Back"]]
            await update.message.reply_text("प्लान चुनें:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
            
        elif context.user_data.get("state") == "select_plan":
            context.user_data["add_plan"] = text
            context.user_data["state"] = "add_keys"
            await update.message.reply_text(f"ठीक है! {context.user_data['add_game']} - {text} के लिए कीज (keys) पेस्ट करें:")
            
        elif context.user_data.get("state") == "add_keys":
            for k in text.split("\n"):
                if k.strip(): save_key(context.user_data["add_game"], k.strip(), context.user_data["add_plan"])
            await update.message.reply_text("✅ कीज सफलतापूर्वक ऐड हो गई!", reply_markup=ReplyKeyboardMarkup([["🔙 Back"]], resize_keyboard=True))
            context.user_data.clear()
            
        elif text == "📊 Stock":
            msg = "📊 *Current Stock:*\n"
            for g, plans in GAME_PLANS.items():
                msg += f"\n*{g}:*\n"
                for p in plans: msg += f"  - {p}: {get_stock_count(g, p)} keys\n"
            await update.message.reply_text(msg, parse_mode="Markdown")

async def button_click(update, context):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("game_"):
        game = query.data.split("_")[1]
        context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{p}_{pr}")] for p, pr in GAME_PLANS[game].items()]
        await query.edit_message_text(f"🎮 {game}\nप्लान चुनें:", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data.startswith("acc_"):
        d = query.data.split("_")
        key = approve_and_assign_key(int(d[1]), d[2], d[3])
        if key: await context.bot.send_message(int(d[1]), f"🎉 Success! Key: `{key}`", parse_mode="Markdown")

def main():
    if not TOKEN: return
    create_tables()
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling(drop_pending_updates=True, timeout=10)

if __name__ == "__main__":
    main()
