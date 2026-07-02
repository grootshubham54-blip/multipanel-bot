Import os
import logging
import sqlite3

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
    get_total_purchases,
    DB_NAME
)

from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

# Railway पर ADMIN_ID सेट है तो वहां से उठाएगा, बैकअप के लिए 0 रखा है
ADMIN_ID = int(os.getenv("ADMIN_ID", 0)) 

# गेम के स्पेशल नामों को सुरक्षित शॉर्ट-कोड में बदलने के लिए मैपिंग
GAME_MAPPING = {
    "👑 KING iOS": "king",
    "WINIOS": "win",
    "NEXT IOS": "next",
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "mars",
    "𝘿𝙀𝘼𝘿𝙀𝙔𝙀": "dead",
    "DOLPHIN IOS": "dolphin"
}

# शॉर्ट-कोड से वापस असली नाम पाने के लिए रिवर्स मैपिंग
REVERSE_GAME_MAPPING = {v: k for k, v in GAME_MAPPING.items()}

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

def get_payment_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["❌ Cancel Payment"]], resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()  
    add_user(user.id, user.username or "No Username")

    await update.message.reply_text(
        "👑 Welcome to KING iOS Bot\n\nSelect an option from below:",
        reply_markup=get_main_keyboard(user.id)
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # --- BROADCAST FEATURE ---
    if context.user_data.get("broadcasting"):
        msg_to_send = text
        context.user_data["broadcasting"] = False
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        conn.close()

        count = 0
        for u in users:
            try:
                await context.bot.send_message(chat_id=u[0], text=f"📢 *Announcement:*\n\n{msg_to_send}", parse_mode="Markdown")
                count += 1
            except:
                continue
        
        await update.message.reply_text(f"✅ Announcement sent to {count} users!", reply_markup=admin_keyboard())
        return

    if text == "🔙 Back to Main" or text == "❌ Cancel Payment":
        context.user_data.clear()  
        await update.message.reply_text("👑 Main Menu", reply_markup=get_main_keyboard(user.id))
        return

    if text == "🔙 Back to Admin":
        context.user_data["adding_key"] = False
        context.user_data["checking_stock"] = False
        context.user_data["selected_game"] = None
        await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
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
            context.user_data.clear()
            await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
            return

        elif text == "📢 Broadcast":
            context.user_data["broadcasting"] = True
            await update.message.reply_text("📢 Send your announcement message now:", reply_markup=get_back_keyboard("Admin"))
            return

        if text == "🔑 Add Keys":
            context.user_data["adding_key"] = True
            context.user_data["checking_stock"] = False
            await update.message.reply_text("🎯 Select the game you want to add keys for:", reply_markup=admin_game_selection_keyboard())
            return

        elif text == "📦 Stock":
            context.user_data["checking_stock"] = True
            context.user_data["adding_key"] = False
            await update.message.reply_text("🎯 Select the game to check its individual stock:", reply_markup=admin_game_selection_keyboard())
            return

        GAMES_LIST = ["👑 KING iOS", "WINIOS", "NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀", "DOLPHIN IOS"]
        if text in GAMES_LIST:
            if context.user_data.get("adding_key"):
                context.user_data["selected_game"] = text
                await update.message.reply_text(f"🔑 Typing keys for [{text}].\n\nSend the license key string directly now:", reply_markup=get_back_keyboard("Admin"))
                return
            elif context.user_data.get("checking_stock"):
                stock_count = get_stock(text)
                await update.message.reply_text(f"📦 Available Keys for *{text}*: `{stock_count}`", parse_mode="Markdown", reply_markup=admin_game_selection_keyboard())
                return

        if context.user_data.get("adding_key") and context.user_data.get("selected_game"):
            game = context.user_data["selected_game"]
            save_key(game, text)
            await update.message.reply_text(f"✅ Key added successfully for [{game}]. Send next key or click Back to Admin.", reply_markup=get_back_keyboard("Admin"))
            return

        elif text == "👥 Total Users":
            await update.message.reply_text(f"👥 Total Registered Users: {get_total_users()}")
            return

        elif text == "💰 Purchases":
            await update.message.reply_text(f"💰 Total Complete Purchases: {get_total_purchases()}")
            return

        elif text == "📊 Statistics":
            total_stock = get_stock()
            await update.message.reply_text(
                "📊 *System Statistics*\n\n"
                f"👥 *Total Users:* {get_total_users()}\n"
                f"📦 *Total Combined Stock:* {total_stock}\n"
                f"💰 *Total Approved Purchases:* {get_total_purchases()}",
                parse_mode="Markdown"
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
        context.user_data["base_game"] = "👑 KING iOS"
        context.user_data["plan"] = "KING iOS 1 DAY"
        context.user_data["amount"] = "200"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)
    elif text == "👑 KING iOS 1 WEEK - ₹800":
        context.user_data["base_game"] = "👑 KING iOS"
        context.user_data["plan"] = "KING iOS 1 WEEK"
        context.user_data["amount"] = "800"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)
    elif text == "👑 KING iOS 1 MONTH - ₹2000":
        context.user_data["base_game"] = "👑 KING iOS"
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
            ], resize_keyboard=True)
        )
    elif text == "WINIOS 1 DAY - ₹199":
        context.user_data["base_game"] = "WINIOS"
        context.user_data["plan"] = "WINIOS 1 DAY"
        context.user_data["amount"] = "199"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)
    elif text == "WINIOS 1 WEEK - ₹599":
        context.user_data["base_game"] = "WINIOS"
        context.user_data["plan"] = "WINIOS 1 WEEK"
        context.user_data["amount"] = "599"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)
    elif text == "WINIOS 1 MONTH - ₹1399":
        context.user_data["base_game"] = "WINIOS"
        context.user_data["plan"] = "WINIOS 1 MONTH"
        context.user_data["amount"] = "1399"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)

    # --- 3. NEXT IOS PLANS ---
    elif text == "NEXT IOS":
        await update.message.reply_text(
            "NEXT IOS Plans:",
            reply_markup=ReplyKeyboardMarkup([
                ["NEXT IOS 1 DAY - ₹200"],
                ["NEXT IOS 1 WEEK - ₹799"],
                ["🔙 Back to Games"]
            ], resize_keyboard=True)
        )
    elif text == "NEXT IOS 1 DAY - ₹200":
        context.user_data["base_game"] = "NEXT IOS"
        context.user_data["plan"] = "NEXT IOS 1 DAY"
        context.user_data["amount"] = "200"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)
    elif text == "NEXT IOS 1 WEEK - ₹799":
        context.user_data["base_game"] = "NEXT IOS"
        context.user_data["plan"] = "NEXT IOS 1 WEEK"
        context.user_data["amount"] = "799"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)

    # --- 4. 𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫 PLANS ---
    elif text == "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫":
        await update.message.reply_text(
            "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫 Plans:",
            reply_markup=ReplyKeyboardMarkup([
                ["MARS 1 DAY - ₹120"],
                ["MARS 1 WEEK - ₹500"],
                ["MARS 1 MONTH - ₹999"],
                ["🔙 Back to Games"]
            ], resize_keyboard=True)
        )
    elif text == "MARS 1 DAY - ₹120":
        context.user_data["base_game"] = "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫"
        context.user_data["plan"] = "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫 1 DAY"
        context.user_data["amount"] = "120"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)
    elif text == "MARS 1 WEEK - ₹500":
        context.user_data["base_game"] = "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫"
        context.user_data["plan"] = "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫 1 WEEK"
        context.user_data["amount"] = "500"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)
    elif text == "MARS 1 MONTH - ₹999":
        context.user_data["base_game"] = "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫"
        context.user_data["plan"] = "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫 1 MONTH"
        context.user_data["amount"] = "999"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)

    # --- 5. 𝘿𝙀𝘼𝘿𝙀𝙔𝙀 PLANS ---
    elif text == "𝘿𝙀𝘼𝘿𝙀𝙔𝙀":
        await update.message.reply_text(
            "𝘿𝙀𝘼𝘿𝙀𝙔𝙀 Plans:",
            reply_markup=ReplyKeyboardMarkup([
                ["DEADEYE 1 DAY - ₹150"],
                ["DEADEYE 1 WEEK - ₹600"],
                ["DEADEYE 1 MONTH - ₹1500"],
                ["🔙 Back to Games"]
            ], resize_keyboard=True)
        )
    elif text == "DEADEYE 1 DAY - ₹150":
        context.user_data["base_game"] = "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"
        context.user_data["plan"] = "𝘿𝙀𝘼𝘿𝙀𝙔𝙀 1 DAY"
        context.user_data["amount"] = "150"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)
    elif text == "DEADEYE 1 WEEK - ₹600":
        context.user_data["base_game"] = "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"
        context.user_data["plan"] = "𝘿𝙀𝘼𝘿𝙀𝙔𝙀 1 WEEK"
        context.user_data["amount"] = "600"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)
    elif text == "DEADEYE 1 MONTH - ₹1500":
        context.user_data["base_game"] = "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"
        context.user_data["plan"] = "𝘿𝙀𝘼𝘿𝙀𝙔𝙀 1 MONTH"
        context.user_data["amount"] = "1500"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)

    # --- 6. DOLPHIN IOS PLANS ---
    elif text == "DOLPHIN IOS":
        await update.message.reply_text(
            "DOLPHIN IOS Plans:",
            reply_markup=ReplyKeyboardMarkup([
                ["DOLPHIN 1 DAY - ₹200"],
                ["DOLPHIN 1 WEEK - ₹700"],
                ["DOLPHIN 1 MONTH - ₹1599"],
                ["🔙 Back to Games"]
            ], resize_keyboard=True)
        )
    elif text == "DOLPHIN 1 DAY - ₹200":
        context.user_data["base_game"] = "DOLPHIN IOS"
        context.user_data["plan"] = "DOLPHIN IOS 1 DAY"
        context.user_data["amount"] = "200"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)
    elif text == "DOLPHIN 1 WEEK - ₹700":
        context.user_data["base_game"] = "DOLPHIN IOS"
        context.user_data["plan"] = "DOLPHIN IOS 1 WEEK"
        context.user_data["amount"] = "700"
        context.user_data["awaiting_screenshot"] = True
        await payment_info(update, context)
    elif text == "DOLPHIN 1 MONTH - ₹1599":
        context.user_data["base_game"] = "DOLPHIN IOS"
        context.user_data["plan"] = "DOLPHIN IOS 1 MONTH"
        context.user_data["amount"] = "1599"
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
        await update.message.reply_text("💳 Please head to: 🎮 Games to select a plan.")


async def payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    qr_image_path = os.path.join(current_dir, "67f1394a-82f8-4d58-b648-6edcb3417c66.jpeg")
    
    plan = context.user_data.get("plan", "Unknown")
    amount = context.user_data.get("amount", "0")
    
    upi_id = "YOUR_UPI_ID@okaxis"  
    upi_link = f"upi://pay?pa={upi_id}&pn=KING_iOS&am={amount}&cu=INR"

    caption_text = (
        f"💳 *Payment Details*\n\n"
        f"👑 *Plan:* {plan}\n"
        f"💰 *Amount:* ₹{amount}\n\n"
        f"1. Scan the QR Code above to pay.\n"
        f"2. Or click this direct UPI link: [Pay Now]({upi_link})\n\n"
        f"📸 *Next Step:* Send the payment success screenshot directly into this chat now.\n\n"
        f"💡 *Note:* If you want to change your mind, click the **❌ Cancel Payment** button below."
    )

    try:
        with open(qr_image_path, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=caption_text,
                parse_mode="Markdown",
                reply_markup=get_payment_keyboard()  
            )
    except FileNotFoundError:
        await update.message.reply_text(
            caption_text + f"\n\n*(Error: QR Code Image Not Found)*",
            parse_mode="Markdown",
            reply_markup=get_payment_keyboard()  
        )


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not context.user_data.get("awaiting_screenshot"):
        await update.message.reply_text("❌ Please select a game plan first before sending any screenshots.")
        return

    plan = context.user_data.get("plan", "Unknown")
    amount = context.user_data.get("amount", "0")
    base_game = context.user_data.get("base_game", "Unknown")

    payment_id = save_payment(user.id, plan, amount)
    context.user_data["awaiting_screenshot"] = False

    await update.message.reply_text(
        "✅ Screenshot received! Your payment request has been sent to the admin for validation.",
        reply_markup=get_main_keyboard(user.id)
    )

    if ADMIN_ID:
        photo_file_id = update.message.photo[-1].file_id
        
        # गेम के असली नाम को शॉर्ट-कोड में बदलें (ताकि 64 bytes से छोटा रहे)
        short_game = GAME_MAPPING.get(base_game, "king")

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Accept", callback_data=f"acc_{payment_id}_{user.id}_{short_game}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"rej_{payment_id}_{user.id}")
            ]
        ])

        try:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo_file_id,
                caption=(
                    f"🔔 *New Payment Verification Request*\n\n"
                    f"👤 *User:* {user.mention_html()} (ID: {user.id})\n"
                    f"🎮 *Game Category:* {base_game}\n"
                    f"👑 *Plan Chosen:* {plan}\n"
                    f"💰 *Amount To Verify:* ₹{amount}\n"
                    f"🆔 *Payment ID:* {payment_id}"
                ),
                reply_markup=buttons,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed sending validation request to Admin ID {ADMIN_ID}: {e}")


async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    parts = data.split("_")
    action = parts[0]
    payment_id = int(parts[1])
    user_id = int(parts[2])

    if action == "acc":
        short_game = parts[3] if len(parts) > 3 else "king"
        # शॉर्ट-कोड से वापस डाटाबेस के लिए असली नाम निकालें
        game_name = REVERSE_GAME_MAPPING.get(short_game, "👑 KING iOS")
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, key_code FROM keys WHERE game_name = ? AND is_used = 0 LIMIT 1", (game_name,))
        row = cursor.fetchone()
        
        if row:
            key_id, real_key = row
            cursor.execute("UPDATE keys SET is_used = 1 WHERE id = ?", (key_id,))
            conn.commit()
            conn.close()
            
            update_payment_status(payment_id, "approved")

            await query.edit_message_caption(
                caption=f"✅ Approved! Dispatched real key for [{game_name}] to User ID: {user_id}."
            )

            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"🎉 *Payment Verified Successfully!*\n\n"
                        f"🎮 *Game:* {game_name}\n"
                        f"👑 Here is your official license key code:\n"
                        f"`{real_key}`\n\n"
                        f"Thank you for purchasing!"
                    ),
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Failed to send key to user: {e}")
        else:
            conn.close()
            await query.edit_message_caption(
                caption=f"❌ ERROR: Cannot Approve! Stock is empty (Out of Keys) for [{game_name}]. Please add keys first!"
            )

    elif action == "rej":
        update_payment_status(payment_id, "rejected")
        await query.edit_message_caption(caption=f"❌ Payment Request Rejected for User ID: {user_id}.")

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ Your payment request verification screenshot was rejected by the administrator. Please contact support."
            )
        except Exception as e:
            logger.error(f"Failed to alert user: {e}")


def main():
    if not TOKEN:
        raise ValueError("Critical Token Missing! Assign valid BOT_TOKEN env configurations.")

    create_tables()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(CallbackQueryHandler(admin_action))

    print("Bot loop started successfully. Long-polling channels linked.")
    app.run_polling()


if __name__ == "__main__":
    main()