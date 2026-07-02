# एडमिन पैनल और गेम/प्लान सिलेक्शन लॉजिक (फिक्स्ड)
async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    state = context.user_data.get("state")

    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel":
            await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "select_game"
            await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard())
            
        elif state == "select_game" and text in GAME_PLANS.keys():
            context.user_data["add_game"] = text
            context.user_data["state"] = "select_plan"
            # यहाँ प्लान सिलेक्शन वाला कीबोर्ड कॉल हो रहा है
            await update.message.reply_text(f"Selected {text}. Now select plan:", reply_markup=admin_plan_selection_keyboard())
            
        elif state == "select_plan" and text in ["1 Day", "1 Week", "1 Month"]:
            context.user_data["add_plan"] = text
            context.user_data["state"] = "add_keys"
            await update.message.reply_text(f"Enter keys for {context.user_data['add_game']} ({text}):", reply_markup=ReplyKeyboardMarkup([["🔙 Back to Admin"]], resize_keyboard=True))
            
        elif state == "add_keys":
            keys = text.split("\n")
            for k in keys:
                if k.strip():
                    save_key(context.user_data["add_game"], k.strip(), context.user_data["add_plan"])
            await update.message.reply_text("✅ Keys Saved!", reply_markup=admin_keyboard())
            context.user_data.clear()

        elif text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
            
        # ... बाकी एडमिन लॉजिक वही है
