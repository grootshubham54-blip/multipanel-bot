from telegram import ReplyKeyboardMarkup

def admin_keyboard():
    return ReplyKeyboardMarkup([["🔑 Add Keys", "📦 Stock"], ["👥 Total Users", "🔙 Back to Admin"]], resize_keyboard=True)

def admin_game_selection_keyboard():
    return ReplyKeyboardMarkup([["👑 KING iOS", "WINIOS"], ["NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫"], ["🔙 Back to Admin"]], resize_keyboard=True)
