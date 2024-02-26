from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from src.database import async_session_maker
from src.auth.models import VPNProfile
from src.auth.models import User

router = Router(name='vpn_profiles')

@router.message(F.text.lower() == "мои vpn профили")
async def vpn(message: Message):
    async with async_session_maker() as session:
        user = await session.get(User, message.from_user.id)
        print(user.vpn_profiles)
