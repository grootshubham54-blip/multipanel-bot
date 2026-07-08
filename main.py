import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593 
SUPPORT_USERNAME = "@IOS_HACK_S" 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

# --- KEYBOARD ---
def admin_keyboard():
    return ReplyKeyboardMarkup([["🔑 Add Keys", "📊 Stock"], ["📊 Sales Dashboard", "👥 Total Users"], ["🔙 Back"]], resize_keyboard=True)

async def start(update, context):
    user = update.effective_user
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user.id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

# --- MESSAGE HANDLER (Keys & Admin) ---
async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    # एडमिन कीज एडिंग फ्लो
    if context.user_data.get("state") == "select_game":
        if text in GAME_PLANS:
            context.user_data["add_game"] = text
            context.user_data["state"] = "select_plan"
            kb = [[p] for p in GAME_PLANS[text].keys()]
            await update.message.reply_text("Select Plan:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    elif context.user_data.get("state") == "select_plan":
        context.user_data["add_plan"] = text
        context.user_data["state"] = "add_keys"
        await update.message.reply_text("Paste keys (एक लाइन में एक):")
    elif context.user_data.get("state") == "add_keys":
        for k in text.split("\n"):
            if k.strip(): save_key(context.user_data["add_game"], k.strip(), context.user_data["add_plan"])
        await update.message.reply_text("✅ Keys Saved!", reply_markup=admin_keyboard())
        context.user_data.clear()
        return

    # एडमिन कमांड्स
    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "select_game"
            kb = [[g] for g in GAME_PLANS.keys()]
            await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        elif text == "📊 Stock":
            msg = "📊 *Stock:*\n" + "".join([f"{g}: {get_stock_count(g, '1 Day')} keys\n" for g in GAME_PLANS])
            await update.message.reply_text(msg, parse_mode="Markdown")

    # यूजर कमांड्स
    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "💳 Payment":
        await update.message.reply_text(f"Pay here: {PAYMENT_DETAILS}")
    elif update.message.photo and user_id != ADMIN_ID:
        # पेमेंट स्क्रीनशॉट हैंडलिंग
        g = context.user_data.get("game", "N/A"); p = context.user_data.get("plan", "N/A")
        btns = [[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), 
                 InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}_{g}_{p}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, 
                                     caption=f"Payment from {user_id}\nGame: {g}\nPlan: {p}", 
                                     reply_markup=InlineKeyboardMarkup(btns))
        await update.message.reply_text("✅ Screenshot sent!")

# --- BUTTON CLICK (Accept/Reject/QR) ---
async def button_click(update, context):
    query = update.callback_query; await query.answer()
    data = query.data

    if data.startswith("game_"):
        game = data.split("_")[1]; context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{p}_{pr}_{game}")] for p, pr in GAME_PLANS[game].items()]
        await query.edit_message_text(f"🎮 {game}\nSelect Plan:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif data.startswith("pay_"):
        d = data.split("_"); plan, price, game = d[1], d[2], d[3]
        context.user_data["plan"] = plan
        if os.path.exists("qr.JPG"):
            with open("qr.JPG", "rb") as qr:
                await query.message.reply_photo(photo=qr, caption=f"Pay ₹{price} for {game} ({plan})")
        else: await query.message.reply_text("QR file missing!")

    elif data.startswith(("acc_", "rej_")):
        d = data.split("_"); action, uid, game, plan = d[0], int(d[1]), d[2], d[3]
        if action == "acc":
            key = approve_and_assign_key(uid, game, plan)
            if key:
                await context.bot.send_message(uid, f"🎉 Key: `{key}`", parse_mode="Markdown")
                await query.edit_message_caption(caption=f"✅ Approved! Key: {key}")
            else: await query.edit_message_caption(caption="⚠️ No keys left!")
        else:
            await context.bot.send_message(uid, "❌ Payment Rejected.")
            await query.edit_message_caption(caption="❌ Rejected.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
