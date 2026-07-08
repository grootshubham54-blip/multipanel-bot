import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

# Logging setup
logging.basicConfig(level=logging.INFO)

# Configuration
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
    # Ensure user is in DB
    add_user_to_db(user.id, user.username or "N/A")
    
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user.id == ADMIN_ID:
        kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    # Global Reset
    if text == "🔙 Back":
        context.user_data.clear()
        await start(update, context)
        return

    # Broadcast State
    if context.user_data.get("state") == "broadcasting":
        users = get_all_users()
        for u in users:
            try: await context.bot.send_message(chat_id=int(u), text=text)
            except: continue
        await update.message.reply_text("✅ Broadcast Sent!", reply_markup=admin_keyboard())
        context.user_data.clear()
        return

    # Admin State Management for Add Keys
    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel": 
            await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        
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

        # Other Admin Logic
        elif text == "📢 Broadcast":
            context.user_data["state"] = "broadcasting"
            await update.message.reply_text("Send your message:")

    # User Logic
    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "🔑 My Keys":
        keys = get_user_keys(user_id)
        if not keys: await update.message.reply_text("No keys found!")
        else: await update.message.reply_text("\n".join([f"{g} ({p}): {k}" for g, p, k in keys]))
    elif text == "📞 Support": await update.message.reply_text(f"📞 Contact: {SUPPORT_USERNAME}")
    elif text == "💳 Payment": await update.message.reply_text(f"💳 Payment Details:\n{PAYMENT_DETAILS}")

async def button_click(update, context):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("game_"):
        game = query.data.split("_")[1]
        context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{p}_{pr}")] for p, pr in GAME_PLANS[game].items()]
        await query.edit_message_text(f"🎮 *{game}*\nSelect plan:", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
