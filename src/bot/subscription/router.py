from datetime import date
from dateutil.relativedelta import relativedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import random
import aiohttp

from src.bot.database import session_maker
from src.bot.auth.auth import User
from src.bot.vpn_profiles.models import Server, VPNInterface
from src.bot.config import Config
from src.bot.subscription.keyboards import get_subscription_keyboard, get_subscription_choice_keyboard, \
    get_subscription_payment_keyboard
from src.bot.bot import bot
from src.bot.subscription.payments import create_payment_subscription, check_payment_subscription

router = Router(name='vpn_profiles')


@router.message(F.text.lower() == "подписка")
async def subscription(message: Message):
    with session_maker() as session:
        user = session.query(User).where(User.id == message.from_user.id).first()
    if user.subscription_till < date.today():
        keyboard = get_subscription_keyboard("Оформить")
        await message.answer(
            text="Ваша подписка истекла, для того чтобы продолжить пользоваться сервисом необходимо продлить её",
            reply_markup=keyboard)
    else:
        keyboard = get_subscription_keyboard("Продлить")
        await message.answer(text=f"Ваша подписка действительная до {user.subscription_till}", reply_markup=keyboard)


@router.callback_query(lambda callback_query: callback_query.data == "subscribe")
async def subscription_choice(callback: CallbackQuery):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    keyboard = get_subscription_choice_keyboard()
    await callback.message.answer(text="Выберите срок подписки", reply_markup=keyboard)


@router.callback_query(lambda callback_query: callback_query.data.split('_')[0] == "subscribeBuy")
async def subscription_buy(callback: CallbackQuery):
    data = callback.data.split('_')[1:]
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    payment_url, payment = create_payment_subscription(f"Подписка на {data[0]} месяцев", int(data[1]))
    keyboard = get_subscription_payment_keyboard("Оплатить", payment_url)
    await callback.message.answer(text=f"Оплатите подписку на {data[0]} Месяцев", reply_markup=keyboard)
    status = await check_payment_subscription(payment.id)
    if status:
        subs_ext = relativedelta(months=int(data[0]))
        with session_maker() as session:
            user = session.query(User).where(User.id == callback.from_user.id).first()
            user.subscription_till = user.subscription_till + subs_ext
            session.commit()

        await callback.message.answer(text='Оплата успешна')

        if user.last_action is None:
            with session_maker() as session:
                user = session.query(User).where(User.id == callback.from_user.id)
                servers = session.query(Server.country).distinct().all()
                async with aiohttp.ClientSession() as request_session:
                    for server in servers:
                        country_servers = session.query(Server).where(Server.country == server[0]).all()
                        country_server = random.choice(country_servers)
                        url = f'http://{country_server.address}/api/v1/interface/'
                        headers = {"X-API-Key": Config.API_TOKEN}
                        data = {'network_size': Config.USERS_NETWORK_SIZE}
                        try:
                            async with request_session.post(url=url, headers=headers, json=data) as response:
                                response_data = await response.json()
                                if response.status != 200:
                                    session.flush()
                        except aiohttp.client_exceptions.ClientConnectorError as e:
                            session.flush()

                        interface = VPNInterface(interface_name=response_data['interface_name'],
                                                 server=country_server,
                                                 owner=user)
                        session.add(interface)
                        session.commit()

    else:
        await callback.message.answer(text='Платёж отклонён')
