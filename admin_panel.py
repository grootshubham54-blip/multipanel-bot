from telegram import ReplyKeyboardMarkup

def admin_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        ["🔑 Add Keys", "📦 Stock"],
        ["👥 Total Users", "💰 Purchases"],
        ["📊 Statistics"], 
        ["🔙 Back to Main"] # 'Back' को अलग लाइन में रखना ज्यादा यूजर-फ्रेंडली होता है
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_game_selection_keyboard() -> ReplyKeyboardMarkup:
    # इसे 2-2 की ग्रिड में रखें ताकि छोटे स्क्रीन (iPhone/iPad) पर बटन कटे नहीं
    keyboard = [
        ["👑 KING iOS", "WINIOS"],
        ["NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫"],
        ["𝘿𝙀𝘼𝘿𝙀𝙔𝙀", "DOLPHIN IOS"],
        ["🔙 Back to Admin"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
