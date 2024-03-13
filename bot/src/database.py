from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import Config

DATABASE_URL = Config.DB_URI

class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL)
session_maker = sessionmaker(engine)

