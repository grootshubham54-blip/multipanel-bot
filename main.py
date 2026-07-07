import os, logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593 
SUPPORT_USERNAME = "@IOS_HACK_S" 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

GAME_PLANS = {
    "👑 ✦ 𝕂𝕀ℕ𝔾 𝕚𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "⭐️ ✦ 𝕎𝕀ℕ𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "🚀 ✦ ℕ𝔼𝕏𝕋 𝕚𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800"},
    "🪐 ✦ 𝕄𝕒𝕣𝕤 𝕃𝕠𝕒𝕕𝕖𝕣 ✦": {"1 Day": "130", "1 Week": "599"},
    "💀 ✦ 𝔻𝔼𝔸𝔻𝔼𝕐𝔼 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "🐬 ✦ 𝔻𝕆𝕃ℙℍ𝕀ℕ 𝕚𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

def admin_keyboard():
    return ReplyKeyboardMarkup([
        ["🔑 Add Keys", "📊 Stock"], ["📊 Sales Dashboard", "👥 Total Users"], 
        ["📜 Key Report", "🔄 Resend Key"], ["📂 Export Data", "📢 Broadcast"],
        ["💾 Backup DB", "🗑 Delete Key"], ["🔙 Back"]
    ], resize_keyboard=True)

async def start(update, context):
    user = update.effective_user
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username or "N/A"))
    conn.commit(); conn.close()
    
    welcome_text = (
        "🎮 Welcome to IOS SHUBHAM License Store\n\n"
        "Your trusted destination for premium gaming licenses.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "📦 Available Products\n• KINGIOS\n• WINIOS\n• NEXT IOS\n• Mars Loader\n• DEADEYE\n• DOLPHIN IOS\n\n"
        "⏳ License Durations\n• 1 Day License\n• 7 Days License\n• 30 Days License\n\n"
        "✨ Why Choose Us?\n✅ Instant QR Code Generation\n✅ Automatic Payment Verification\n✅ Instant License Delivery\n✅ Real-Time Order Tracking\n✅ Fast & Reliable Support\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "🚀 Select an option from the menu below to get started."
    )
    
    kb = [["🎮 ✦ Games ✦", "🔑 ✦ My Keys ✦"], ["🎧 ✦ Support ✦", "💳 ✦ Top Up ✦"], ["🔍 ✦ Status Check ✦"]]
    if user.id == ADMIN_ID: kb.append(["⚙️ ✦ Admin Panel ✦"])
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    # 1. Admin Logic (High Priority)
    if user_id == ADMIN_ID:
        if text == "⚙️ ✦ Admin Panel ✦": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "🔙 Back": context.user_data.clear(); await start(update, context); return
        elif text == "📢 Broadcast": context.user_data["state"] = "broadcasting"; await update.message.reply_text("Send your Broadcast message:")
        elif text == "🔑 Add Keys": context.user_data["state"] = "select_game"; await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup([[g] for g in GAME_PLANS.keys()] + [["🔙 Back"]], resize_keyboard=True))
        elif context.user_data.get("state") == "select_game":
            context.user_data["add_game"] = text; context.user_data["state"] = "select_plan"
            await update.message.reply_text("Select Plan:", reply_markup=ReplyKeyboardMarkup([[p] for p in GAME_PLANS[text].keys()] + [["🔙 Back"]], resize_keyboard=True))
        elif context.user_data.get("state") == "select_plan":
            context.user_data["add_plan"] = text; context.user_data["state"] = "add_keys"
            await update.message.reply_text("Enter keys (one per line):", reply_markup=ReplyKeyboardMarkup([["🔙 Back"]], resize_keyboard=True))
        elif context.user_data.get("state") == "add_keys":
            for k in text.split("\n"):
                if k.strip(): save_key(context.user_data["add_game"], k.strip(), context.user_data["add_plan"])
            await update.message.reply_text("✅ Keys Saved!", reply_markup=admin_keyboard()); context.user_data.clear(); return

    # 2. User Logic (Broadcast/Support states)
    if context.user_data.get("state") == "broadcasting":
        users = get_all_users()
        for u in users:
            try: await context.bot.send_message(u, text)
            except: pass
        await update.message.reply_text("✅ Broadcast Sent!", reply_markup=admin_keyboard()); context.user_data.clear(); return

    if context.user_data.get("state") == "support_msg":
        await context.bot.send_message(ADMIN_ID, f"📩 *New Support Ticket*\n👤 User: @{update.effective_user.username or 'N/A'}\n🆔 ID: `{user_id}`\n\n💬 Message: {text}", parse_mode="Markdown")
        await update.message.reply_text("✅ Your message has been sent to the admin.")
        context.user_data.clear(); return

    # 3. Main Buttons
    if text == "🔍 ✦ Status Check ✦": await update.message.reply_text("⏳ Your payment is being reviewed by the admin. Please wait.")
    elif text == "🎮 ✦ Games ✦":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "🔑 ✦ My Keys ✦":
        keys = get_user_keys(user_id)
        if not keys: await update.message.reply_text("No keys found!")
        else: await update.message.reply_text("\n".join([f"{g} ({p}): {k}" for g, p, k in keys]))
    elif text == "🎧 ✦ Support ✦": 
        context.user_data["state"] = "support_msg"
        await update.message.reply_text("✍️ Write your message here:")
    elif text == "💳 ✦ Top Up ✦": await update.message.reply_text(f"💳 Payment Details:\n{PAYMENT_DETAILS}")
    elif update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("game", "N/A"); p = context.user_data.get("plan", "N/A")
        btns = [[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}_{g}_{p}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}\nGame: {g}\nPlan: {p}", reply_markup=InlineKeyboardMarkup(btns))
        await update.message.reply_text("✅ Screenshot sent!")

async def button_click(update, context):
    query = update.callback_query; await query.answer()
    # ... (Keep existing button_click logic from before) ...
    if query.data.startswith("game_"):
        game = query.data.split("_")[1]; context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr} ({get_stock_count(game, p)} Left)", callback_data=f"pay_{p}_{pr}")] for p, pr in GAME_PLANS[game].items()]
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="back_games")])
        await query.edit_message_text(f"🎮 *{game}*\nSelect your plan:", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    elif query.data == "back_games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await query.edit_message_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data.startswith("pay_"):
        data = query.data.split("_"); plan, price = data[1], data[2]; game = context.user_data.get("game", "Game")
        caption_text = f"✅ *Order Details*\n\n🎮 *Game:* {game}\n⏳ *Plan:* {plan}\n💰 *Amount:* ₹{price}\n\n👉 Pay to this QR and send screenshot."
        try:
            with open("qr.JPG", "rb") as qr: await query.message.reply_photo(photo=qr, caption=caption_text, parse_mode="Markdown")
        except: await update.message.reply_text(f"⚠️ QR not found!\n{caption_text}", parse_mode="Markdown")
    elif query.data.startswith(("acc_", "rej_")):
        data = query.data.split("_"); action, uid, game, plan = data[0], int(data[1]), data[2], data[3]
        if action == "acc":
            key = approve_and_assign_key(uid, game, plan)
            if key:
                await context.bot.send_message(uid, f"🎉 *Payment Received!*\n\n📦 *Game:* {game}\n⏳ *Plan:* {plan}\n🔑 *Key:* `{key}`", parse_mode="Markdown")
                await query.edit_message_caption(caption=f"✅ Approved!\nUser ID: {uid}\nKey: {key}")
        elif action == "rej":
            await context.bot.send_message(uid, "❌ Payment Rejected. Please send a valid screenshot."); await query.edit_message_caption(caption=f"❌ Rejected!\nUser ID: {uid}")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__": main()
