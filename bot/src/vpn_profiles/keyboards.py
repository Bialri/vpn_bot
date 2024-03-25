from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp
import sys
import flag
import pycountry

sys.path.append('..')
from config import Config


async def get_profiles_keyboard(interfaces: list['VPNInterface']) -> InlineKeyboardMarkup:
    profile_keyboard = []
    profiles = []
    for interface in interfaces:
        url = f'http://{interface.server.address}/api/v1/interface/{interface.interface_name}/peers'
        headers = {"X-API-Key": Config.API_TOKEN}
        async with aiohttp.ClientSession() as request_session:
            async with request_session.get(url=url, headers=headers) as response:
                new_profiles = [(interface.interface_name, profile, interface.server.country) for profile in (await response.json())]
                profiles = profiles + new_profiles
    profile_iterator = iter(profiles)
    while (True):
        try:
            keyboard_row = []
            first_profile = next(profile_iterator)
            first_flag = flag.flag(first_profile[2])
            keyboard_row.append(
                InlineKeyboardButton(text=f'{first_profile[1]}{first_flag}',
                                     callback_data=f'profile_{first_profile[0]}_{first_profile[1]}'))
            second_profile = next(profile_iterator)
            second_flag = flag.flag(second_profile[2])
            keyboard_row.append(
                InlineKeyboardButton(text=f'{second_profile[1]}{second_flag}',
                                     callback_data=f'profile_{second_profile[0]}_{second_profile[1]}'))
        except StopIteration:
            break
        finally:
            profile_keyboard.append(keyboard_row)

    create_button = [InlineKeyboardButton(text='Создать новый профиль', callback_data='createprofile')]
    profile_keyboard.append(create_button)
    return InlineKeyboardMarkup(inline_keyboard=profile_keyboard)


def get_profile_keyboard(interface_name, profile_name):
    keyboard = [
        [InlineKeyboardButton(text="Получить QR код", callback_data=f'qr_{interface_name}_{profile_name}'),
         InlineKeyboardButton(text="Получить файл конфигурации",
                              callback_data=f'config_{interface_name}_{profile_name}')],
        [InlineKeyboardButton(text="Удалить профиль", callback_data=f'delete_{interface_name}_{profile_name}')],
        [InlineKeyboardButton(text="Назад", callback_data=f'profiles')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_choice_country_keyboard(interfaces):
    keyboard = []
    for interface in interfaces:
        country_name = pycountry.countries.get(alpha_2=interface.server.country).name
        country_flag = flag.flag(interface.server.country)
        keyboard.append([InlineKeyboardButton(text=f'{country_name}{country_flag}',
                                              callback_data=f'chosenCountry_{interface.server.address}_{interface.interface_name}')])
    keyboard.append([InlineKeyboardButton(text="Отменить",callback_data='cancel_creation')])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_return_button(callback_data):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data=callback_data)]])


def get_delete_confirm_keyboard(callback_data):
    keyboard = [
        [InlineKeyboardButton(text="Удалить", callback_data=f'confirmDelete_{callback_data[0]}_{callback_data[1]}')],
        [InlineKeyboardButton(text="Отменить", callback_data=f'profile_{callback_data[0]}_{callback_data[1]}')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_create_button():
    keyboard = [
        [InlineKeyboardButton(text="Отменить",callback_data='cancel_creation')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
