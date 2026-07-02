from telegram import ReplyKeyboardMarkup

# मुख्य एडमिन मेन्यू
def admin_keyboard():
    keyboard = [
        ["🔑 Add Keys", "📦 Stock"],
        ["📥 Pending Payments", "✅ Approve Payment"],
        ["❌ Reject Payment", "📢 Broadcast"],
        ["👥 Total Users", "📊 Statistics"],
        ["🔙 Back to Main"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# गेम सिलेक्शन मेन्यू
def admin_game_selection_keyboard():
    keyboard = [
        ["👑 KING iOS", "WINIOS"],
        ["NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫"],
        ["𝘿𝙀𝘼𝘿𝙀𝙀𝙔𝙀", "DOLPHIN IOS"],
        ["🔙 Back to Admin"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# प्लान सिलेक्शन मेन्यू
def admin_plan_selection_keyboard():
    keyboard = [
        ["🟢 1 Day", "🟡 1 Week"],
        ["🔴 1 Month"],
        ["🔙 Back to Admin"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
