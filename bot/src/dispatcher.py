from aiogram import Dispatcher

from vpn_profiles.router import router as profiles_router
from registration.router import router as registration_router
from subscription.router import router as subscription_router


dp = Dispatcher()

dp.include_router(profiles_router)
dp.include_router(registration_router)
dp.include_router(subscription_router)