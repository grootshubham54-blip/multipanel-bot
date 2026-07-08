import os, logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

# Logging setup
logging.basicConfig(level=logging.INFO)
TOKEN = "YOUR_BOT_TOKEN_HERE" # अपना टोकन डालें
ADMIN_ID = 7908981593 

# --- START COMMAND ---
async def start(update, context):
    uid = update.effective_user.id
    if is_banned(uid): await update.message.reply_text("You are banned."); return
    save_user(uid, update.effective_user.username)
    kb = [["🎮 Games", "🔑 My Keys"], ["📜 Order History", "📞 Support"]]
    if uid == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("Welcome to our Store!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

# --- ADMIN PANEL ---
async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID: return
    kb = [["📈 Stats", "📊 Stock"], ["📋 Orders List", "📢 Broadcast"], ["🗑 Delete Keys", "🔙 Back"]]
    await update.message.reply_text("Admin Control Panel:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

# --- PAYMENT & ORDER LOGIC ---
async def message_handler(update, context):
    uid = update.effective_user.id
    text = update.message.text
    
    if text == "🛠 Admin Panel": await admin_panel(update, context)
    elif text == "📞 Support": await update.message.reply_text("Contact: @YourSupportUsername")
    
    # QR & UPI Display
    elif text == "🎮 Games":
        qr = get_setting('qr_file_id')
        upi = get_setting('upi_details')
        if qr == 'none': await update.message.reply_text("Admin has not set QR.")
        else: await context.bot.send_photo(uid, photo=qr, caption=f"💰 Pay here:\nUPI: `{upi}`\n\nSend Screenshot after payment.", parse_mode="Markdown")

    # Stats
    elif text == "📈 Stats":
        u, o, p, a, r, k = get_stats()
        await update.message.reply_text(f"📊 Stats:\nUsers: {u}\nOrders: {o}\nPending: {p}\nApproved: {a}\nRejected: {r}\nTotal Keys: {k}")

    # Broadcast
    elif text == "📢 Broadcast" and uid == ADMIN_ID:
        await update.message.reply_text("Reply to a message to broadcast.")

# --- BUTTON HANDLER ---
async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # Approve
    if data.startswith("acc_"):
        _, oid, uid, game, plan = data.split("_")
        key = approve_and_assign_key(int(uid), game, plan)
        if key:
            update_order_status(oid, "Approved")
            await context.bot.send_message(int(uid), f"✅ Approved! Key: `{key}`", parse_mode="Markdown")
            await query.edit_message_text(f"Approved Order #{oid}")
        else: await query.edit_message_text("❌ Key out of stock!")

    # Reject
    elif data.startswith("rej_"):
        _, oid, uid = data.split("_")
        update_order_status(oid, "Rejected")
        await query.edit_message_text(f"Rejected Order #{oid}. User notified.")

# --- ADMIN COMMANDS ---
async def set_qr(update, context):
    if update.effective_user.id != ADMIN_ID or not update.message.reply_to_message: return
    file_id = update.message.reply_to_message.photo[-1].file_id
    update_setting('qr_file_id', file_id)
    await update.message.reply_text("✅ QR Updated.")

async def set_upi(update, context):
    if update.effective_user.id != ADMIN_ID: return
    new_upi = " ".join(context.args)
    update_setting('upi_details', new_upi)
    await update.message.reply_text(f"✅ UPI Updated to: {new_upi}")

if __name__ == '__main__':
    create_tables()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setqr", set_qr))
    app.add_handler(CommandHandler("setupi", set_upi))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    
    print("Bot is running...")
    app.run_polling()
