from telegram import ReplyKeyboardMarkup

def admin_keyboard():
    keyboard = [
        ["🔑 Add Keys", "📦 Stock"],
        ["📢 Broadcast"],
        ["👥 Total Users", "💰 Purchases", "📊 Statistics"],
        ["🔙 Back to Main"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_game_selection_keyboard():
    keyboard = [
        ["👑 KING iOS", "WINIOS"],
        ["NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫"],
        ["𝘿𝙀𝘼𝘿𝙀𝙔𝙀", "DOLPHIN IOS"],
        ["🔙 Back to Admin"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
