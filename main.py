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
            "🎮 Games\n\nSelect Game / Loader:",
            reply_markup=ReplyKeyboardMarkup([
                ["👑 KING iOS"],
                ["WINIOS", "NEXT IOS"],
                ["𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"],
                ["DOLPHIN IOS"],
                ["🔙 Back to Main"]
            ], resize_keyboard=True)
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
            "🎮 Games\n\nSelect Game / Loader:",
            reply_markup=ReplyKeyboardMarkup([
                ["👑 KING iOS"],
                ["WINIOS", "NEXT IOS"],
                ["𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"],
                ["DOLPHIN IOS"],
                ["🔙 Back to Main"]
            ], resize_keyboard=True)
        )

    # --- 1. 👑 KING iOS PLANS ---
    elif text == "👑 KING iOS":
        await update.message.reply_text(
            "👑 KING iOS Plans:",
            reply_markup=ReplyKeyboardMarkup([
                ["👑 KING iOS 1 DAY - ₹200"],
                ["👑 KING iOS 1 WEEK - ₹800"],
                ["👑 KING iOS 1 MONTH - ₹2000"],
                ["🔙 Back to Games"]
            ], resize_keyboard=True)
        )
    elif text == "👑 KING iOS 1 DAY - ₹200":
        context.user_data["plan"] = "KING iOS 1 DAY"
        context.user_data["amount"] = "200"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)
    elif text == "👑 KING iOS 1 WEEK - ₹800":
        context.user_data["plan"] = "KING iOS 1 WEEK"
        context.user_data["amount"] = "800"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)
    elif text == "👑 KING iOS 1 MONTH - ₹2000":
        context.user_data["plan"] = "KING iOS 1 MONTH"
        context.user_data["amount"] = "2000"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)

    # --- 2. WINIOS PLANS ---
    elif text == "WINIOS":
        await update.message.reply_text(
            "WINIOS Plans:",
            reply_markup=ReplyKeyboardMarkup([
                ["WINIOS 1 DAY - ₹199"],
                ["WINIOS 1 WEEK - ₹599"],
                ["WINIOS 1 MONTH - ₹1399"],
                ["🔙 Back to Games"]
            ], resize_keyboard=
