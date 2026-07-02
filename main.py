import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    ContextTypes, filters
)
# अपनी बनाई हुई database.py और admin_panel.py को उसी फोल्डर में रखें
from database import create_tables, add_user, save_pending_payment, approve_and_assign_key, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Logging सेटअप
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id, update.effective_user.username or "No Username")
    
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if str(user_id) == ADMIN_ID:
        keyboard.append(["🛠 Admin Panel"])
        
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    # 1. पेमेंट फोटो हैंडलिंग
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

    # 2. बटन्स लॉजिक (यहाँ सब कुछ कवर है)
    if str(user_id) == ADMIN_ID and text == "🛠 Admin Panel":
        await update.message.reply_text("Admin:", reply_markup=admin_keyboard())
    elif text == "🎮 Games":
        await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
    elif text == "🔑 My Keys":
        keys = get_user_keys(user_id)
        if keys:
            msg = "\n".join([f"🎮 {k[0]} | {k[1]} | Key: `{k[2]}`" for k in keys])
            await update.message.reply_text(f"Your Keys:\n{msg}", parse_mode="Markdown")
        else: await update.message.reply_text("No keys found.")
    elif text in GAME_PLANS:
        context.user_data["u_game"] = text
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"plan_{p}")] for p, pr in GAME_PLANS[text].items()]
        await update.message.reply_text("Select plan:", reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update.message.reply_text("Please use the menu buttons.")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("plan_"):
        context.user_data["u_plan"] = query.data.split("_")[1]
        if os.path.exists("qr.JPG"):
            with open("qr.JPG", "rb") as qr:
                await query.message.reply_photo(photo=qr, caption="Send screenshot of payment.")
        else: await query.message.reply_text("QR not found.")
            
    elif query.data.startswith("acc_"):
        pay_id = int(query.data.split("_")[1])
        key, uid = approve_and_assign_key(pay_id)
        if key:
            await context.bot.send_message(uid, f"✅ Key: `{key}`", parse_mode="Markdown")
            await query.edit_message_caption(caption="✅ Approved.")
        else: await query.edit_message_caption(caption="❌ No stock or Invalid payment.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build() # PicklePersistence हटाया, अब डेटाबेस है
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
