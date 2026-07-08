import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import (
    create_tables, save_user, is_banned, save_order, get_order, approve_order, 
    reject_order, save_key, get_user_keys, get_stock, get_total_users
)

# Configuration
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7908981593"))
PAYMENT_QR = os.getenv("PAYMENT_QR_FILE_ID", "YOUR_QR_FILE_ID")

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": 200, "1 Week": 800, "1 Month": 2000},
    "WIN iOS": {"1 Day": 200, "1 Week": 600, "1 Month": 1200},
    "VISION": {"1 Day": 199, "1 Week": 799, "1 Month": 2199},
    "RAGE": {"1 Day": 150, "1 Week": 599, "1 Month": 1499}
}

# --- KEYBOARDS ---
def main_keyboard(uid):
    buttons = [["🎮 Games", "🔑 My Keys"], ["👤 Profile", "📞 Support"], ["💳 Payment"]]
    if uid == ADMIN_ID: buttons.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def admin_keyboard():
    return ReplyKeyboardMarkup([["📦 Stock", "🔑 Add Keys"], ["👥 Total Users", "🔙 Back to Home"]], resize_keyboard=True)

# --- CALLBACK HANDLER (Buttons) ---
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Admin: Approve/Reject Logic
    if data.startswith(("approve|", "reject|")):
        if query.from_user.id != ADMIN_ID: return
        order_id = int(data.split("|")[1])
        order = get_order(order_id)
        
        if not order: await query.edit_message_text("❌ Order not found"); return
        
        if data.startswith("approve|"):
            key = approve_order(order_id, order["game"], order["plan"], order["user_id"])
            if key:
                await context.bot.send_message(order["user_id"], f"✅ Payment Approved!\n\n🎮 {order['game']}\n📦 {order['plan']}\n\n🔑 Key:\n`{key}`", parse_mode="Markdown")
                await query.edit_message_text(f"✅ Approved. Key sent to user.")
            else: await query.edit_message_text("❌ Error: Stock Empty!")
        else:
            reject_order(order_id)
            await context.bot.send_message(order["user_id"], "❌ Payment Rejected by Admin.")
            await query.edit_message_text("❌ Rejected.")
        return

    # User: Game/Plan Logic
    if data.startswith("game|"):
        game = data.split("|")[1]
        context.user_data["game"] = game
        buttons = [[InlineKeyboardButton(f"{plan} - ₹{price}", callback_data=f"plan|{plan}")] for plan, price in GAME_PLANS[game].items()]
        await query.edit_message_text(f"🎮 {game}\n\nSelect Plan:", reply_markup=InlineKeyboardMarkup(buttons))
    elif data.startswith("plan|"):
        plan = data.split("|")[1]
        context.user_data["plan"] = plan
        await context.bot.send_photo(query.from_user.id, PAYMENT_QR, caption=f"💳 Payment\n\n🎮 {context.user_data['game']}\n📦 {plan}\n\nपेमेंट का स्क्रीनशॉट यहाँ भेजें।")

# --- MESSAGE HANDLER ---
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text or ""

    # Customer Screenshot Logic
    if update.message.photo:
        if "game" not in context.user_data: await update.message.reply_text("❌ पहले 'Games' से गेम चुनें।"); return
        order_id = save_order(user.id, user.username, context.user_data["game"], context.user_data["plan"])
        
        # एडमिन को बटन के साथ भेजना
        buttons = [[InlineKeyboardButton("✅ Approve", callback_data=f"approve|{order_id}"), InlineKeyboardButton("❌ Reject", callback_data=f"reject|{order_id}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, 
                                     caption=f"📦 New Payment!\nID: {order_id}\nUser: {user.first_name} (@{user.username})\nGame: {context.user_data['game']}\nPlan: {context.user_data['plan']}", 
                                     reply_markup=InlineKeyboardMarkup(buttons))
        
        await update.message.reply_text("✅ स्क्रीनशॉट एडमिन को भेज दिया गया है।"); context.user_data.clear(); return

    # Admin & User Text Commands
    if user.id == ADMIN_ID:
        if text in ["🛠 Admin Panel", "🔙 Back to Admin"]: await update.message.reply_text("⚙️ Admin Panel", reply_markup=admin_keyboard()); return
        if text == "🔙 Back to Home": await update.message.reply_text("👋 Welcome Admin!", reply_markup=main_keyboard(user.id)); return
        if text == "📦 Stock":
            stock = get_stock()
            msg = "📦 STOCK\n" + "".join([f"{g} | {p} | {c}\n" for g,p,c in stock]) if stock else "❌ Empty"
            await update.message.reply_text(msg); return
        if text == "🔑 Add Keys": context.user_data["admin_mode"] = "game"; await update.message.reply_text("Select Game:"); return
        # ... (Add Key logic remains as before)

    if text == "🎮 Games":
        buttons = [[InlineKeyboardButton(g, callback_data=f"game|{g}")] for g in GAME_PLANS]
        await update.message.reply_text("🎮 Games:", reply_markup=InlineKeyboardMarkup(buttons))
    elif text == "🔑 My Keys":
        keys = get_user_keys(user.id)
        msg = "🔑 Your Keys:\n\n" + "".join([f"🎮 {g}\n📦 {p}\n🔑 `{k}`\n\n" for g,p,k in keys]) if keys else "❌ No Keys Found"
        await update.message.reply_text(msg, parse_mode="Markdown")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start := lambda u, c: u.message.reply_text("👋 Welcome!", reply_markup=main_keyboard(u.effective_user.id))))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
