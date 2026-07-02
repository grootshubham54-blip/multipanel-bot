import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593 

# Mapping
GAME_PLANS = {"👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"}, "WINIOS": {"1 Day": "199", "1 Week": "600", "1 Month": "1299"}, "NEXT IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"}, "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"}, "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"}, "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"}}
GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN", "NEXT IOS": "NEXT", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "MARS", "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": "DEAD", "DOLPHIN IOS": "DOLP"}
REV_GAME_MAP = {v: k for k, v in GAME_MAP.items()}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id, update.effective_user.username or "User")
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if update.effective_user.id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    state = context.user_data.get("state")

    # 1. Admin State Logic
    if user_id == ADMIN_ID:
        if text == "🔙 Back to Main": await start(update, context); return
        if text == "🛠 Admin Panel" or text == "🔙 Back to Admin":
            context.user_data.clear(); await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard()); return
        
        if state == "awaiting_game" and text in GAME_PLANS:
            context.user_data.update({"add_game": text, "state": "awaiting_plan"})
            await update.message.reply_text("Select plan:", reply_markup=admin_plan_selection_keyboard()); return
        if state == "awaiting_plan" and text in ["1 Day", "1 Week", "1 Month"]:
            context.user_data.update({"add_plan": text, "state": "awaiting_keys"})
            await update.message.reply_text("Enter keys (one per line):"); return
        if state == "awaiting_keys":
            for key in text.split("\n"): save_key(context.user_data["add_game"], key.strip(), context.user_data["add_plan"])
            context.user_data.clear(); await update.message.reply_text("✅ Saved!", reply_markup=admin_keyboard()); return

        if text == "🔑 Add Keys": context.user_data["state"] = "awaiting_game"; await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard()); return
        if text == "📦 Stock": await update.message.reply_text("Stock check logic here..."); return
        if text == "👥 Total Users": await update.message.reply_text(f"Users: {get_total_users()}"); return

    # 2. Customer Logic
    if update.message.photo and user_id != ADMIN_ID:
        # Payment verification logic...
        return
    
    if text == "🎮 Games": await update.message.reply_text("Select:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_PLANS:
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"plan_{GAME_MAP[text]}_{p}")] for p, pr in GAME_PLANS[text].items()]
        await update.message.reply_text("Plan:", reply_markup=InlineKeyboardMarkup(kb))
    else: await start(update, context)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # ChatGPT's Point #2 Resolved
    # Callback logic here...

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
