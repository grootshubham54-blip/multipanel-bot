import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7908981593"

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "199", "1 Week": "600", "1 Month": "1299"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"}
}

GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN", "NEXT IOS": "NEXT", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "MARS", "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": "DEAD", "DOLPHIN IOS": "DOLP"}
REV_GAME_MAP = {v: k for k, v in GAME_MAP.items()}
PLAN_MAP = {"1 Day": "1D", "1 Week": "1W", "1 Month": "1M"}
REV_PLAN_MAP = {"1D": "1 Day", "1W": "1 Week", "1M": "1 Month"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "No Username"
    add_user(update.effective_user.id, username)
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID: keyboard.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome! How can I help you today?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    state = context.user_data.get("state")

    if update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("u_game", "👑 KING iOS")
        p = context.user_data.get("u_plan", "1 Day")
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, 
            caption=f"👤 Payment from {user_id}\n🎮 Game: {g}\n📦 Plan: {p}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept & Send Key", callback_data=f"acc_{user_id}_{GAME_MAP[g]}_{PLAN_MAP[p]}")], [InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]))
        await update.message.reply_text("✅ Screenshot received! Admin is verifying your payment.")
        return

    if user_id == ADMIN_ID and state:
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
            return
        if state == "awaiting_game":
            if text in GAME_PLANS:
                context.user_data["add_game"] = text
                context.user_data["state"] = "awaiting_plan"
                await update.message.reply_text(f"🎮 Selected: {text}\nNow choose the plan:", reply_markup=admin_plan_selection_keyboard())
            return
        elif state == "awaiting_plan":
            clean_plan = text.replace("🟢 ", "").replace("🟡 ", "").replace("🔴 ", "").strip()
            if clean_plan in ["1 Day", "1 Week", "1 Month"]:
                context.user_data["add_plan"] = clean_plan
                context.user_data["state"] = "awaiting_keys"
                await update.message.reply_text(f"📝 Enter the Keys for {context.user_data['add_game']} ({clean_plan}):")
            return
        elif state == "awaiting_keys":
            keys = [k.strip() for k in text.split("\n") if k.strip()]
            g_name, p_name = context.user_data["add_game"], context.user_data["add_plan"]
            for key in keys: save_key(g_name, key, p_name)
            context.user_data.clear()
            await update.message.reply_text(f"✅ {len(keys)} Keys saved successfully for {g_name}!", reply_markup=admin_keyboard())
            return

    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel" or text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("🛠 Admin Panel:", reply_markup=admin_keyboard())
            return
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "awaiting_game"
            await update.message.reply_text("🎮 Choose a game to add keys:", reply_markup=admin_game_selection_keyboard())
            return
        elif text == "📦 Stock":
            msg = "📦 **Current Stock:**\n"
            for g in GAME_PLANS:
                msg += f"\n🔹 {g}:\n"
                for p in GAME_PLANS[g]: msg += f"  - {p}: {get_stock_count(g, p)} left\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
            return
        elif text == "👥 Total Users":
            await update.message.reply_text(f"👥 Total Users: {get_total_users()}")
            return

    if text == "🎮 Games":
        await update.message.reply_text("Choose a game to purchase:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_PLANS:
        keyboard = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{GAME_MAP[text]}_{PLAN_MAP[p]}_{pr}")] for p, pr in GAME_PLANS[text].items()]
        await update.message.reply_text(f"🎮 Select your plan for {text}:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif text == "🔑 My Keys":
        my_keys = get_user_keys(update.effective_user.id)
        if my_keys:
            msg = "🔑 **Your Keys:**\n"
            for gk, pk, kcode in my_keys: msg += f"\n🎮 {gk} ({pk}): `{kcode}`"
            await update.message.reply_text(msg, parse_mode="Markdown")
        else: await update.message.reply_text("❌ No keys found.")
    elif text == "📞 Support":
        await update.message.reply_text("📞 Contact admin: @IOS_HACK_S")
    elif text == "💳 Payment":
        await update.message.reply_text("💳 Go to '🎮 Games' to select a plan and make payment.")
    else: await start(update, context)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("pay_"):
        _, g_short, p_short, price = data.split("_")
        context.user_data.update({"u_game": REV_GAME_MAP[g_short], "u_plan": REV_PLAN_MAP[p_short]})
        with open("qr.JPG", "rb") as qr:
            await query.message.reply_photo(photo=qr, caption=f"✅ Plan: {REV_GAME_MAP[g_short]} ({REV_PLAN_MAP[p_short]})\n💰 Amount: ₹{price}\n\n👉 Pay to this QR and **send the screenshot here**.")
    elif data.startswith("acc_"):
        _, uid, g_short, p_short = data.split("_")
        key = approve_and_assign_key(int(uid), REV_GAME_MAP[g_short], REV_PLAN_MAP[p_short])
        if key:
            await context.bot.send_message(int(uid), f"✅ Payment Approved!\n\n🎮 Game: {REV_GAME_MAP[g_short]}\n🔑 Key: `{key}`")
            await query.edit_message_caption(caption="✅ Approved and Key sent.")
        else: await query.edit_message_caption(caption="⚠️ Error: Stock finished!")
    elif data.startswith("rej_"):
        await context.bot.send_message(int(data.split("_")[1]), "❌ Payment Rejected. Contact @IOS_HACK_S")
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
