import os
import logging
from telegram import (
    Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
)
from database import (
    create_tables, save_user, is_banned, save_order, get_order, approve_order, reject_order, save_key
)
from admin_keyboard import (
    admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard
)

# =========================
# LOGGING & CONFIG
# =========================
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN missing")

ADMIN_ID = int(os.getenv("ADMIN_ID", "7908981593"))
PAYMENT_QR = os.getenv("PAYMENT_QR_FILE_ID", "YOUR_QR_FILE_ID")

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": 200, "1 Week": 800, "1 Month": 2000},
    "WIN iOS": {"1 Day": 200, "1 Week": 600, "1 Month": 1200},
    "VISION": {"1 Day": 199, "1 Week": 799, "1 Month": 2199},
    "RAGE": {"1 Day": 150, "1 Week": 599, "1 Month": 1499}
}

# =========================
# HANDLERS
# =========================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error("Exception:", exc_info=context.error)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_banned(user.id): return
    save_user(user.id, user.username)
    username = user.username or "No Username"
    await update.message.reply_text(f"👋 Welcome {username}!", reply_markup=main_keyboard(user.id))

def main_keyboard(user_id):
    buttons = [["🎮 Games", "🔑 My Keys"], ["👤 Profile", "📞 Support"], ["💳 Payment"]]
    if user_id == ADMIN_ID: buttons.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # Security check for Admin actions
    if data.startswith(("approve|", "reject|")) and query.from_user.id != ADMIN_ID:
        return

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
        await context.bot.send_photo(chat_id=query.from_user.id, photo=PAYMENT_QR, caption=f"💰 Amount: ₹{price}\n\nPayment के बाद Screenshot भेजें.")

    elif data.startswith("approve|"):
        order_id = int(data.split("|")[1])
        order = get_order(order_id)
        if not order: await query.edit_message_text("❌ Order not found."); return
        key = approve_order(order_id, order["game"], order["plan"])
        if key:
            await context.bot.send_message(order["user_id"], f"✅ Approved!\n🔑 Key: `{key}`", parse_mode="Markdown")
            await query.edit_message_text("✅ Approved & Key Sent.")
        else: await query.edit_message_text("❌ Key Stock Empty.")

    elif data.startswith("reject|"):
        order_id = int(data.split("|")[1])
        order = get_order(order_id)
        if order:
            reject_order(order_id)
            await context.bot.send_message(order["user_id"], "❌ Payment Rejected.")
        await query.edit_message_text("❌ Payment Rejected.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text or "" # Fix for Issue 1
    
    # Admin Panel Logic
    if text == "🛠 Admin Panel" and user.id == ADMIN_ID:
        await update.message.reply_text("⚙️ Admin Panel", reply_markup=admin_keyboard())
    elif text == "🔑 Add Keys" and user.id == ADMIN_ID:
        context.user_data["admin_mode"] = "select_game"
        await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard())
    elif context.user_data.get("admin_mode") == "select_game":
        if text not in GAME_PLANS: await update.message.reply_text("❌ Invalid Game"); return
        context.user_data.update({"add_game": text, "admin_mode": "select_plan"})
        await update.message.reply_text("Select Plan:", reply_markup=admin_plan_selection_keyboard())
    elif context.user_data.get("admin_mode") == "select_plan":
        context.user_data.update({"add_plan": text, "admin_mode": "send_keys"})
        await update.message.reply_text("🔑 अब Keys भेजें.")
    elif context.user_data.get("admin_mode") == "send_keys":
        for k in text.split("\n"): save_key(context.user_data["add_game"], context.user_data["add_plan"], k.strip())
        await update.message.reply_text("✅ Added", reply_markup=admin_keyboard()); context.user_data.clear()

    # User Logic
    elif update.message.photo:
        if "game" not in context.user_data: await update.message.reply_text("❌ Select Game first."); return
        order_id = save_order(user.id, user.username, context.user_data["game"], context.user_data["plan"])
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"New Payment: {order_id}", 
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅", callback_data=f"approve|{order_id}"), InlineKeyboardButton("❌", callback_data=f"reject|{order_id}")]]))
        await update.message.reply_text("✅ Sent to Admin."); context.user_data.clear()
    elif text == "🎮 Games": await show_games(update, context)
    elif text == "🔑 My Keys": await update.message.reply_text("🛠 Coming Soon!")

async def show_games(update, context):
    await update.message.reply_text("Select:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(g, callback_data=f"game|{g}")] for g in GAME_PLANS]))

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_error_handler(error_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
