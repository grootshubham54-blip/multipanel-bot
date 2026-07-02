Import os
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
from database import (
    create_tables,
    add_user,
    update_payment_status,
    save_key,
    get_stock,
    get_total_users,
    get_total_purchases
)
from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# CONFIGURATION
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 7908981593)) # Default fallback

# --- KEYBOARD MARKUPS ---
def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [
        ["🎮 Games", "🔑 My Keys"],
        ["📞 Support", "👤 Profile"],
        ["💳 Payment"]
    ]
    if user_id == ADMIN_ID:
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard(target: str = "Main") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[f"🔙 Back to {target}"]], resize_keyboard=True)

def get_payment_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["❌ Cancel Payment"]], resize_keyboard=True)

# --- START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text(
        "👑 Welcome to KING iOS Bot\n\nSelect an option:",
        reply_markup=get_main_keyboard(user.id)
    )

# --- MESSAGE HANDLER (All logic here) ---
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text in ["🔙 Back to Main", "❌ Cancel Payment"]:
        context.user_data.clear()
        await update.message.reply_text("👑 Main Menu", reply_markup=get_main_keyboard(user.id))
        return

    # ADMIN LOGIC (ENGLISH)
    if user.id == ADMIN_ID:
        if text == "⚙️ Admin Panel":
            await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
            return
        elif text == "🔑 Add Keys":
            context.user_data["adding_key"] = True
            await update.message.reply_text("🎯 Select game to add keys:", reply_markup=admin_game_selection_keyboard())
            return
        # [ADD REST OF YOUR ADMIN LOGIC HERE AS IT WAS...]

    # USER PLANS LOGIC (KEEP AS IS, IT IS WORKING FINE)
    # ... (Your plan logic remains here) ...

# --- PHOTO HANDLER ---
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.user_data.get("awaiting_screenshot"):
        await update.message.reply_text("❌ Please select a plan first.")
        return

    plan = context.user_data.get("plan", "Unknown")
    amount = context.user_data.get("amount", "0")
    payment_id = save_payment(user.id, plan, amount)
    context.user_data["awaiting_screenshot"] = False

    await update.message.reply_text("✅ Screenshot received! Admin will verify it soon.")

    # Send to Admin with English Buttons
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Accept", callback_data=f"accept_{payment_id}_{user.id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{payment_id}_{user.id}")
        ]
    ])
    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"🔔 New Payment Verification\n\n👤 User: {user.mention_html()}\n💰 Amount: ₹{amount}\n🆔 ID: {payment_id}",
        reply_markup=buttons,
        parse_mode="HTML"
    )

# --- ADMIN ACTION (FIXED) ---
async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    action, payment_id, user_id = parts[0], int(parts[1]), int(parts[2])

    if action == "accept":
        update_payment_status(payment_id, "approved")
        await query.edit_message_caption(caption=f"✅ Approved. Key sent to user {user_id}.")
        await context.bot.send_message(user_id, "🎉 Payment Verified! Your key: `KING-LICENSE-XYZ`")
    else:
        update_payment_status(payment_id, "rejected")
        await query.edit_message_caption(caption=f"❌ Rejected. User {user_id} notified.")
        await context.bot.send_message(user_id, "❌ Payment Rejected by Admin.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(CallbackQueryHandler(admin_action))
    app.run_polling()

if __name__ == "__main__":
    main()