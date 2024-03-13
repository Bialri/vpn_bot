from aiogram import Dispatcher

from src.bot.vpn_profiles.router import router as profiles_router
from src.bot.registration.router import router as registration_router
from src.bot.subscription.router import router as subscription_router


dp = Dispatcher()

dp.include_router(profiles_router)
dp.include_router(registration_router)
dp.include_router(subscription_router)