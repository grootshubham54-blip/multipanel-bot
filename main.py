import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, add_user, save_pending_payment, approve_and_assign_key, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "199", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1300"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "129", "1 Week": "499", "1 Month": "999"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": {"1 Day": "150", "1 Week": "600", "1 Month": "1600"}
}

def get_main_keyboard(user_id):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    # 1. प्राइसिंग शो करने वाला फीचर (किंग iOS आदि के लिए)
    if text in GAME_PLANS:
        context.user_data["u_game"] = text
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"plan|{p}")] for p, pr in GAME_PLANS[text].items()]
        await update.message.reply_text(f"Select plan for {text}:", reply_markup=InlineKeyboardMarkup(kb))
    
    # 2. अन्य बटन्स
    elif text == "🎮 Games":
        await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
    elif text == "🔑 My Keys":
        keys = get_user_keys(user_id)
        msg = "\n".join([f"🎮 {k[0]} | {k[1]} | Key: `{k[2]}`" for k in keys]) if keys else "❌ No keys found."
        await update.message.reply_text(f"Your Keys:\n{msg}", parse_mode="Markdown")
    elif text == "📞 Support":
        await update.message.reply_text("📞 Contact us at: @YourSupport")
    elif text == "💳 Payment":
        await update.message.reply_text("💳 Please select a game from 'Games' menu first.")
    elif text == "🛠 Admin Panel" and user_id == ADMIN_ID:
        await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
    # ... (बाकी एडमिन बटन्स)
    else:
        await update.message.reply_text("Welcome!", reply_markup=get_main_keyboard(user_id))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if "plan|" in query.data:
        context.user_data["u_plan"] = query.data.split("|")[1]
        await query.message.reply_text("Please send payment screenshot.")
    elif query.data.startswith("acc_"):
        # अप्रूवल लॉजिक
        pay_id = int(query.data.split("_")[1])
        key, uid = approve_and_assign_key(pay_id)
        if key:
            await context.bot.send_message(uid, f"✅ Approved! Key: `{key}`")
            await query.edit_message_caption(caption="✅ Approved.")
        else: await query.edit_message_caption(caption="❌ No stock.")

# ... (start, main फंक्शन वही रहेंगे)
