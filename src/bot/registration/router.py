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
        with session_maker() as session:
            Identificator.create_user(id, session)
            session.commit()

        await message.answer('Привет, купи vpn',reply_markup=menu_keyboard)