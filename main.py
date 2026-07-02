import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7908981593"

# आपकी अपडेटेड प्राइस लिस्ट
GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "199", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1300"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "129", "1 Week": "499", "1 Month": "999"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": {"1 Day": "150", "1 Week": "600", "1 Month": "1600"}
}

GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN", "NEXT IOS": "NEXT", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "MARS", "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": "DEAD"}
REV_GAME_MAP = {v: k for k, v in GAME_MAP.items()}
PLAN_MAP = {"1 Day": "1D", "1 Week": "1W", "1 Month": "1M"}
REV_PLAN_MAP = {"1D": "1 Day", "1W": "1 Week", "1M": "1 Month"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "No Username"
    add_user(update.effective_user.id, username)
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID: keyboard.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome! Select an option:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    state = context.user_data.get("state")

    # पेमेंट हैंडलिंग (बग फिक्स के साथ)
    if update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("u_game", "Unknown")
        p = context.user_data.get("u_plan", "Unknown")
        # सुरक्षित डेटा स्टोरेज (Callback Limit Fix)
        context.user_data[f"pay_{user_id}"] = {"game": g, "plan": p}
        
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, 
            caption=f"👤 Payment from {user_id}\n🎮 Game: {g}\n📦 Plan: {p}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve", callback_data=f"acc_{user_id}")]]))
        await update.message.reply_text("✅ Payment sent to admin!")
        return

    # एडमिन लॉजिक
    if user_id == ADMIN_ID and state:
        if state == "awaiting_game":
            context.user_data["add_game"] = text
            context.user_data["state"] = "awaiting_plan"
            await update.message.reply_text("Select plan:", reply_markup=admin_plan_selection_keyboard())
        elif state == "awaiting_plan":
            context.user_data["add_plan"] = text
            context.user_data["state"] = "awaiting_keys"
            await update.message.reply_text("Enter Keys (one per line):")
        elif state == "awaiting_keys":
            keys = [k.strip() for k in text.split("\n") if k.strip()]
            for key in keys: save_key(context.user_data["add_game"], key, context.user_data["add_plan"])
            context.user_data.clear()
            await update.message.reply_text("✅ Keys saved!", reply_markup=admin_keyboard())
        return

    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "🔑 Add Keys": 
            context.user_data["state"] = "awaiting_game"
            await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
        elif text == "📦 Stock":
            msg = "📦 Stock:\n" + "\n".join([f"{g}: {get_stock_count(g, '1 Day')} left" for g in GAME_PLANS])
            await update.message.reply_text(msg)
        return

    if text == "🎮 Games":
        await update.message.reply_text("Choose game:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_PLANS:
        context.user_data.update({"u_game": text})
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"plan_{p}")] for p, pr in GAME_PLANS[text].items()]
        await update.message.reply_text("Select plan:", reply_markup=InlineKeyboardMarkup(kb))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # बग फिक्स: लोडिंग स्पिनर हटाना
    data = query.data

    if data.startswith("plan_"):
        plan = data.split("_")[1]
        context.user_data["u_plan"] = plan
        with open("qr.JPG", "rb") as qr:
            await query.message.reply_photo(photo=qr, caption="Send screenshot of payment.")
    
    elif data.startswith("acc_"):
        uid = int(data.split("_")[1])
        pay_info = context.user_data.get(f"pay_{uid}")
        if pay_info:
            key = approve_and_assign_key(uid, pay_info["game"], pay_info["plan"])
            if key:
                await context.bot.send_message(uid, f"✅ Approved! Key: `{key}`", parse_mode="Markdown")
                await query.edit_message_caption(caption="✅ Approved.")
            else: await query.edit_message_caption(caption="❌ Out of stock.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
