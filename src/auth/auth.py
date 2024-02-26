from sqlalchemy import select

from src.database import async_session_maker
from .models import User

class Identificator:
    @classmethod
    async def check_user_existing(cls, id: int) -> bool:
        async with async_session_maker() as session:
            user = await session.get(User,id)
            if user is None:
                return False
            return True

    @classmethod
    async def create_user(cls, id: int) -> User:
        async with async_session_maker() as session:
            new_user = User(id=id)
            session.add(new_user)
            await session.commit()
            return new_user