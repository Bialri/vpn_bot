from aiogram import Dispatcher

from src.bot.vpn_profiles.router import router as profiles_router
from src.bot.registration.router import router as registration_router


dp = Dispatcher()

dp.include_router(profiles_router)
dp.include_router(registration_router)