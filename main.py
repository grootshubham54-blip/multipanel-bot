import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, add_user, save_pending_payment, approve_and_assign_key
from admin_panel import admin_keyboard, admin_game_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7908981593"

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "199", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1300"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "129", "1 Week": "499", "1 Month": "999"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": {"1 Day": "150", "1 Week": "600", "1 Month": "1600"}
}

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if update.message.photo and str(user_id) != ADMIN_ID:
        g = context.user_data.get("u_game", "Unknown")
        p = context.user_data.get("u_plan", "Unknown")
        # डेटाबेस में सेव करें
        pay_id = save_pending_payment(user_id, g, p, update.message.photo[-1].file_id)
        
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, 
            caption=f"👤 Payment from {user_id}\n🎮 {g} - {p}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve", callback_data=f"acc_{pay_id}")]]))
        await update.message.reply_text("✅ Payment sent for approval!")
        return

    # ... (बाकी पुराना लॉजिक: 🎮 Games, plan selection आदि) ...

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("acc_"):
        pay_id = int(query.data.split("_")[1])
        key, uid = approve_and_assign_key(pay_id)
        if key:
            await context.bot.send_message(uid, f"✅ Key: `{key}`", parse_mode="Markdown")
            await query.edit_message_caption(caption="✅ Approved.")
        else: await query.edit_message_caption(caption="❌ No stock or Invalid payment.")
