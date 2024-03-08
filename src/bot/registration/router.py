from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
import aiohttp
import random


from src.bot.menu import menu_keyboard
from src.bot.auth.auth import Identificator
from src.bot.vpn_profiles.models import VPNInterface, Server
from src.bot.database import session_maker
from src.bot.config import Config

router = Router(name="registration")

@router.message(CommandStart())
async def start(message: Message):
    id = message.from_user.id
    is_exist = Identificator.check_user_existing(id)
    if is_exist:
        await message.answer('Привет, ты уже смешарик',reply_markup=menu_keyboard)

    else:
        new_user = Identificator.create_user(id)
        with session_maker() as session:
            servers = session.query(Server.country).distinct().all()
            async with aiohttp.ClientSession() as request_session:
                for server in servers:
                    country_servers = session.query(Server).where(Server.country == server[0]).all()
                    country_server = random.choice(country_servers)
                    url = f'http://{country_server.address}/interface/'
                    headers = { "X-API-Key": Config.API_TOKEN }
                    data = {'network_size': Config.USERS_NETWORK_SIZE}
                    async with request_session.post(url=url, headers=headers, json=data) as response:
                        response_data = await response.json()
                        if response.status != 200:
                            session.flush()
                            await message.answer("Произошла ошибка")
                    interface = VPNInterface(interface_name=response_data['interface_name'],
                                             server=country_server.address,
                                             owner=new_user)
                    session.add(interface)
            session.commit()

        await message.answer('Привет, купи vpn',reply_markup=menu_keyboard)