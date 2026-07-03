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
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

def admin_keyboard():
    return ReplyKeyboardMarkup([
        ["🔑 Add Keys", "📊 Stock"], 
        ["📊 Sales Dashboard", "📜 Key Report"], 
        ["📂 Export Data", "🔄 Resend Key"],
        ["📢 Broadcast", "💾 Backup DB"],
        ["🗑 Delete Key", "🔙 Back"]
    ], resize_keyboard=True)

async def start(update, context):
    user_id = update.effective_user.id
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "🔙 Back":
        context.user_data.clear()
        await start(update, context)
        return

    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
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
                context.user_data["target_uid"] = uid
                keys = get_key_by_user_id(uid)
                if keys:
                    msg = "\n".join([f"🎮 {g} ({p}): `{k}`" for g, p, k in keys])
                    context.user_data["resend_msg"] = msg
                    context.user_data["state"] = "confirm_resend"
                    await update.message.reply_text(f"Found:\n{msg}\n\nConfirm to resend?", reply_markup=ReplyKeyboardMarkup([["✅ Confirm Resend", "🔙 Back"]], resize_keyboard=True))
                else: await update.message.reply_text("⚠️ No keys found."); context.user_data.clear()
            except: await update.message.reply_text("⚠️ Invalid ID."); context.user_data.clear()
        elif context.user_data.get("state") == "confirm_resend" and text == "✅ Confirm Resend":
            uid = context.user_data.get("target_uid")
            msg = context.user_data.get("resend_msg")
            await context.bot.send_message(uid, f"🔄 *Your key has been resent:*\n\n{msg}", parse_mode="Markdown")
            await update.message.reply_text("✅ Sent successfully!", reply_markup=admin_keyboard())
            context.user_data.clear()
        elif text == "📊 Sales Dashboard":
            sold = get_sold_keys_count()
            await update.message.reply_text(f"📊 *Sales Dashboard*\n\n✅ Sold: {sold}\n💰 Revenue: ₹{sold * 200}", parse_mode="Markdown")

    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "🔑 My Keys":
        keys = get_user_keys(user_id)
        if not keys: await update.message.reply_text("No keys found!")
        else: await update.message.reply_text("\n".join([f"{g} ({p}): {k}" for g, p, k in keys]))
    elif text == "📞 Support": await update.message.reply_text(f"📞 Contact: {SUPPORT_USERNAME}")
    elif text == "💳 Payment": await update.message.reply_text(f"💳 Payment Details:\n{PAYMENT_DETAILS}")
    elif update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("game", "N/A"); p = context.user_data.get("plan", "N/A")
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}\nGame: {g}\nPlan: {p}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}")]]))
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
    elif query.data.startswith("acc_"):
        data = query.data.split("_"); uid, game, plan = int(data[1]), data[2], data[3]
        key = approve_and_assign_key(uid, game, plan)
        if key:
            success_msg = (f"🎉 *Payment Received Successfully!*\n\n━━━━━━━━━━━━━━━━━━\n📦 *Purchase Details:*\n🎮 *Game:* {game}\n⏳ *Plan:* {plan}\n━━━━━━━━━━━━━━━━━━\n\n🔑 *Your Access Key:*\n`{key}`\n\n━━━━━━━━━━━━━━━━━━\n🙏 *Thank you for your purchase!*\n🚀 Enjoy your access!")
            await context.bot.send_message(uid, success_msg, parse_mode="Markdown")
            await query.edit_message_caption(caption=f"✅ Approved!\nUser ID: {uid}\nKey: {key}")
        else: await query.edit_message_caption(caption="⚠️ Error: No keys available!")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
