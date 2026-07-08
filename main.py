import os, logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from database import *

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593 
SUPPORT_USERNAME = "@IOS_HACK_S" 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

async def start(update, context):
    user = update.effective_user
    save_user_to_db(user.id, user.username)
    # आपका ओरिजिनल बड़ा वेलकम मैसेज
    welcome_text = (
        "🎮 Welcome to IOS SHUBHAM License Store\n\n"
        "Your trusted destination for premium gaming licenses.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "🚀 Select an option from the menu below to get started."
    )
    kb = [["🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦", "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦"], ["🎧 ✦ 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 ✦", "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦"]]
    if user.id == ADMIN_ID: kb.append(["⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦"])
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    if user_id == ADMIN_ID and context.user_data.get("state") == "add_keys":
        try:
            g, p, k = text.split("|"); save_key(g.strip(), k.strip(), p.strip())
            await update.message.reply_text("✅ Key Added Successfully!")
        except: await update.message.reply_text("⚠️ Format Error! Use: Game | Plan | Key")
        context.user_data["state"] = None; return

    if user_id == ADMIN_ID:
        if text == "⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦": await update.message.reply_text("Admin Panel:", reply_markup=ReplyKeyboardMarkup([["🔑 Add Keys", "📊 Stock"], ["📊 Sales Dashboard", "👥 Total Users"], ["🔙 Back"]], resize_keyboard=True))
        elif text == "🔑 Add Keys": context.user_data["state"] = "add_keys"; await update.message.reply_text("Send key in format: Game | Plan | Key")
        elif text == "📊 Stock": await update.message.reply_text(f"📊 Total Keys in Stock: {get_stock_count_all()}")
        elif text == "👥 Total Users": await update.message.reply_text(f"👥 Total Users: {get_total_users()}")
        elif text == "📊 Sales Dashboard": await update.message.reply_text(f"💰 Total Sold: {get_sold_keys_count()}")
        elif text == "🔙 Back": await start(update, context)

    if text == "🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦":
        keys = get_user_keys(user_id)
        await update.message.reply_text("\n".join([f"{g} ({p}): {k}" for g, p, k in keys]) if keys else "No keys found!")
    elif text == "🎧 ✦ 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 ✦": await update.message.reply_text(f"Contact: {SUPPORT_USERNAME}")
    elif text == "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦": await update.message.reply_text(f"Payment Details:\n{PAYMENT_DETAILS}")
    elif update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("game", "N/A"); p = context.user_data.get("plan", "N/A")
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}\nGame: {g}\nPlan: {p}", 
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}_{g}_{p}")]]))
        await update.message.reply_text("✅ Screenshot sent!")

async def button_click(update, context):
    query = update.callback_query; await query.answer()
    if query.data.startswith("game_"):
        game = query.data.split("_")[1]; context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{p}_{pr}_{game}")] for p, pr in GAME_PLANS[game].items()]
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="back_games")])
        await query.edit_message_text(f"🎮 {game}\nSelect plan:", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data == "back_games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await query.edit_message_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data.startswith("pay_"):
        data = query.data.split("_"); context.user_data["plan"] = data[1]; context.user_data["game"] = data[3]
        if os.path.exists("qr.JPG"): await query.message.reply_photo(photo=open("qr.JPG", "rb"), caption="👉 Pay to this QR.")
        await query.message.delete()
    elif query.data.startswith(("acc_", "rej_")):
        data = query.data.split("_"); action, uid, game, plan = data[0], int(data[1]), data[2], data[3]
        if action == "acc":
            key = approve_and_assign_key(uid, game, plan)
            if key: await context.bot.send_message(uid, f"🎉 Key: `{key}`"); await query.edit_message_caption(caption="✅ Approved!")
        else:
            # आपका ओरिजिनल बड़ा रिजेक्शन मैसेज
            rej_msg = (
                "❌ *PAYMENT REJECTED*\n\n"
                "Your payment screenshot was invalid or unclear. Please ensure the screenshot shows:\n"
                "1. Transaction ID\n"
                "2. Correct Date & Time\n"
                "3. Success Status\n\n"
                "If you believe this is an error, please contact support."
            )
            await context.bot.send_message(uid, rej_msg, parse_mode="Markdown")
            await query.edit_message_caption(caption="❌ Rejected!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
