from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_subscription_keyboard(text: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=text, callback_data="subscribe")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_subscription_choice_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="1 месяц", callback_data="subscribeBuy_1_120")],
        [InlineKeyboardButton(text="3 месяцeв", callback_data="subscribeBuy_3_350")],
        [InlineKeyboardButton(text="6 месяцев", callback_data="subscribeBuy_6_600")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_subscription_payment_keyboard(title,url) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=title, url=url)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)