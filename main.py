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
    
    # Reset internal user states safely on start
    context.user_data.clear()

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
        context.user_data.clear()  # Clear state cleanly
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
            await update.message.reply_text(
                "👑 Admin Control Panel",
                reply_markup=admin_keyboard() # Keep inline markup from your imported module
            )
            # Send a companion reply keyboard to exit or browse statistics natively
            await update.message.reply_text(
                "Admin Quick Navigation Active:",
                reply_markup=ReplyKeyboardMarkup([
                    ["🔑 Add Keys", "📦 Stock"],
                    ["👥 Total Users", "💰 Purchases"],
                    ["📊 Statistics", "🔙 Back to Main"]
                ], resize_keyboard=True)
            )
            return

        # Passive State: Processing added key text
        if context.user_data.get("adding_key"):
            save_key(text)
            context.user_data["adding_key"] = False
            await update.message.reply_text("✅ Key Added Successfully", reply_markup=get_main_keyboard(user.id))
            return

        if text == "🔑 Add Keys":
            context.user_data["adding_key"] = True
            await update.message.reply_text("🔑 Send the license key code string layout directly:", reply_markup=get_back_keyboard())
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
        await payment_info(update)

    elif text.startswith("👑 1 WEEK"):
        context.user_data["plan"] = "1 WEEK"
        context.user_data["amount"] = "800"
        await payment_info(update)

    elif text.startswith("👑 1 MONTH"):
        context.user_data["plan"] = "1 MONTH"
        context.user_data["amount"] = "2000"
        await payment_info(update)

    elif text == "✅ I've Paid":
        plan = context.user_data.get("plan")
        amount = context.user_data.get("amount")

        if not plan or not amount:
            await update.message.reply_text("❌ No active order state found. Please select a dynamic package plan first.", reply_markup=get_main_keyboard(user.id))
            return

        payment_id = save_payment(user.id, plan, amount)
        await update.message.reply_text("✅ Payment request captured and pushed to validation admins.", reply_markup=get_main_keyboard(user.id))

        if ADMIN_ID:
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Accept", callback_data=f"accept_{payment_id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{payment_id}")
                ]
            ])
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    "🔔 New Payment Request Pending Evaluation\n\n"
                    f"👤 User: {user.mention_html()} ({user.id})\n"
                    f"👑 Plan Product Chosen: {plan}\n"
                    f"💰 Amount Sent: ₹{amount}"
                ),
                reply_markup=buttons,
                parse_mode="HTML"
            )

    elif text == "📞 Support":
        await update.message.reply_text("📞 Support Channels\n\nFor service inquiries or help context, chat with @YourAdminHandle here.", reply_markup=get_back_keyboard())

    elif text == "👤 Profile":
        await update.message.reply_text(
            f"👤 User Profile Context\n\n"
            f"🏷️ Unique Account ID: <code>{user.id}</code>\n"
            f"👤 Username Address: @{user.username or 'None Set'}",
            parse_mode="HTML"
        )

    elif text == "🔑 My Keys":
        await update.message.reply_text("🔑 Your purchased licenses keys will populate below once verified:")

    elif text == "💳 Payment":
        await update.message.reply_text("💳 Please head to: 🎮 Games → 👑 KING iOS to provision dynamic item parameters directly.")


async def payment_info(update: Update):
    await update.message.reply_text(
        "💳 Payment Instructions Details\n\n"
        "Send exact money transfer amount to your upi/wallet identifier.\n"
        "Once payment confirmation settles, click the button underneath:",
        reply_markup=ReplyKeyboardMarkup([["✅ I've Paid"], ["🔙 Back to Games"]], resize_keyboard=True)
    )


async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data

    if data.startswith("accept_"):
        payment_id = int(data.split("_")[1])
        update_payment_status(payment_id, "approved")
        await query.edit_message_text("✅ Payment Approved & Account Updated Successfully.")

    elif data.startswith("reject_"):
        payment_id = int(data.split("_")[1])
        update_payment_status(payment_id, "rejected")
        await query.edit_message_text("❌ Payment Request Rejected / Denied.")


def main():
    if not TOKEN:
        raise ValueError("Critical Token Missing! Assign valid BOT_TOKEN env configurations.")

    create_tables()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CallbackQueryHandler(admin_action))

    print("Bot loop started successfully. Long-polling channels linked.")
    app.run_polling()


if __name__ == "__main__":
    main()
