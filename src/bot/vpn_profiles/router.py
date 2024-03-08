from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import qrcode
import aiohttp
import io

from src.bot.database import session_maker
from src.bot.auth.models import User
from src.bot.vpn_profiles.models import VPNInterface
from src.bot.vpn_profiles.keyboards import get_profiles_keyboard, get_profile_keyboard, get_return_button
from src.bot.config import Config
from src.bot.bot import bot

router = Router(name='vpn_profiles')


@router.callback_query(lambda callback_query: callback_query.data == "profiles")
async def callback_profiles(callback_query: CallbackQuery):
    with session_maker() as session:
        user = session.get(User, callback_query.message.from_user.id)
        profile_keyboard = await get_profiles_keyboard(user.vpn_interfaces)
        await bot.delete_message(callback_query.message.chat.id,callback_query.message.message_id)
        await bot.send_message(callback_query.message.chat.id, text='Ваши профили:', reply_markup=profile_keyboard)

@router.message(F.text.lower() == "мои vpn профили")
async def callback_profiles(message: Message):
    with session_maker() as session:
        user = session.get(User, message.from_user.id)
        profile_keyboard = await get_profiles_keyboard(user.vpn_interfaces)
        await message.answer(text='Ваши профили:', reply_markup=profile_keyboard)



@router.callback_query(lambda callback_query: callback_query.data.split('_')[0] == 'profile')
async def profile(callback: CallbackQuery):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data = callback.data.split('_')[1:]
    keyboard = get_profile_keyboard(f'{data[0]}_{data[1]}')
    await callback.message.answer(text='Профиль', reply_markup=keyboard)


@router.callback_query(lambda callback_query: callback_query.data.split('_')[0] == 'qr')
async def get_profile_qr(callback: CallbackQuery):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data = callback.data.split('_')[1:]

    async with aiohttp.ClientSession() as request_session:
        with session_maker() as session:
            user = session.get(User, callback.message.from_user.id)
            interface = session.query(VPNInterface).where(VPNInterface.interface_name == data[0]).first()
        url = f'http://{interface.server}/interface/{interface.interface_name}/peer/{data[1]}/config'
        headers = {"X-API-Key": Config.API_TOKEN}
        async with request_session.get(url=url, headers=headers) as response:
            json_response = await response.json()
        qr = qrcode.make(json_response['config'])
        buf = io.BytesIO()
        qr.save(buf)
        buf.seek(0)
        buf_file = BufferedInputFile(buf.read(), 'config.conf')
        keyboard = get_return_button("profiles")
        await bot.send_photo(callback.message.chat.id, buf_file, reply_markup=keyboard)


@router.callback_query(lambda callback_query: callback_query.data.split('_')[0] == 'config')
async def get_profile_config(callback: CallbackQuery):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data = callback.data.split('_')[1:]

    async with aiohttp.ClientSession() as request_session:
        with session_maker() as session:
            user = session.get(User, callback.message.from_user.id)
            interface = session.query(VPNInterface).where(VPNInterface.interface_name == data[0]).first()
        url = f'http://{interface.server}/interface/{interface.interface_name}/peer/{data[1]}/config'
        headers = {"X-API-Key": Config.API_TOKEN}
        async with request_session.get(url=url, headers=headers) as response:
            json_response = await response.json()
        buf_file = BufferedInputFile(json_response['config'].encode('utf-8'), 'config.conf')
        await bot.send_document(callback.message.chat.id, buf_file)


class CreateProfile(StatesGroup):
    chosing_profile_name = State()


@router.callback_query(lambda callback_query: callback_query.data == 'createprofile')
async def request_profile_name(callback: CallbackQuery, state: FSMContext):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await bot.send_message(callback.message.chat.id, 'Введите имя профиля')
    await state.set_state(CreateProfile.chosing_profile_name)


@router.message(CreateProfile.chosing_profile_name)
async def create_profile(message: Message, state: FSMContext):
    await state.update_data(profile_name=message.text)

    async with aiohttp.ClientSession() as request_session:
        with session_maker() as session:
            user = session.get(User, message.from_user.id)
            interface = session.query(VPNInterface).where(VPNInterface.owner == user).first()
            url = f'http://{interface.server}/interface/{interface.interface_name}/peer'
            headers = {"X-API-Key": Config.API_TOKEN}
            data = {'peer_name': message.text}
            async with request_session.post(url=url, headers=headers, params=data) as response:
                print(await response.text())
                if response.status != 200:
                    await message.answer("По пизде что-то пошло")
                else:
                    await message.answer("Профиль успешно создан")
            await state.clear()
