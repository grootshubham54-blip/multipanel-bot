import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    ContextTypes, filters, PicklePersistence
)
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7908981593"

# Persistence सेटअप (ताकि डेटा रिस्टार्ट के बाद भी रहे)
my_persistence = PicklePersistence(filepath="bot_data.pickle")

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "199", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1300"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "129", "1 Week": "499", "1 Month": "999"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": {"1 Day": "150", "1 Week": "600", "1 Month": "1600"}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    add_user(update.effective_user.id, update.effective_user.username or "No Username")
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID: keyboard.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    
    # पेमेंट फोटो हैंडलिंग
    if update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("u_game", "Unknown")
        p = context.user_data.get("u_plan", "Unknown")
        context.user_data[f"pay_{user_id}"] = {"game": g, "plan": p}
        
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, 
            caption=f"👤 Payment from {user_id}\n🎮 {g} - {p}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve", callback_data=f"acc_{user_id}")]]))
        await update.message.reply_text("✅ Payment sent!")
        return

    # एडमिन और अन्य लॉजिक...
    if user_id == ADMIN_ID and text == "🛠 Admin Panel":
        await update.message.reply_text("Admin:", reply_markup=admin_keyboard())
    elif text == "🎮 Games":
        await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_PLANS:
        context.user_data["u_game"] = text
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"plan_{p}")] for p, pr in GAME_PLANS[text].items()]
        await update.message.reply_text("Select plan:", reply_markup=InlineKeyboardMarkup(kb))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("plan_"):
        context.user_data["u_plan"] = query.data.split("_")[1]
        with open("qr.JPG", "rb") as qr:
            await query.message.reply_photo(photo=qr, caption="Send screenshot.")
            
    elif query.data.startswith("acc_"):
        uid = int(query.data.split("_")[1])
        pay_info = context.user_data.get(f"pay_{uid}")
        if pay_info:
            key = approve_and_assign_key(uid, pay_info["game"], pay_info["plan"])
            if key:
                await context.bot.send_message(uid, f"✅ Key: `{key}`", parse_mode="Markdown")
                await query.edit_message_caption(caption="✅ Approved.")
            else: await query.edit_message_caption(caption="❌ No stock.")

def main():
    create_tables()
    # Persistence जोड़कर बोट को स्टेबल किया
    app = Application.builder().token(TOKEN).persistence(my_persistence).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
