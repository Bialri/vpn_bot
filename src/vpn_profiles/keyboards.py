from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_profiles_keyboard(profiles: list['VPNProfile']) -> InlineKeyboardMarkup:
    profile_keyboard = []
    profile_iterator = iter(profiles)
    while(True):
        try:
            keyboard_row = []
            first_profile = next(profile_iterator)
            keyboard_row.append(
                InlineKeyboardButton(text=first_profile.name, callback_data=f'profile_{first_profile.id}'))
            second_profile = next(profile_iterator)
            keyboard_row.append(
                InlineKeyboardButton(text=second_profile.name, callback_data=f'profile_{second_profile.id}'))
        except StopIteration:
            break
        finally:
            profile_keyboard.append(keyboard_row)

    create_button = [InlineKeyboardButton(text='Создать новый профиль', callback_data='create_profile')]
    profile_keyboard.append(create_button)
    return InlineKeyboardMarkup(inline_keyboard=profile_keyboard)
