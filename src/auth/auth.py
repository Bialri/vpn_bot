from sqlalchemy import select

from src.database import session_maker
from src.auth.models import User

class Identificator:
    @classmethod
    def check_user_existing(cls, id: int) -> bool:
        with session_maker() as session:
            user = session.get(User,id)
            if user is None:
                return False
            return True

    @classmethod
    def create_user(cls, id: int) -> User:
        with session_maker() as session:
            new_user = User(id=id)
            session.add(new_user)
            session.commit()
            return new_user