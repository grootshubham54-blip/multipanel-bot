import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import (
    create_tables, save_user, is_banned, save_order, get_order, approve_order, 
    reject_order, save_key, get_user_keys, get_stock, get_total_users
)
# अब यहाँ से import सही काम करेगा क्योंकि आपने admin_keyboard.py बना ली है
from admin_keyboard import (
    admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard
)

# Configuration
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN: raise ValueError("BOT_TOKEN missing")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7908981593"))
PAYMENT_QR = os.getenv("PAYMENT_QR_FILE_ID", "YOUR_QR_FILE_ID")

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": 200, "1 Week": 800, "1 Month": 2000},
    "WIN iOS": {"1 Day": 200, "1 Week": 600, "1 Month": 1200},
    "VISION": {"1 Day": 199, "1 Week": 799, "1 Month": 2199},
    "RAGE": {"1 Day": 150, "1 Week": 599, "1 Month": 1499}
}

async def error_handler(update, context): logging.error("BOT ERROR", exc_info=context.error)

def main_keyboard(uid):
    buttons = [["🎮 Games", "🔑 My Keys"], ["👤 Profile", "📞 Support"], ["💳 Payment"]]
    if uid == ADMIN_ID: buttons.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

async def start(update: Update, context):
    user = update.effective_user
    if is_banned(user.id): return
    save_user(user.id, user.username)
    await update.message.reply_text(f"👋 Welcome {user.first_name}", reply_markup=main_keyboard(user.id))

async def callback_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith(("approve|", "reject|")):
        if query.from_user.id != ADMIN_ID: return
        order_id = int(data.split("|")[1])
        order = get_order(order_id)
        if not order or order["status"] != "pending": await query.edit_message_text("❌ Invalid or processed."); return
        
        if data.startswith("approve|"):
            key = approve_order(order_id, order["game"], order["plan"], order["user_id"])
            if key:
                await context.bot.send_message(order["user_id"], f"✅ Payment Approved\n\n🎮 {order['game']}\n📦 {order['plan']}\n\n🔑 Key:\n`{key}`", parse_mode="Markdown")
                await query.edit_message_text("✅ Approved & Key Sent")
            else: await query.edit_message_text("❌ Stock Empty")
        else:
            reject_order(order_id)
            await context.bot.send_message(order["user_id"], "❌ Payment Rejected")
            await query.edit_message_text("❌ Rejected")
        return

    if data.startswith("game|"):
        game = data.split("|")[1]
        context.user_data["game"] = game
        buttons = [[InlineKeyboardButton(f"{plan} - ₹{price}", callback_data=f"plan|{plan}")] for plan, price in GAME_PLANS[game].items()]
        await query.edit_message_text(f"🎮 {game}\n\nSelect Plan", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("plan|"):
        plan = data.split("|")[1]
        context.user_data["plan"] = plan
        await context.bot.send_photo(query.from_user.id, PAYMENT_QR, caption=f"💳 Payment\n\n🎮 {context.user_data['game']}\n📦 {plan}\n\nस्क्रीनशॉट भेजें।")

async def message_handler(update, context):
    user = update.effective_user
    if update.message.photo:
        if "game" not in context.user_data: await update.message.reply_text("❌ पहले Game select करें"); return
        order_id = save_order(user.id, user.username, context.user_data["game"], context.user_data["plan"])
        buttons = [[InlineKeyboardButton("✅ Approve", callback_data=f"approve|{order_id}"), InlineKeyboardButton("❌ Reject", callback_data=f"reject|{order_id}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"📦 New Payment\nID: {order_id}\nUser: {user.id}\nGame: {context.user_data['game']}\nPlan: {context.user_data['plan']}", reply_markup=InlineKeyboardMarkup(buttons))
        await update.message.reply_text("✅ Screenshot Admin को भेज दिया गया"); context.user_data.clear(); return

    text = update.message.text or ""

    if user.id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("⚙️ Admin Panel", reply_markup=admin_keyboard()); return
        if text == "📦 Stock":
            stock = get_stock()
            if not stock: await update.message.reply_text("❌ Stock Empty"); return
            msg = "📦 STOCK\n\n"
            for g,p,c in stock: msg += f"{g} | {p} | {c}\n"
            await update.message.reply_text(msg); return
        if text == "👥 Total Users": await update.message.reply_text(f"👥 Users: {get_total_users()}"); return
        if text == "🔑 Add Keys": context.user_data["admin_mode"] = "game"; await update.message.reply_text("Select Game", reply_markup=admin_game_selection_keyboard()); return
        
        if context.user_data.get("admin_mode") == "game":
            if text not in GAME_PLANS: await update.message.reply_text("❌ Invalid Game"); return
            context.user_data.update({"add_game": text, "admin_mode": "plan"}); await update.message.reply_text("Select Plan", reply_markup=admin_plan_selection_keyboard()); return
        if context.user_data.get("admin_mode") == "plan": context.user_data.update({"add_plan": text, "admin_mode": "keys"}); await update.message.reply_text("Send Keys"); return
        if context.user_data.get("admin_mode") == "keys":
            for k in text.split("\n"):
                if k.strip(): save_key(context.user_data["add_game"], context.user_data["add_plan"], k.strip())
            context.user_data.clear(); await update.message.reply_text("✅ Keys Added", reply_markup=admin_keyboard()); return

    if text == "🎮 Games":
        buttons = [[InlineKeyboardButton(g, callback_data=f"game|{g}")] for g in GAME_PLANS]
        await update.message.reply_text("Select Game", reply_markup=InlineKeyboardMarkup(buttons))
    elif text == "🔑 My Keys":
        keys = get_user_keys(user.id)
        if not keys: await update.message.reply_text("❌ No Keys"); return
        msg = "🔑 Your Keys\n\n"
        for g,p,k in keys: msg += f"{g}\n{p}\n`{k}`\n\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    elif text == "👤 Profile": await update.message.reply_text(f"ID: {user.id}")
    elif text == "📞 Support": await update.message.reply_text("@YourAdminUsername")
    elif text == "💳 Payment": await update.message.reply_text("🎮 Games से plan select करें")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_error_handler(error_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
