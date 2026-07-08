async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    # --- HANDLING MENU BUTTONS ---
    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Choose a game:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif text == "🔑 My Keys":
        keys = get_user_keys(user_id)
        if keys:
            msg = "🔑 *Your Purchased Keys:*\n\n"
            for g, p, k in keys:
                msg += f"🎮 {g} ({p}): `{k}`\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("No keys found in your account.")

    elif text == "📞 Support":
        await update.message.reply_text("📞 For support, please contact: @YourAdminUsername") # Change this username

    elif text == "💳 Payment":
        await update.message.reply_text("💳 To buy a key, select 'Games' from the menu, choose your game and plan, and you will receive payment instructions.")

    elif text == "🛠 Admin Panel":
        if user_id == ADMIN_ID:
            await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        else:
            await update.message.reply_text("Unauthorized access.")

    # --- HANDLING PHOTO (PAYMENT) ---
    elif update.message.photo and "game" in context.user_data:
        g, p = context.user_data["game"], context.user_data["plan"]
        kb = [[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}\nGame: {g}\nPlan: {p}", reply_markup=InlineKeyboardMarkup(kb))
        await update.message.reply_text("✅ Screenshot sent to Admin!")
    
    # --- HANDLING ADMIN KEY ADDITION ---
    elif context.user_data.get("state") == "add_keys":
        for k in text.split("\n"):
            save_key(context.user_data["add_game"], context.user_data["add_plan"], k.strip())
        await update.message.reply_text("✅ Keys saved!", reply_markup=admin_keyboard())
        context.user_data.clear()
