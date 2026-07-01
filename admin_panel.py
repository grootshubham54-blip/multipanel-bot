from telegram import ReplyKeyboardMarkup


def admin_keyboard():

    keyboard = [
        ["➕ Add Stock", "🔑 Add Keys"],
        ["📦 Stock", "🗑 Delete Keys"],
        ["👥 Total Users", "💰 Purchases"],
        ["📊 Statistics"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )