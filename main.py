import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

# Logging setup
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

# --- KEYBOARDS ---
def get_main_kb(uid):
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if uid == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def get_admin_kb():
    return ReplyKeyboardMarkup([["🔑 Add Keys", "📊 Stock"], ["📊 Sales Dashboard", "👥 Total Users"], ["🔙 Back"]], resize_keyboard=True)

# --- START ---
async def start(update, context):
    user = update.effective_user
    welcome_text = (
        "🎮 *Welcome to IOS SHUBHAM License Store*\n\n"
        "Your trusted destination for premium gaming licenses.\n\n"
        "📦 *Available Products*\n• KINGIOS, WINIOS, NEXT IOS, Mars Loader, DEADEYE, DOLPHIN IOS\n\n"
        "🚀 Select an option from the menu below."
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_kb(user.id), parse_mode="Markdown")

# --- MESSAGE HANDLER ---
async def message_handler(update, context):
    text = update.message.text
    uid = update.effective_user.id
    
    if text == "🔙 Back":
        context.user_data.clear()
        await start(update, context)
        return

    # ADMIN LOGIC
    if uid == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("Admin Panel:", reply_markup=get_admin_kb())
        elif text == "📊 Sales Dashboard":
            sold = get_sold_keys_count()
            await update.message.reply_text(f"📊 *Total Sales:* {sold}\n💰 *Revenue:* ₹{sold * 200}", parse_mode="Markdown")
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "add_game"
            await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup([[g] for g in GAME_PLANS.keys()], resize_keyboard=True))
            return
        
        # KEY ADDING FLOW
        if context.user_data.get("state") == "add_game":
            context.user_data["game"] = text
            context.user_data["state"] = "add_keys"
            await update.message.reply_text("Paste the Key:")
            return
        elif context.user_data.get("state") == "add_keys":
            save_key(context.user_data["game"], "1 Day", text) # Plan auto-set
            await update.message.reply_text("✅ Key Saved!", reply_markup=get_admin_kb())
            context.user_data.clear()
            return

    # USER LOGIC
    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "💳 Payment":
        await update.message.reply_text(f"💳 Payment Details:\n{PAYMENT_DETAILS}")
    elif update.message.photo and uid != ADMIN_ID:
        await update.message.reply_text("✅ Screenshot sent to Admin!")

# --- CALLBACK HANDLER ---
async def button_click(update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("game_"):
        game = query.data.split("_")[1]
        kb = [[InlineKeyboardButton(p, callback_data=f"pay_{p}")] for p in GAME_PLANS[game].keys()]
        await query.edit_message_text(f"Select plan for {game}:", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data.startswith("pay_"):
        if os.path.exists("qr.JPG"):
            await query.message.reply_photo(photo=open("qr.JPG", "rb"), caption="Please pay and send screenshot.")
        else:
            await query.message.reply_text("⚠️ QR Code missing in server!")

# --- MAIN ---
def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
