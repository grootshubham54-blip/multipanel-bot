import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# आपके पुराने वाले imports यहाँ रहने दें
from database import create_tables, add_user, save_key, get_stock, DB_NAME
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# (बाकी सब कुछ जो आपके पुराने working कोड में था, उसे यहाँ रहने दें)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # --- 1. BROADCAST LOGIC (वही वाला जो काम कर रहा था) ---
    if context.user_data.get("broadcasting"):
        # ... (आपका वर्किंग ब्रॉडकास्ट कोड) ...
        return

    # --- 2. KEY ADDING (PLAN SELECTION के साथ) ---
    if user.id == ADMIN_ID and context.user_data.get("adding_key"):
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("Admin Control Panel", reply_markup=admin_keyboard())
            return
        
        if not context.user_data.get("selected_game"):
            context.user_data["selected_game"] = text
            await update.message.reply_text("Select Plan:", reply_markup=ReplyKeyboardMarkup([["1 DAY", "1 WEEK", "1 MONTH"]], resize_keyboard=True))
            return
        elif not context.user_data.get("selected_plan"):
            context.user_data["selected_plan"] = text
            await update.message.reply_text("Send the Key:", reply_markup=ReplyKeyboardMarkup([["🔙 Back to Admin"]], resize_keyboard=True))
            return
        else:
            save_key(context.user_data["selected_game"], text, context.user_data["selected_plan"])
            await update.message.reply_text("✅ Key Added successfully!", reply_markup=admin_keyboard())
            context.user_data.clear()
            return

    # --- 3. GAMES & ESING CERTIFICATE ---
    if text == "🎮 Games":
        await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup([
            ["👑 KING iOS"], ["WINIOS", "NEXT IOS"], ["𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"], 
            ["DOLPHIN IOS", "ESING CERTIFICATE"], ["🔙 Back to Main"]
        ], resize_keyboard=True))
        return
        
    if text == "ESING CERTIFICATE":
        await update.message.reply_text("📄 ESING CERTIFICATE is now available.")
        return

    # --- 4. बाकी सब (आपके पुराने वर्किंग कोड के elif यहाँ जोड़ें) ---
    # [यहाँ अपना बाकी सारा पुराना कोड पेस्ट करें]

# (अपना original main() फंक्शन इसके नीचे रखें)
