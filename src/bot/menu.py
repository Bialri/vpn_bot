from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Мои VPN профили',),
            KeyboardButton(text='Подписка')
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт",
    selective=True

)
