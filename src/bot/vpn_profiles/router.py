from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from src.database import session_maker
from src.auth.models import User
from src.vpn_profiles.models import VPNProfile
from src.vpn_profiles.keyboards import get_profiles_keyboard

router = Router(name='vpn_profiles')

@router.message(F.text.lower() == "мои vpn профили")
async def vpn(message: Message):
    with session_maker() as session:
        user = session.get(User, message.from_user.id)
        profile_keyboard = get_profiles_keyboard(user.vpn_profiles)
        print(user.vpn_profiles)
        await message.answer(text='Ваши профили:', reply_markup=profile_keyboard)

@router.callback_query(lambda callback_query: callback_query.data.split('_')[0] == 'profile')
async def profile(callback: CallbackQuery):
    pass

@router.callback_query(lambda callback_query: callback_query.data == 'create_profile')
async def create_profile(callback: CallbackQuery):
