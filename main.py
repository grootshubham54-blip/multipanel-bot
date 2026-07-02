async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # 1. BROADCAST LOGIC (ब्रॉडकास्ट का फिक्स)
    if context.user_data.get("broadcasting"):
        msg_to_send = text
        context.user_data["broadcasting"] = False
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        conn.close()
        count = 0
        for u in users:
            try: await context.bot.send_message(chat_id=u[0], text=f"📢 *Announcement:*\n\n{msg_to_send}", parse_mode="Markdown")
            except: continue
        await update.message.reply_text(f"✅ Announcement sent to {count} users!", reply_markup=admin_keyboard())
        return

    # 2. NAVIGATION AND BACK BUTTONS
    if text == "🔙 Back to Main" or text == "❌ Cancel Payment":
        context.user_data.clear()  
        await update.message.reply_text("👑 Main Menu", reply_markup=get_main_keyboard(user.id))
        return

    if text == "🔙 Back to Admin":
        context.user_data["adding_key"] = False
        context.user_data["checking_stock"] = False
        context.user_data["selected_game"] = None
        await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
        return

    if text == "🔙 Back to Games":
        await update.message.reply_text(
            "🎮 Games\n\nSelect Game / Loader:",
            reply_markup=ReplyKeyboardMarkup([
                ["👑 KING iOS"], ["WINIOS", "NEXT IOS"],
                ["𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"], ["DOLPHIN IOS"],
                ["🔙 Back to Main"]
            ], resize_keyboard=True)
        )
        return

    # 3. ADMIN ROUTES
    if user.id == ADMIN_ID:
        if text == "⚙️ Admin Panel":
            context.user_data.clear()
            await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
            return
        elif text == "📢 Broadcast":
            context.user_data["broadcasting"] = True
            await update.message.reply_text("📢 Send your announcement message now:", reply_markup=get_back_keyboard("Admin"))
            return
        elif text == "🔑 Add Keys":
            context.user_data["adding_key"] = True
            context.user_data["checking_stock"] = False
            await update.message.reply_text("🎯 Select the game you want to add keys for:", reply_markup=admin_game_selection_keyboard())
            return
        elif text == "📦 Stock":
            context.user_data["checking_stock"] = True
            context.user_data["adding_key"] = False
            await update.message.reply_text("🎯 Select the game to check its individual stock:", reply_markup=admin_game_selection_keyboard())
            return
        # --- बाक़ी एडमिन लॉजिक (Add Keys, Stats, Users) यहाँ जैसा था वैसा ही रहने दें ---
        # (ध्यान दें: आपके पास जो पुराने elif/if थे, उन्हें यहाँ पेस्ट रहने दें)

    # 4. CORE USER MENUS (Games, Plans, Support, Profile, Payment)
    # --- आपका पूरा पुराना Games और Plans का कोड यहाँ नीचे बिल्कुल ऐसे ही लगा दें ---
    # उदाहरण:
    if text == "🎮 Games":
        # ... बाकी आपका ओरिजिनल कोड ...
    
    # [यहाँ अपना बाकी सारा पुराना कोड पेस्ट करें जो गेम्स और पेमेंट के लिए था]
