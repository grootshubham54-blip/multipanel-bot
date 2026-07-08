import os, logging
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from database import *

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

async def start(update, context):
    u = update.effective_user
    save_user(u.id, u.username)
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if u.id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome to Store!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    txt, uid = update.message.text, update.effective_user.id
    if uid == ADMIN_ID:
        if txt == "🛠 Admin Panel": await update.message.reply_text("Admin:", reply_markup=ReplyKeyboardMarkup([["🔑 Add Keys", "📊 Stock"], ["📜 Key Report", "👥 Total Users"], ["🔙 Back"]], resize_keyboard=True))
        elif txt == "📊 Stock":
            msg = "📊 *Stock:*\n"
            for g, ps in GAME_PLANS.items():
                msg += f"*{g}:*\n" + "".join([f"  - {p}: {get_stock_count(g, p)}\n" for p in ps])
            await update.message.reply_text(msg, parse_mode="Markdown")
        elif txt == "📜 Key Report":
            report = "📜 *Report:*\n" + "".join([f"🎮 {g}|{p} | {'✅' if u==1 else '🟢'} {k}\n" for g,p,k,u,id in get_all_keys_report()])
            await update.message.reply_text(report, parse_mode="Markdown")
        elif txt == "👥 Total Users": await update.message.reply_text(f"Total: {get_total_users()}")
        elif txt == "🔑 Add Keys": 
            context.user_data["state"] = "wait_keys"
            await update.message.reply_text("Format: GameName | Plan | Key (one per line)")
        elif context.user_data.get("state") == "wait_keys":
            for line in txt.split("\n"):
                if "|" in line:
                    g, p, k = line.split("|")
                    save_key(g.strip(), p.strip(), k.strip())
            await update.message.reply_text("✅ Keys Saved!")
            context.user_data["state"] = None
        elif txt == "🔙 Back": await start(update, context)

    if txt == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select:", reply_markup=InlineKeyboardMarkup(kb))
    elif txt == "🔑 My Keys":
        k = get_user_keys(uid)
        await update.message.reply_text("\n".join([f"{g}({p}): {k}" for g,p,k in k]) if k else "No keys!")
    elif update.message.photo and uid != ADMIN_ID:
        g, p = context.user_data.get("g", "N/A"), context.user_data.get("p", "N/A")
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Pay by {uid}\nGame: {g}\nPlan: {p}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Acc", callback_data=f"acc_{uid}_{g}_{p}"), InlineKeyboardButton("❌ Rej", callback_data=f"rej_{uid}_{g}_{p}")]]))
        await update.message.reply_text("✅ Sent!")

async def button_click(update, context):
    q = update.callback_query; await q.answer()
    d = q.data.split("_")
    if d[0] == "game":
        context.user_data["g"] = d[1]
        kb = [[InlineKeyboardButton(f"{p} - {pr}", callback_data=f"pay_{p}_{d[1]}")] for p, pr in GAME_PLANS[d[1]].items()]
        await q.message.reply_text("Select Plan:", reply_markup=InlineKeyboardMarkup(kb))
    elif d[0] == "pay":
        context.user_data["p"] = d[1]
        await q.message.reply_text("Send screenshot now.")
    elif d[0] in ["acc", "rej"]:
        uid, g, p = int(d[1]), d[2], d[3]
        if d[0] == "acc":
            key = approve_and_assign_key(uid, g, p)
            if key: await context.bot.send_message(uid, f"✅ Key: `{key}`", parse_mode="Markdown"); await q.edit_message_caption("✅ Approved!")
        else: await context.bot.send_message(uid, "❌ Payment Rejected! Send clear screenshot."); await q.edit_message_caption("❌ Rejected!")

if __name__ == "__main__":
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()
