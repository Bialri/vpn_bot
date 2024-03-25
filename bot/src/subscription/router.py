import asyncio
from datetime import date
from dateutil.relativedelta import relativedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import random
import aiohttp
import pika
import json
import datetime
import sys

sys.path.append('..')

from database import session_maker
from auth.auth import User
from vpn_profiles.models import Server, VPNInterface
from config import Config
from subscription.keyboards import get_subscription_keyboard, get_subscription_choice_keyboard, \
    get_subscription_payment_keyboard
from bot import bot
from subscription.payments import create_payment_subscription, check_payment_subscription, refund_payment, \
    capture_payment

router = Router(name='vpn_profiles')


@router.message(F.text.lower() == "подписка")
async def subscription(message: Message):
    with session_maker() as session:
        user = session.query(User).where(User.id == message.from_user.id).first()
    if not user.last_action:
        keyboard_text = 'Оформить'
        answer_text = 'Для пользования сервисом оформите подписку'
    elif user.subscription_till < date.today():
        keyboard_text = 'Оформить'
        answer_text = 'Ваша подписка истекла, для того чтобы продолжить пользоваться сервисом необходимо продлить её'
    else:
        keyboard_text = 'Продлить'
        answer_text = f'Ваша подписка действительная до <b>{user.subscription_till}</b>'
    keyboard = get_subscription_keyboard(keyboard_text)
    await message.answer(text=answer_text, reply_markup=keyboard)


@router.callback_query(lambda callback_query: callback_query.data == "subscribe")
async def subscription_choice(callback: CallbackQuery):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    keyboard = get_subscription_choice_keyboard()
    await callback.message.answer(text="Выберите срок подписки", reply_markup=keyboard)


# TODO: REFACTOR
@router.callback_query(lambda callback_query: callback_query.data.split('_')[0] == "subscribeBuy")
async def subscription_buy(callback: CallbackQuery):
    call_data = callback.data.split('_')[1:]
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    payment_url, payment = create_payment_subscription(f"Подписка на {call_data[0]} месяцев", int(call_data[1]))
    keyboard = get_subscription_payment_keyboard("Оплатить", payment_url)
    await callback.message.answer(text=f"Оплатите подписку на {call_data[0]} Месяцев", reply_markup=keyboard)
    status = await check_payment_subscription(payment.id)
    try:
        if status:
            with session_maker() as session:
                user = session.query(User).where(User.id == callback.from_user.id).first()
                if not user.last_action or not user.interfaces:
                    countries = session.query(Server.country).distinct().all()
                    async with aiohttp.ClientSession() as request_session:
                        for country in countries:
                            country_servers = session.query(Server).where(Server.country == country[0]).all()
                            country_server = random.choice(country_servers)
                            url = f'http://{country_server.address}/api/v1/interface/'
                            headers = {"X-API-Key": Config.API_TOKEN}
                            request_data = {'network_size': Config.USERS_NETWORK_SIZE}
                            try:
                                async with request_session.post(url=url, headers=headers,
                                                                json=request_data) as response:
                                    response_data = await response.json()
                                    if response.status != 200:
                                        session.flush()
                                    interface = VPNInterface(interface_name=response_data['interface_name'],
                                                             server=country_server,
                                                             owner=user)
                                    session.add(interface)
                            except aiohttp.client_exceptions.ClientConnectorError as e:
                                session.flush()
                                raise

                elif user.subscription_till < date.today() and user.vpn_interfaces:
                    connection = pika.BlockingConnection(Config.PIKA_PARAMETRS)
                    channel = connection.channel()
                    interfaces = session.query(VPNInterface).where(VPNInterface.owner == user).all()
                    for interface in interfaces:
                        query = {
                            'interface': f'{interface.interface_name}',
                            'status': "running"
                        }
                        channel.basic_publish(exchange='route',
                                              routing_key=interface.server.address,
                                              body=json.dumps(query))

                user.last_action = datetime.datetime.now()
                subs_ext = relativedelta(months=int(call_data[0]))
                user.subscription_till = date.today() + subs_ext
                session.commit()

            await callback.message.answer(text='Оплата успешна')

        else:
            await callback.message.answer(text='Платёж отклонён')

    except Exception:
        refund_payment(payment.id)
        await callback.message.answer(text="К сожалению произошла ошибка, средства будут возвращены в ближайшее время.")
    else:
        capture_payment(payment.id)
