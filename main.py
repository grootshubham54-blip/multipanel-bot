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

from database import (
    create_tables,
    add_user,
    update_payment_status,
    save_key,
    get_stock,
    get_total_users,
    get_total_purchases
)

# Note: Ensure your database module has a function like get_one_key() 
# or implement a function to fetch and remove/mark a key as used.
# For now, we will simulate or use a placeholders where needed.

from payment import save_payment
from admin_panel import admin_keyboard

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Keyboard Markups
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()  # Reset states Safely
    add_user(user.id, user.username or "No Username")

    await update.message.reply_text(
        "👑 Welcome to KING iOS Bot\n\nSelect an option from below:",
        reply_markup=get_main_keyboard(user.id)
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # GLOBAL BACK BUTTON ROUTING
    if text == "🔙 Back to Main":
        context.user_data.clear()
        await update.message.reply_text("👑 Main Menu", reply_markup=get_main_keyboard(user.id))
        return

    if text == "🔙 Back to Games":
        await update.message.reply_text(
            "🎮 Games\n\nSelect Game:",
            reply_markup=ReplyKeyboardMarkup([["👑 KING iOS"], ["🔙 Back to Main"]], resize_keyboard=True)
        )
        return

    # --- ADMIN ROUTES ---
    if user.id == ADMIN_ID:
        if text == "⚙️ Admin Panel":
            await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
            await update.message.reply_text(
                "Admin Quick Navigation Active:",
                reply_markup=ReplyKeyboardMarkup([
                    ["🔑 Add Keys", "📦 Stock"],
                    ["👥 Total Users", "💰 Purchases"],
                    ["📊 Statistics", "🔙 Back to Main"]
                ], resize_keyboard=True)
            )
            return

        if context.user_data.get("adding_key"):
            save_key(text)
            context.user_data["adding_key"] = False
            await update.message.reply_text("✅ Key Added Successfully", reply_markup=get_main_keyboard(user.id))
            return

        if text == "🔑 Add Keys":
            context.user_data["adding_key"] = True
            await update.message.reply_text("🔑 Send the license key code string directly:", reply_markup=get_back_keyboard())
            return

        elif text == "📦 Stock":
            await update.message.reply_text(f"📦 Available Keys: {get_stock()}")
            return

        elif text == "👥 Total Users":
            await update.message.reply_text(f"👥 Total Registered Users: {get_total_users()}")
            return

        elif text == "💰 Purchases":
            await update.message.reply_text(f"💰 Total Complete Purchases: {get_total_purchases()}")
            return

        elif text == "📊 Statistics":
            await update.message.reply_text(
                "📊 System Statistics\n\n"
                f"👥 Users: {get_total_users()}\n"
                f"📦 Stock: {get_stock()}\n"
                f"💰 Purchases: {get_total_purchases()}"
            )
            return

    # --- CORE USER MENUS ---
    if text == "🎮 Games":
        await update.message.reply_text(
            "🎮 Games\n\nSelect Game:",
            reply_markup=ReplyKeyboardMarkup([["👑 KING iOS"], ["🔙 Back to Main"]], resize_keyboard=True)
        )

    elif text == "👑 KING iOS":
        await update.message.reply_text(
            "👑 KING iOS Plans:",
            reply_markup=ReplyKeyboardMarkup([
                ["👑 1 DAY - ₹200"],
                ["👑 1 WEEK - ₹800"],
                ["👑 1 MONTH - ₹2000"],
                ["🔙 Back to Games"]
            ], resize_keyboard=True)
        )
        
    elif text.startswith("👑 1 DAY"):
        context.user_data["plan"] = "1 DAY"
        context.user_data["amount"] = "200"
        context.user_data["awaiting_screenshot"] = True  # Set screenshot flow state
        await payment_info(update, context)

    elif text.startswith("👑 1 WEEK"):
        context.user_data["plan"] = "1 WEEK"
        context.user_data["amount"] = "800"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)

    elif text.startswith("👑 1 MONTH"):
        context.user_data["plan"] = "1 MONTH"
        context.user_data["amount"] = "2000"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)

    elif text == "📞 Support":
        await update.message.reply_text("📞 Support Channels\n\nContact Admin at @YourAdminHandle.", reply_markup=get_back_keyboard())

    elif text == "👤 Profile":
        await update.message.reply_text(
            f"👤 User Profile Context\n\n"
            f"🏷️ Unique Account ID: <code>{user.id}</code>\n"
            f"👤 Username Address: @{user.username or 'None Set'}",
            parse_mode="HTML"
        )

    elif text == "🔑 My Keys":
        await update.message.reply_text("🔑 Your purchased licenses keys will populate below once verified by admin.")

    elif text == "💳 Payment":
        await update.message.reply_text("💳 Please head to: 🎮 Games → 👑 KING iOS to select a plan.")


async def payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    qr_image_path = "qr.png" 
    plan = context.user_data.get("plan", "Unknown")
    amount = context.user_data.get("amount", "0")
    
    upi_id = "YOUR_UPI_ID@okaxis"  # Change this to your real UPI ID
    upi_link = f"upi://pay?pa={upi_id}&pn=KING_iOS&am={amount}&cu=INR"

    caption_text = (
        f"💳 *Payment Details*\n\n"
        f"👑 *Plan:* {plan}\n"
        f"💰 *Amount:* ₹{amount}\n\n"
        f"1. Scan the QR Code above to pay.\n"
        f"2. Or click this direct UPI link: [Pay Now]({upi_link})\n\n"
        f"📸 *Next Step:* Send the payment success screenshot directly into this chat now."
    )

    try:
        with open(qr_image_path, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=caption_text,
                parse_mode="Markdown",
                reply_markup=get_back_keyboard("Games")
            )
    except FileNotFoundError:
        await update.message.reply_text(
            caption_text + "\n\n*(Error: QR Code Image Not Found on Server)*",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard("Games")
        )


# HANDLER FOR RECEIVING THE SCREENSHOT PHOTO
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Check if user is actually in a payment process flow
    if not context.user_data.get("awaiting_screenshot"):
        await update.message.reply_text("❌ Please select a dynamic game plan first before sending any screenshots.")
        return

    plan = context.user_data.get("plan", "Unknown")
    amount = context.user_data.get("amount", "0")

    # Save payment row status dynamically as pending inside DB
    payment_id = save_payment(user.id, plan, amount)

    # Reset user state cleanly
    context.user_data["awaiting_screenshot"] = False

    await update.message.reply_text(
        "✅ Screenshot received! Your payment request has been sent to the admin for validation.",
        reply_markup=get_main_keyboard(user.id)
    )

    # Route screenshot straight to admin channel for verification
    if ADMIN_ID:
        # Capture the highest resolution photo sent by user
        photo_file_id = update.message.photo[-1].file_id

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Accept", callback_data=f"accept_{payment_id}_{user.id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{payment_id}_{user.id}")
            ]
        ])

        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_file_id,
            caption=(
                f"🔔 *New Payment Verification Request*\n\n"
                f"👤 *User:* {user.mention_html()} (ID: {user.id})\n"
                f"👑 *Plan Chosen:* {plan}\n"
                f"💰 *Amount To Verify:* ₹{amount}\n"
                f"🆔 *Payment ID:* {payment_id}"
            ),
            reply_markup=buttons,
            parse_mode="HTML"
        )


async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    parts = data.split("_")
    action = parts[0]
    payment_id = int(parts[1])
    user_id = int(parts[2])

    if action == "accept":
        update_payment_status(payment_id, "approved")
        
        # TODO: Fetch a real unused license key from your stock database here
        # Example: generated_key = get_unused_key_from_db()
        generated_key = "KING-XYZ-MOCK-LICENSE-KEY-12345" # Placeholder

        await query.edit_message_caption(
            caption=f"✅ Payment Approved! Key assigned & dispatched to user ID: {user_id}."
        )

        # Send Key instantly directly to the customer chat
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"🎉 *Payment Verified Successfully!*\n\n"
                    f"👑 Here is your official license key code:\n"
                    f"`{generated_key}`\n\n"
                    f"Thank you for purchasing!"
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to send automated message key directly to user: {e}")

    elif action == "reject":
        update_payment_status(payment_id, "rejected")
        await query.edit_message_caption(caption="❌ Payment Request Rejected / Denied.")

        # Notify the user instantly about denial status
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ Your payment request verification screenshot was rejected by the administrator. Please contact support."
            )
        except Exception as e:
            logger.error(f"Failed to alert user about rejected request status: {e}")


def main():
    if not TOKEN:
        raise ValueError("Critical Token Missing! Assign valid BOT_TOKEN env configurations.")

    create_tables()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Handler activated specifically when user uploads photo screenshots
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    
    app.add_handler(CallbackQueryHandler(admin_action))

    print("Bot loop started successfully. Long-polling channels linked.")
    app.run_polling()


if __name__ == "__main__":
    main()
