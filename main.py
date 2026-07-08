import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import (
    save_user, is_banned, save_order, get_order, approve_order, reject_order, 
    save_key, get_user_keys, get_stock, get_total_users
)
from admin_keyboard import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

# Configuration
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN missing in environment variables!")

ADMIN_ID = int(os.getenv("ADMIN_ID", "7908981593"))
PAYMENT_QR = os.getenv("PAYMENT_QR_FILE_ID", "YOUR_QR_FILE_ID")

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": 200, "1 Week": 800, "1 Month": 2000},
    "WIN iOS": {"1 Day": 200, "1 Week": 600, "1 Month": 1200},
    "VISION": {"1 Day": 199, "1 Week": 799, "1 Month": 2199},
    "RAGE": {"1 Day": 150, "1 Week": 599, "1 Month": 1499}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_banned(user.id): return
    save_user(user.id, user.username)
    buttons = [["🎮 Games", "🔑 My Keys"], ["👤 Profile", "📞 Support"], ["💳 Payment"]]
    if user.id == ADMIN_ID: buttons.append(["🛠 Admin Panel"])
    await update.message.reply_text(f"👋 Welcome {user.first_name}!", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # Issue 4 Fix: Security Check
    if data.startswith(("approve|", "reject|")):
        if query.from_user.id != ADMIN_ID: return
        
        order_id = int(data.split("|")[1])
        order = get_order(order_id)
        if not order or order.get("status") != "pending":
            await query.edit_message_text("❌ Already processed or not found."); return
        
        if data.startswith("approve|"):
            key = approve_order(order_id, order["game"], order["plan"], order["user_id"])
            if key:
                await context.bot.send_message(order["user_id"], f"✅ Payment Approved!\n🔑 Key: `{key}`", parse_mode="Markdown")
                await query.edit_message_text("✅ Approved & Key Sent.")
            else: await query.edit_message_text("❌ Key Stock Empty.")
        else:
            reject_order(order_id)
            await context.bot.send_message(order["user_id"], "❌ Payment Rejected.")
            await query.edit_message_text("❌ Payment Rejected.")
        return

    # Game/Plan Logic
    if data.startswith("game|"):
        game = data.split("|", 1)[1]
        context.user_data["game"] = game
        buttons = [[InlineKeyboardButton(f"{plan} - ₹{price}", callback_data=f"plan|{plan}")] for plan, price in GAME_PLANS[game].items()]
        await query.edit_message_text(f"🎮 {game}\n\nSelect Plan:", reply_markup=InlineKeyboardMarkup(buttons))
    elif data.startswith("plan|"):
        plan = data.split("|", 1)[1]
        context.user_data["plan"] = plan
        await context.bot.send_photo(chat_id=query.from_user.id, photo=PAYMENT_QR, caption=f"💰 Plan: {plan}\n\nकृपया पेमेंट स्क्रीनशॉट भेजें।")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Photo Handler
    if update.message.photo:
        if "game" not in context.user_data: await update.message.reply_text("❌ पहले Game और Plan सेलेक्ट करें।"); return
        order_id = save_order(user.id, user.username, context.user_data["game"], context.user_data["plan"])
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"📦 New Order: {order_id}\n👤 User: @{user.username}", 
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve", callback_data=f"approve|{order_id}"), InlineKeyboardButton("❌ Reject", callback_data=f"reject|{order_id}")]]))
        await update.message.reply_text("✅ स्क्रीनशॉट एडमिन को भेज दिया गया है।"); context.user_data.clear()
        return

    text = update.message.text or ""

    # Admin Logic
    if user.id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("⚙️ Admin Panel", reply_markup=admin_keyboard()); return
        elif text == "🔙 Back to Admin": await update.message.reply_text("⚙️ Admin Panel", reply_markup=admin_keyboard()); return
        elif text == "📦 Stock":
            stock = get_stock()
            if not stock: await update.message.reply_text("❌ Stock Empty"); return
            msg = "📦 Available Stock:\n\n"
            for g, p, c in stock: msg += f"🎮 {g} | 📦 {p} | 🔑 {c}\n"
            await update.message.reply_text(msg); return
        elif text == "👥 Total Users": await update.message.reply_text(f"👥 Total Users: {get_total_users()}"); return
        
        # Key Addition Logic
        if text == "🔑 Add Keys": context.user_data["admin_mode"] = "select_game"; await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard()); return
        if context.user_data.get("admin_mode") == "select_game": context.user_data.update({"add_game": text, "admin_mode": "select_plan"}); await update.message.reply_text("Select Plan:", reply_markup=admin_plan_selection_keyboard()); return
        if context.user_data.get("admin_mode") == "select_plan": context.user_data.update({"add_plan": text, "admin_mode": "send_keys"}); await update.message.reply_text("🔑 अब Keys पेस्ट करें (एक लाइन में एक):"); return
        if context.user_data.get("admin_mode") == "send_keys":
            for k in text.split("\n"):
                if k.strip(): save_key(context.user_data["add_game"], context.user_data["add_plan"], k.strip())
            await update.message.reply_text("✅ Keys Added!", reply_markup=admin_keyboard()); context.user_data.clear(); return

    # User Logic
    if text == "👤 Profile": await update.message.reply_text(f"👤 ID: {user.id}\n👤 User: @{user.username}")
    elif text == "📞 Support": await update.message.reply_text("📞 संपर्क: @YourAdminUsername")
    elif text == "💳 Payment": await update.message.reply_text("🎮 'Games' बटन पर क्लिक करके अपना गेम चुनें।")
    elif text == "🔑 My Keys":
        keys = get_user_keys(user.id)
        if not keys: await update.message.reply_text("❌ No keys found."); return
        msg = "🔑 Your Keys:\n\n"
        for g, p, k in keys: msg += f"🎮 {g}\n📦 {p}\n🔑 `{k}`\n\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    elif text == "🎮 Games":
        await update.message.reply_text("Games List:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(g, callback_data=f"game|{g}")] for g in GAME_PLANS]))

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.ALL, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
