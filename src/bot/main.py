import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from src.config import Config
from src.menu import menu_keyboard
from src.auth.auth import Identificator
from src.vpn_profiles.router import router as profiles_router


dp = Dispatcher()

dp.include_router(profiles_router)

@dp.message(CommandStart())
async def start(message: Message):
    id = message.from_user.id
    is_exist = Identificator.check_user_existing(id)
    if is_exist:
        await message.answer('Привет, ты уже смешарик',reply_markup=menu_keyboard)

    else:
        new_user = Identificator.create_user(id)
        await message.answer('Привет, купи vpn',reply_markup=menu_keyboard)

async def main():
    bot = Bot(token=Config.BOT_TOKEN, parse_mode="HTML")
    await bot.delete_webhook()
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())