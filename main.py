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

def admin_game_selection_keyboard():
    buttons = [["👑 KING iOS", "WIN iOS"], ["VISION", "RAGE"], ["🔙 Back to Admin"]]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def admin_plan_selection_keyboard():
    return ReplyKeyboardMarkup([["1 Day", "1 Week"], ["1 Month"], ["🔙 Back to Admin"]], resize_keyboard=True)

# --- HANDLERS ---
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
        if not order: await query.edit_message_text("❌ Order not found"); return
        
        if data.startswith("approve|"):
            key = approve_order(order_id, order["game"], order["plan"], order["user_id"])
            if key:
                await context.bot.send_message(order["user_id"], f"✅ Payment Approved\n\n🔑 Key: `{key}`", parse_mode="Markdown")
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
        await query.edit_message_text(f"🎮 {game}\n\nSelect Plan:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("plan|"):
        plan = data.split("|")[1]
        price = GAME_PLANS[context.user_data["game"]][plan]
        # यहाँ QR भेजने का फिक्स किया गया है
        await context.bot.send_photo(query.from_user.id, PAYMENT_QR, caption=f"💳 Payment\n\n🎮 {context.user_data['game']}\n📦 {plan}\n💰 ₹{price}\n\nपेमेंट का स्क्रीनशॉट भेजें।")

async def message_handler(update, context):
    user = update.effective_user
    text = update.message.text or ""

    if update.message.photo and "game" in context.user_data:
        order_id = save_order(user.id, user.username, context.user_data["game"], context.user_data["plan"])
        buttons = [[InlineKeyboardButton("✅ Approve", callback_data=f"approve|{order_id}"), InlineKeyboardButton("❌ Reject", callback_data=f"reject|{order_id}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"📦 New Order: {order_id}\nUser: {user.id}", reply_markup=InlineKeyboardMarkup(buttons))
        await update.message.reply_text("✅ स्क्रीनशॉट एडमिन को भेज दिया गया।"); context.user_data.clear(); return

    # Admin Logic
    if user.id == ADMIN_ID:
        if text == "🛠 Admin Panel" or text == "🔙 Back to Admin": await update.message.reply_text("⚙️ Admin Panel", reply_markup=admin_keyboard()); return
        if text == "🔙 Back to Home": await update.message.reply_text("👋 Welcome!", reply_markup=main_keyboard(user.id)); return
        if text == "📦 Stock":
            stock = get_stock()
            msg = "📦 STOCK\n" + "".join([f"{g} | {p} | {c}\n" for g,p,c in stock]) if stock else "❌ Empty"
            await update.message.reply_text(msg); return
        if text == "👥 Total Users": await update.message.reply_text(f"👥 Users: {get_total_users()}"); return
        if text == "🔑 Add Keys": context.user_data["admin_mode"] = "game"; await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard()); return
        
        if context.user_data.get("admin_mode"):
            if text == "🔙 Back to Admin": context.user_data.clear(); await update.message.reply_text("Cancelled.", reply_markup=admin_keyboard()); return
            if context.user_data["admin_mode"] == "game":
                if text not in GAME_PLANS: await update.message.reply_text("❌ Invalid Game"); return
                context.user_data.update({"add_game": text, "admin_mode": "plan"}); await update.message.reply_text("Select Plan:", reply_markup=admin_plan_selection_keyboard()); return
            if context.user_data["admin_mode"] == "plan":
                context.user_data.update({"add_plan": text, "admin_mode": "keys"}); await update.message.reply_text("🔑 Keys पेस्ट करें:"); return
            if context.user_data["admin_mode"] == "keys":
                for k in text.split("\n"):
                    if k.strip(): save_key(context.user_data["add_game"], context.user_data["add_plan"], k.strip())
                context.user_data.clear(); await update.message.reply_text("✅ Added!", reply_markup=admin_keyboard()); return

    # User Logic
    if text == "🎮 Games":
        buttons = [[InlineKeyboardButton(g, callback_data=f"game|{g}")] for g in GAME_PLANS]
        await update.message.reply_text("🎮 Games:", reply_markup=InlineKeyboardMarkup(buttons))
    elif text == "🔑 My Keys":
        keys = get_user_keys(user.id)
        msg = "🔑 Your Keys:\n\n" + "".join([f"🎮 {g}\n📦 {p}\n🔑 `{k}`\n\n" for g,p,k in keys]) if keys else "❌ No Keys"
        await update.message.reply_text(msg, parse_mode="Markdown")
    elif text == "👤 Profile": await update.message.reply_text(f"ID: {user.id}")
    elif text == "💳 Payment": await update.message.reply_text("🎮 'Games' बटन से अपना गेम चुनें।")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
