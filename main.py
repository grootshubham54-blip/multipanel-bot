import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7908981593"

GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN", "NEXT IOS": "NEXT", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "MARS", "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": "DEAD", "DOLPHIN IOS": "DOLP"}
REV_GAME_MAP = {v: k for k, v in GAME_MAP.items()}
PLAN_PRICES = {"1 Day": "₹200", "1 Week": "₹800", "1 Month": "₹2000"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id, update.effective_user.username or "User")
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if str(user_id) == ADMIN_ID: keyboard.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    # 1. Screenshot Handler
    if update.message.photo and user_id != ADMIN_ID:
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}")
        await update.message.reply_text("✅ Screenshot received!")
        return

    # 2. Universal Buttons (Work for Everyone)
    if text == "🎮 Games":
        await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_MAP:
        # यहाँ प्राइस के साथ बटन दिखेंगे
        kb = [[InlineKeyboardButton(f"{p} ({PLAN_PRICES[p]})", callback_data=f"pay_{GAME_MAP[text]}_{p.replace(' ','')}")] for p in PLAN_PRICES]
        await update.message.reply_text(f"🎮 Plan for {text}:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "🔑 My Keys":
        keys = get_user_keys(update.effective_user.id)
        msg = "🔑 Keys:\n" + "\n".join([f"{k[0]}: {k[2]}" for k in keys]) if keys else "❌ No keys."
        await update.message.reply_text(msg)
    elif text in ["🔙 Back to Main", "🔙 Back to Admin"]:
        await start(update, context)
        
    # 3. Admin Panel
    elif user_id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("Panel:", reply_markup=admin_keyboard())
        elif text == "🔑 Add Keys": 
            context.user_data["state"] = "awaiting_game"
            await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
        # बाकी एडमिन लॉजिक...

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("pay_"):
        await query.message.reply_text("Send screenshot now.")
    elif query.data.startswith("acc_"):
        await context.bot.send_message(query.data.split("_")[1], "✅ Approved!")
        await query.edit_message_caption(caption="✅ Approved.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
