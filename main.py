async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # 1. GLOBAL NAVIGATION
    if text in ["🔙 Back to Main", "❌ Cancel Payment"]:
        context.user_data.clear()
        await update.message.reply_text("👑 Main Menu", reply_markup=get_main_keyboard(user.id))
        return

    # 2. ADMIN LOGIC
    if user.id == ADMIN_ID:
        if text == "⚙️ Admin Panel":
            await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
            return
        elif text == "🔑 Add Keys":
            context.user_data["adding_key"] = True
            await update.message.reply_text("🎯 Select game:", reply_markup=admin_game_selection_keyboard())
            return
        elif text == "📦 Stock":
            context.user_data["checking_stock"] = True
            await update.message.reply_text("🎯 Select game to check stock:", reply_markup=admin_game_selection_keyboard())
            return
        # यहाँ बाकी एडमिन बटन (Users, Purchases, Statistics) भी जोड़ें...

    # 3. USER NAVIGATION (ये अब 'Admin Logic' के बाहर है, तो अब काम करेगा)
    if text == "🎮 Games":
        await update.message.reply_text(
            "🎮 Select Game / Loader:",
            reply_markup=ReplyKeyboardMarkup([
                ["👑 KING iOS", "WINIOS"],
                ["NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫"],
                ["𝘿𝙀𝘼𝘿𝙀𝙔𝙀", "DOLPHIN IOS"],
                ["🔙 Back to Main"]
            ], resize_keyboard=True)
        )
    
    # 4. PLAN SELECTION (यहाँ अपने बाकी के Plan Logic जोड़ें)
    elif text == "👑 KING iOS":
        # आपका KING iOS वाला लॉजिक...
        pass
    
    # ...बाकी के गेम्स का लॉजिक...
