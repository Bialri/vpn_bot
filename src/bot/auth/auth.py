from sqlalchemy import select
from sqlalchemy.orm import Session

from src.bot.database import session_maker
from src.bot.auth.models import User

class Identificator:
    @classmethod
    def check_user_existing(cls, id: int) -> bool:
        with session_maker() as session:
            user = session.get(User,id)
            if user is None:
                return False
            return True

    @classmethod
    def create_user(cls, id: int, session: Session) -> User:
        new_user = User(id=id)
        session.add(new_user)
        return new_user