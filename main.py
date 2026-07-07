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
        "⏳ License Durations\n• 1 Day | 7 Days | 30 Days\n\n"
        "🚀 Select an option from the menu below to get started."
    )
    
    kb = [["🎮 ✦ Games ✦", "🔑 ✦ My Keys ✦"], ["🎧 ✦ Support ✦", "💳 ✦ Top Up ✦"], ["🔍 ✦ Status Check ✦"]]
    if user.id == ADMIN_ID: kb.append(["⚙️ ✦ Admin Panel ✦"])
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    # 1. Admin Logic - All buttons fixed here
    if user_id == ADMIN_ID:
        if text == "⚙️ ✦ Admin Panel ✦": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "🔙 Back": context.user_data.clear(); await start(update, context); return
        elif text == "📢 Broadcast": context.user_data["state"] = "broadcasting"; await update.message.reply_text("Send your Broadcast message:")
        elif text == "🔑 Add Keys": context.user_data["state"] = "select_game"; await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup([[g] for g in GAME_PLANS.keys()] + [["🔙 Back"]], resize_keyboard=True))
        elif text == "📊 Stock":
            msg = "📊 *Current Stock:*\n\n"
            for g, plans in GAME_PLANS.items():
                msg += f"*{g}:*\n"
                for p in plans: msg += f"  - {p}: {get_stock_count(g, p)} keys\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
        elif text == "👥 Total Users": await update.message.reply_text(f"👥 Total Users: {get_total_users()}")
        elif text == "📊 Sales Dashboard": sold = get_sold_keys_count(); await update.message.reply_text(f"💰 Revenue: ₹{sold * 200}")
        elif text == "💾 Backup DB": path = create_backup(); await update.message.reply_text(f"✅ Backup: {path}")
        elif text == "📂 Export Data": 
            data = get_all_keys_export()
            with open("keys.csv", "w") as f: f.write("ID,Game,Plan,Key,Used,UserID\n" + "\n".join([",".join(map(str, r)) for r in data]))
            await update.message.reply_document(document=open("keys.csv", "rb"))
        elif text == "🔄 Resend Key": context.user_data["state"] = "resend_uid"; await update.message.reply_text("Enter User ID:")
        elif context.user_data.get("state") == "select_game":
            context.user_data["add_game"] = text; context.user_data["state"] = "select_plan"
            await update.message.reply_text("Select Plan:", reply_markup=ReplyKeyboardMarkup([[p] for p in GAME_PLANS[text].keys()] + [["🔙 Back"]], resize_keyboard=True))
        elif context.user_data.get("state") == "select_plan":
            context.user_data["add_plan"] = text; context.user_data["state"] = "add_keys"
            await update.message.reply_text("Enter keys:", reply_markup=ReplyKeyboardMarkup([["🔙 Back"]], resize_keyboard=True))
        elif context.user_data.get("state") == "add_keys":
            for k in text.split("\n"):
                if k.strip(): save_key(context.user_data["add_game"], k.strip(), context.user_data["add_plan"])
            await update.message.reply_text("✅ Keys Saved!", reply_markup=admin_keyboard()); context.user_data.clear(); return

    # 2. States
    if context.user_data.get("state") == "broadcasting":
        for u in get_all_users(): 
            try: await context.bot.send_message(u, text)
            except: pass
        await update.message.reply_text("✅ Broadcast Sent!", reply_markup=admin_keyboard()); context.user_data.clear(); return

    if context.user_data.get("state") == "support_msg":
        await context.bot.send_message(ADMIN_ID, f"📩 *New Ticket*\nID: `{user_id}`\nMessage: {text}", parse_mode="Markdown")
        await update.message.reply_text("✅ Message sent to admin."); context.user_data.clear(); return

    # 3. User Buttons
    if text == "🔍 ✦ Status Check ✦": await update.message.reply_text("⏳ Payment under review.")
    elif text == "🎮 ✦ Games ✦": await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]))
    elif text == "🎧 ✦ Support ✦": context.user_data["state"] = "support_msg"; await update.message.reply_text("Write your message:")
    elif update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("game", "N/A"); p = context.user_data.get("plan", "N/A")
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}\nGame: {g}\nPlan: {p}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}_{g}_{p}")]]))
        await update.message.reply_text("✅ Screenshot sent!")

async def button_click(update, context):
    query = update.callback_query; await query.answer()
    if query.data.startswith("game_"):
        game = query.data.split("_")[1]; context.user_data["game"] = game
        await query.edit_message_text(f"🎮 *{game}*\nSelect plan:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{p}_{pr}")] for p, pr in GAME_PLANS[game].items()]), parse_mode="Markdown")
    elif query.data.startswith("pay_"):
        data = query.data.split("_"); plan, price = data[1], data[2]; game = context.user_data.get("game")
        await query.message.reply_photo(photo=open("qr.JPG", "rb"), caption=f"Pay ₹{price} for {game} ({plan})")
    elif query.data.startswith(("acc_", "rej_")):
        data = query.data.split("_"); action, uid, game, plan = data[0], int(data[1]), data[2], data[3]
        if action == "acc":
            key = approve_and_assign_key(uid, game, plan)
            await context.bot.send_message(uid, f"🎉 Received! Key: `{key}`" if key else "⚠️ No keys left", parse_mode="Markdown")
            await query.edit_message_caption(caption=f"✅ Approved: {key}")
        else: await context.bot.send_message(uid, "❌ Rejected."); await query.edit_message_caption(caption="❌ Rejected")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__": main()
