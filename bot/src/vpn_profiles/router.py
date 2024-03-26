from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import qrcode
import io
from datetime import date
import sys

sys.path.append('..')

from database import session_maker
from auth.models import User
from vpn_profiles.models import VPNInterface, Server
from vpn_profiles.keyboards import (get_profiles_keyboard, get_profile_keyboard, get_return_button,
                                    get_delete_confirm_keyboard, get_choice_country_keyboard,
                                    get_cancel_create_button)
from bot import bot
from vpn_profiles.requester import BotRequesterSession

router = Router(name='vpn_profiles')


def subscription_validation(user_id):
    with session_maker() as session:
        user = session.get(User, user_id)
        return user.subscription_till < date.today()


@router.callback_query(lambda callback_query: callback_query.data == "profiles")
async def callback_profiles(callback_query: CallbackQuery):
    if subscription_validation(callback_query.from_user.id):
        await callback_query.message.answer("Срок подписки истёк, чтобы востановить доступ, продлите её.")
        return

    with session_maker() as session:
        user = session.get(User, callback_query.from_user.id)
        profile_keyboard = await get_profiles_keyboard(user.vpn_interfaces)
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        await bot.send_message(callback_query.message.chat.id, text='Ваши профили:', reply_markup=profile_keyboard)


@router.message(F.text.lower() == "мои vpn профили")
async def callback_profiles(message: Message):
    if subscription_validation(message.from_user.id):
        await message.answer("Срок подписки истёк, чтобы востановить доступ, продлите её.")
        return

    with session_maker() as session:
        user = session.get(User, message.from_user.id)
        profile_keyboard = await get_profiles_keyboard(user.vpn_interfaces)
        await message.answer(text='Ваши профили:', reply_markup=profile_keyboard)
        return


@router.callback_query(lambda callback_query: callback_query.data.split('_')[0] == 'profile')
async def profile(callback: CallbackQuery):
    if subscription_validation(callback.from_user.id):
        await callback.message.answer("Срок подписки истёк, чтобы востановить доступ, продлите её.")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data = callback.data.split('_')[1:]
    keyboard = get_profile_keyboard(data[0], data[1])
    await callback.message.answer(text=f'Профиль {data[1]}', reply_markup=keyboard)


@router.callback_query(lambda callback_query: callback_query.data.split('_')[0] == 'qr')
async def get_profile_qr(callback: CallbackQuery):
    if subscription_validation(callback.from_user.id):
        await callback.message.answer("Срок подписки истёк, чтобы востановить доступ, продлите её.")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data = callback.data.split('_')[1:]

    with session_maker() as session:
        user = session.query(User).where(User.id == callback.from_user.id).first()
        print(user.id)
        interface = session.query(VPNInterface).where(VPNInterface.interface_name == data[0],
                                                      VPNInterface.owner_id == user.id).first()
        async with BotRequesterSession(interface.server.address) as request_session:
            url = f'/api/v1/interface/{interface.interface_name}/peer/{data[1]}/config'
            async with request_session.get(url=url) as response:
                json_response = await response.json()

            qr = qrcode.make(json_response['config'])
            buf = io.BytesIO()
            qr.save(buf)
            buf.seek(0)
            buf_file = BufferedInputFile(buf.read(), 'config.conf')
            keyboard = get_return_button(f"profile_{data[0]}_{data[1]}")
            await bot.send_photo(callback.message.chat.id, buf_file, reply_markup=keyboard)


@router.callback_query(lambda callback_query: callback_query.data.split('_')[0] == 'config')
async def get_profile_config(callback: CallbackQuery):
    if subscription_validation(callback.from_user.id):
        await callback.message.answer("Срок подписки истёк, чтобы востановить доступ, продлите её.")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data = callback.data.split('_')[1:]

    with session_maker() as session:
        user = session.query(User).where(User.id == callback.from_user.id).first()
        interface = session.query(VPNInterface).where(VPNInterface.interface_name == data[0],
                                                      VPNInterface.owner == user).first()

        async with BotRequesterSession(host=interface.server.address) as request_session:
            url = f'/api/v1/interface/{interface.interface_name}/peer/{data[1]}/config'
            async with request_session.get(url=url) as response:
                json_response = await response.json()
            buf_file = BufferedInputFile(json_response['config'].encode('utf-8'), f'{interface.interface_name}.conf')
            keyboard = get_return_button(f"profile_{data[0]}_{data[1]}")
            await bot.send_document(callback.message.chat.id, buf_file, reply_markup=keyboard)


class CreateProfile(StatesGroup):
    chosing_profile_name = State()
    chosing_profile_country = State()


@router.callback_query(lambda callback_query: callback_query.data == 'cancel_creation')
async def cancel_create_profile(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


@router.callback_query(lambda callback_query: callback_query.data == 'createprofile')
async def request_profile_name(callback: CallbackQuery, state: FSMContext):
    if subscription_validation(callback.from_user.id):
        await callback.message.answer("Срок подписки истёк, чтобы востановить доступ, продлите её.")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    message = await bot.send_message(callback.message.chat.id, 'Введите имя профиля',
                                     reply_markup=get_cancel_create_button())
    await state.set_state(CreateProfile.chosing_profile_name)
    await state.set_data({'choose_name_message': message})


@router.message(CreateProfile.chosing_profile_name)
async def request_profile_country(message: Message, state: FSMContext):
    data = await state.get_data()
    choose_name_message = data['choose_name_message']
    await bot.edit_message_reply_markup(chat_id=choose_name_message.chat.id, message_id=choose_name_message.message_id)
    if subscription_validation(message.from_user.id):
        await message.answer("Срок подписки истёк, чтобы востановить доступ, продлите её.")
        return
    await state.set_data({'name': message.text})

    with session_maker() as session:
        user = session.query(User).where(User.id == message.from_user.id).first()
        interfaces = session.query(VPNInterface).where(VPNInterface.owner == user).all()
        keyboard = get_choice_country_keyboard(interfaces)
    await message.answer("Выберите страну", reply_markup=keyboard)
    await state.set_state(CreateProfile.chosing_profile_country)


@router.callback_query(CreateProfile.chosing_profile_country)
async def create_profile(callback: CallbackQuery, state: FSMContext):
    if subscription_validation(callback.from_user.id):
        await callback.message.answer("Срок подписки истёк, чтобы востановить доступ, продлите её.")
        return

    data = callback.data.split("_")[1:]
    profile_name = (await state.get_data())['name']
    async with BotRequesterSession(host=data[0]) as request_session:
        url = f'/api/v1/interface/{data[1]}/peer'
        request_data = {'peer_name': profile_name}
        async with request_session.post(url=url, json=request_data) as response:
            if response.status != 200:
                await callback.message.answer("По что-то пошло не так")
            else:
                await callback.message.answer("Профиль успешно создан")
        await state.clear()
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)


@router.callback_query(lambda callback_query: callback_query.data.split("_")[0] == 'delete')
async def delete_confirm_request_profile(callback_query: CallbackQuery):
    if subscription_validation(callback_query.from_user.id):
        await callback_query.message.answer("Срок подписки истёк, чтобы востановить доступ, продлите её.")
        return

    data = callback_query.data.split('_')[1:]
    keyboard = get_delete_confirm_keyboard(data)
    await callback_query.message.answer(text="Подтвердите действие", reply_markup=keyboard)
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)


@router.callback_query(lambda callback_query: callback_query.data.split("_")[0] == 'confirmDelete')
async def delete_profile(callback_query: CallbackQuery):
    if subscription_validation(callback_query.from_user.id):
        await callback_query.message.answer("Срок подписки истёк, чтобы востановить доступ, продлите её.")
        return

    data = callback_query.data.split('_')[1:]
    with session_maker() as session:
        user = session.get(User, callback_query.from_user.id)
        interface = session.query(VPNInterface).where(VPNInterface.owner == user).first()
        async with BotRequesterSession(host=interface.server.address) as request_session:
            url = f'/api/v1/interface/{interface.interface_name}/peer/{data[1]}'
            async with request_session.delete(url=url) as response:
                if response.status != 200:
                    await callback_query.message.answer("По что-то пошло не так")
                else:
                    await callback_query.message.answer("Профиль успешно удалён")

    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
