from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
import aiohttp
import random
import sys
sys.path.append('..')

from menu import menu_keyboard
from auth.auth import Identificator
from database import session_maker
from registration.messages import HELLO_MESSAGE


router = Router(name="registration")


@router.message(CommandStart())
async def start(message: Message):
    id = message.from_user.id
    is_exist = Identificator.check_user_existing(id)
    if not is_exist:
        with session_maker() as session:
            Identificator.create_user(id, session)
            session.commit()

    await message.answer(HELLO_MESSAGE,reply_markup=menu_keyboard)