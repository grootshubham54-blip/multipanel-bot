import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "199", "1 Week": "600", "1 Month": "1299"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"}
}

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    # --- ADMIN FLOW ---
    if user_id == ADMIN_ID:
        # (आपका एडमिन लॉजिक यहाँ वैसा ही रहेगा)
        if text == "📦 Stock":
            msg = "📦 Stock:\n" + "\n".join([f"{g}: {sum([get_stock_count(g, p) for p in GAME_PLANS[g]])} left" for g in GAME_PLANS])
            await update.message.reply_text(msg)
        return

    # --- USER PAYMENT SCREENSHOT ---
    if update.message.photo and user_id != ADMIN_ID:
        game = context.user_data.get("last_game", "N/A")
        plan = context.user_data.get("last_plan", "N/A")
        # सुरक्षित callback data: acc_userid_gamename_planname
        callback_acc = f"acc_{user_id}_{game}_{plan}"
        
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, 
            caption=f"Payment from {user_id}\nGame: {game}\nPlan: {plan}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=callback_acc), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]))
        await update.message.reply_text("✅ Screenshot sent to Admin!")
        return

    # --- GAME SELECTION ---
    if text == "🎮 Games": await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_PLANS:
        context.user_data["last_game"] = text
        kb = [[InlineKeyboardButton(f"{p}", callback_data=f"plan_{p}")] for p in GAME_PLANS[text]]
        await update.message.reply_text("Select plan:", reply_markup=InlineKeyboardMarkup(kb))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("plan_"):
        context.user_data["last_plan"] = data.split("_")[1]
        if os.path.exists("qr.JPG"): await query.message.reply_photo(open("qr.JPG", "rb"), caption="Send screenshot.")
    
    elif data.startswith("acc_"):
        # ऑटो-की डिलीवरी का असली लॉजिक:
        _, uid, game, plan = data.split("_", 3)
        key = approve_and_assign_key(int(uid), game, plan) # int(uid) सुरक्षा के लिए
        if key:
            await context.bot.send_message(int(uid), f"✅ Approved! Key: `{key}`", parse_mode="Markdown")
            await query.edit_message_caption(caption=f"✅ Approved & Sent: {key}")
        else:
            await context.bot.send_message(int(uid), "❌ Sorry, no keys left.")
            await query.edit_message_caption(caption="❌ Rejected (Out of Stock).")

    elif data.startswith("rej_"):
        uid = data.split("_")[1]
        await context.bot.send_message(uid, "❌ Rejected.")
        await query.edit_message_caption(caption="❌ Rejected.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", lambda u, c: start(u, c)))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()
