import os
import logging

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ध्यान दें: सुनिश्चित करें कि database.py में save_order फंक्शन मौजूद है
from database import (
    create_tables,
    save_user,
    is_banned,
    save_order 
)

# =========================
# LOGGING & CONFIG
# =========================
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7908981593"))
PAYMENT_QR = os.getenv("PAYMENT_QR_FILE_ID", "YOUR_QR_FILE_ID")

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": 200, "1 Week": 800, "1 Month": 2000},
    "WIN iOS": {"1 Day": 200, "1 Week": 600, "1 Month": 1200},
    "VISION": {"1 Day": 199, "1 Week": 799, "1 Month": 2199},
    "RAGE": {"1 Day": 150, "1 Week": 599, "1 Month": 1499}
}

# =========================
# KEYBOARDS
# =========================
def main_keyboard(user_id):
    buttons = [["🎮 Games", "🔑 My Keys"], ["👤 Profile", "📞 Support"], ["💳 Payment"]]
    if user_id == ADMIN_ID:
        buttons.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# =========================
# COMMANDS & HANDLERS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_banned(user.id): return
    save_user(user.id, user.username)
    await update.message.reply_text("👋 Welcome to Game Key Shop\n\nChoose an option below 👇", reply_markup=main_keyboard(user.id))

async def show_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton(game, callback_data=f"game|{game}")] for game in GAME_PLANS]
    await update.message.reply_text("🎮 Select Game:", reply_markup=InlineKeyboardMarkup(buttons))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("game|"):
        game = data.split("|", 1)[1]
        context.user_data["game"] = game
        buttons = [[InlineKeyboardButton(f"{plan} - ₹{price}", callback_data=f"plan|{plan}")] for plan, price in GAME_PLANS[game].items()]
        await query.edit_message_text(f"🎮 {game}\n\nSelect Plan:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("plan|"):
        plan = data.split("|", 1)[1]
        context.user_data["plan"] = plan
        game = context.user_data.get("game")
        price = GAME_PLANS[game][plan]
        await context.bot.send_photo(chat_id=query.from_user.id, photo=PAYMENT_QR, caption=f"💳 Payment Details\n\n🎮 Game: {game}\n📦 Plan: {plan}\n💰 Amount: ₹{price}\n\nPayment के बाद Screenshot भेजें.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_banned(user.id): return

    # पेमेंट स्क्रीनशॉट हैंडलिंग
    if update.message.photo:
        if "game" not in context.user_data:
            await update.message.reply_text("❌ पहले Game और Plan select करें.")
            return

        game = context.user_data["game"]
        plan = context.user_data["plan"]
        order_id = save_order(user_id=user.id, username=user.username, game=game, plan=plan)

        buttons = [[InlineKeyboardButton("✅ Approve", callback_data=f"approve|{order_id}"), InlineKeyboardButton("❌ Reject", callback_data=f"reject|{order_id}")]]
        
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=f"💰 New Payment\n\n🆔 Order ID: {order_id}\n👤 User: {user.id}\n🎮 Game: {game}\n📦 Plan: {plan}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await update.message.reply_text("✅ Payment screenshot sent to Admin.")
        context.user_data.clear()
        return

    # टेक्स्ट कमांड्स
    text = update.message.text
    if text == "🎮 Games": await show_games(update, context)
    elif text == "👤 Profile": await update.message.reply_text(f"👤 Profile\n\nID: {user.id}\nUsername: @{user.username}")
    elif text == "📞 Support": await update.message.reply_text("📞 Support:\n@YourAdminUsername")
    elif text == "💳 Payment": await update.message.reply_text("🎮 पहले Game चुनें और Plan खरीदें.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    # Photo और Text दोनों को हैंडल करने के लिए filters का उपयोग
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    print("Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()
