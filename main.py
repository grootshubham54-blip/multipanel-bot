import os, logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593 
SUPPORT_USERNAME = "@IOS_HACK_S" 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

# मेंटेनेंस मोड के लिए वेरिएबल
is_bot_active = True 

GAME_PLANS = {
    "👑 ✦ 𝕂𝕀ℕ𝔾 𝕚𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "⭐️ ✦ 𝕎𝕀ℕ𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "🚀 ✦ ℕ𝔼𝕏𝕋 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800"},
    "🪐 ✦ 𝕄𝕒𝕣𝕤 𝕃𝕠𝕒𝕕𝕖𝕣 ✦": {"1 Day": "130", "1 Week": "599"},
    "💀 ✦ 𝔻𝔼𝔸𝔻𝔼𝕐𝔼 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "🐬 ✦ 𝔻𝕆𝕃ℙℍ𝕀ℕ 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

def admin_keyboard():
    global is_bot_active
    status = "ON" if is_bot_active else "OFF"
    return ReplyKeyboardMarkup([
        ["🔑 Add Keys", "📊 Stock"], 
        ["📊 Sales Dashboard", "👥 Total Users"], 
        ["📜 Key Report", "🔄 Resend Key"],
        ["📂 Export Data", "📢 Broadcast"],
        ["💾 Backup DB", "🗑 Delete Key"],
        [f"Maintenance: {status}"], # यह नया बटन है
        ["🔙 Back"]
    ], resize_keyboard=True)

async def start(update, context):
    global is_bot_active
    if not is_bot_active and update.effective_user.id != ADMIN_ID: return
    
    user = update.effective_user
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username or "N/A"))
    conn.commit()
    conn.close()
    
    welcome_text = (
        "🎮 Welcome to IOS SHUBHAM License Store\n\n"
        "Your trusted destination for premium gaming licenses.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "📦 Available Products\n"
        "• KINGIOS\n• WINIOS\n• NEXT IOS\n• Mars Loader\n• DEADEYE\n• DOLPHIN IOS\n\n"
        "⏳ License Durations\n"
        "• 1 Day License\n• 7 Days License\n• 30 Days License\n\n"
        "✨ Why Choose Us?\n"
        "✅ Instant QR Code Generation\n"
        "✅ Automatic Payment Verification\n"
        "✅ Instant License Delivery\n"
        "✅ Real-Time Order Tracking\n"
        "✅ Fast & Reliable Support\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "🚀 Select an option from the menu below to get started.\n\n"
        "Thank you for choosing IOS SHUBHAM License Store."
    )
    
    kb = [["🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦", "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦"], ["🎧 ✦ 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 ✦", "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦"]]
    if user.id == ADMIN_ID: kb.append(["⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦"])
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    global is_bot_active
    text = update.message.text
    user_id = update.effective_user.id
    
    if not is_bot_active and user_id != ADMIN_ID: return

    if user_id == ADMIN_ID and text.startswith("Maintenance:"):
        is_bot_active = not is_bot_active
        await update.message.reply_text(f"✅ बोट मेंटेनेंस मोड {'ON' if is_bot_active else 'OFF'} कर दिया गया है!", reply_markup=admin_keyboard())
        return

    # [आपका मूल कोडिंग यहाँ से आगे बिना किसी बदलाव के जारी है]
    if context.user_data.get("state") == "broadcasting":
        users = get_all_users()
        for u in users:
            try: await context.bot.send_message(u, text)
            except: pass
        await update.message.reply_text("✅ Broadcast Sent!", reply_markup=admin_keyboard())
        context.user_data.clear()
        return

    if text == "🔙 Back":
        context.user_data.clear()
        await start(update, context)
        return

    if user_id == ADMIN_ID:
        if text == "⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "📢 Broadcast":
            context.user_data["state"] = "broadcasting"
            await update.message.reply_text("Send your Broadcast message:")
        elif text == "👥 Total Users":
            await update.message.reply_text(f"👥 *Total Users:* {get_total_users()}", parse_mode="Markdown")
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "select_game"
            kb = [[g] for g in GAME_PLANS.keys()] + [["🔙 Back"]]
            await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        elif context.user_data.get("state") == "select_game":
            if text in GAME_PLANS:
                context.user_data["add_game"] = text
                context.user_data["state"] = "select_plan"
                kb = [[p] for p in GAME_PLANS[text].keys()] + [["🔙 Back"]]
                await update.message.reply_text("Select Plan:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        elif context.user_data.get("state") == "select_plan":
            context.user_data["add_plan"] = text
            context.user_data["state"] = "add_keys"
            await update.message.reply_text("Enter keys (one per line):", reply_markup=ReplyKeyboardMarkup([["🔙 Back"]], resize_keyboard=True))
        elif context.user_data.get("state") == "add_keys":
            for k in text.split("\n"):
                if k.strip(): save_key(context.user_data["add_game"], k.strip(), context.user_data["add_plan"])
            await update.message.reply_text("✅ Keys Saved!", reply_markup=admin_keyboard())
            context.user_data.clear()
        elif text == "📊 Stock":
            msg = "📊 *Current Stock:*\n\n"
            for g, plans in GAME_PLANS.items():
                msg += f"*{g}:*\n"
                for p in plans: msg += f"  - {p}: {get_stock_count(g, p)} keys\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
        elif text == "💾 Backup DB":
            path = create_backup()
            await update.message.reply_text(f"✅ Backup saved at: {path}")
        elif text == "📂 Export Data":
            data = get_all_keys_export()
            with open("keys.csv", "w") as f:
                f.write("ID,Game,Plan,Key,Used,UserID\n")
                for r in data: f.write(f"{','.join(map(str, r))}\n")
            await update.message.reply_document(document=open("keys.csv", "rb"))
        elif text == "🔄 Resend Key":
            context.user_data["state"] = "resend_uid"
            await update.message.reply_text("Enter Customer User ID:")
        elif context.user_data.get("state") == "resend_uid":
            try:
                uid = int(text)
                keys = get_key_by_user_id(uid)
                if keys:
                    msg = "\n".join([f"🎮 {g} ({p}): `{k}`" for g, p, k in keys])
                    context.user_data["resend_msg"] = msg
                    context.user_data["state"] = "confirm_resend"
                    context.user_data["target_uid"] = uid
                    await update.message.reply_text(f"Found:\n{msg}\n\nConfirm to resend?", reply_markup=ReplyKeyboardMarkup([["✅ Confirm Resend", "🔙 Back"]], resize_keyboard=True))
                else: await update.message.reply_text("⚠️ No keys found."); context.user_data.clear()
            except: await update.message.reply_text("⚠️ Invalid ID."); context.user_data.clear()
        elif context.user_data.get("state") == "confirm_resend" and text == "✅ Confirm Resend":
            await context.bot.send_message(context.user_data["target_uid"], f"🔄 *Your key has been resent:*\n\n{context.user_data['resend_msg']}", parse_mode="Markdown")
            await update.message.reply_text("✅ Sent successfully!", reply_markup=admin_keyboard())
            context.user_data.clear()
        elif text == "📊 Sales Dashboard":
            sold = get_sold_keys_count()
            await update.message.reply_text(f"📊 *Sales Dashboard*\n\n✅ Sold: {sold}\n💰 Revenue: ₹{sold * 200}", parse_mode="Markdown")

    if text == "🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦":
        keys = get_user_keys(user_id)
        if not keys: await update.message.reply_text("No keys found!")
        else: await update.message.reply_text("\n".join([f"{g} ({p}): {k}" for g, p, k in keys]))
    elif text == "🎧 ✦ 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 ✦": await update.message.reply_text(f"📞 Contact: {SUPPORT_USERNAME}")
    elif text == "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦": await update.message.reply_text(f"💳 Payment Details:\n{PAYMENT_DETAILS}")
    elif update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("game", "N/A"); p = context.user_data.get("plan", "N/A")
        btns = [[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), 
                 InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}_{g}_{p}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, 
                                     caption=f"Payment from {user_id}\nGame: {g}\nPlan: {p}", 
                                     reply_markup=InlineKeyboardMarkup(btns))
        await update.message.reply_text("✅ Screenshot sent!")

async def button_click(update, context):
    query = update.callback_query; await query.answer()
    if query.data.startswith("game_"):
        game = query.data.split("_")[1]; context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr} ({get_stock_count(game, p)} Left)", callback_data=f"pay_{p}_{pr}")] for p, pr in GAME_PLANS[game].items()]
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="back_games")])
        await query.edit_message_text(f"🎮 *{game}*\nSelect your plan:", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    elif query.data == "back_games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await query.edit_message_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data.startswith("pay_"):
        data = query.data.split("_"); plan, price, game = data[1], data[2], context.user_data.get("game"); context.user_data["plan"] = plan
        try:
            with open("qr.JPG", "rb") as qr: await query.message.reply_photo(photo=qr, caption=f"✅ *Plan:* {game} ({plan})\n💰 *Amount:* ₹{price}\n\n👉 Pay to this QR and send screenshot.", parse_mode="Markdown")
        except: await query.message.reply_text("⚠️ QR file not found!")
    
    elif query.data.startswith(("acc_", "rej_")):
        data = query.data.split("_")
        action, uid, game, plan = data[0], int(data[1]), data[2], data[3]
        if action == "acc":
            key = approve_and_assign_key(uid, game, plan)
            if key:
                success_msg = (f"🎉 *Payment Received Successfully!*\n\n📦 *Game:* {game}\n⏳ *Plan:* {plan}\n🔑 *Key:* `{key}`")
                await context.bot.send_message(uid, success_msg, parse_mode="Markdown")
                await query.edit_message_caption(caption=f"✅ Approved!\nUser ID: {uid}\nKey: {key}")
            else: await query.edit_message_caption(caption="⚠️ Error: No keys available!")
        elif action == "rej":
            reject_msg = (f"❌ 𝗣𝗮𝘆𝗺𝗲𝗻𝘁 𝗥𝗲𝗷𝗲𝗰𝘁𝗲𝗱\n\n"
                          f"Unfortunately, your payment could not be verified or the submitted screenshot is invalid.\n\n"
                          f"Please ensure that:\n"
                          f"• The payment was completed successfully.\n"
                          f"• The screenshot is clear and unedited.\n"
                          f"• The transaction details are fully visible.\n"
                          f"• The transaction ID is valid and matches the payment amount.\n\n"
                          f"⚠️ Any attempt to submit fake, edited, reused, or fraudulent payment screenshots may result in your account being permanently restricted from using this bot.\n\n"
                          f"🔄 Please review your payment details and submit a valid screenshot to continue.")
            await context.bot.send_message(uid, reject_msg)
            await query.edit_message_caption(caption=f"❌ Rejected!\nUser ID: {uid}")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
 इसमें जो भी प्राइसिंग है, प्राइस चेंज मत करना। बाकी मैंने जो बोला है, वह बस ऐड करके देना, ठीक? और यह सभी इसमें काम करना चाहिए। यह वाली है मेरी ओल्ड कोडिंग। बस मुझे इतना बताओ कि यह क्रैश क्यों हो रहा है। बाकी मुझे कुछ भी न्यू नहीं बस।