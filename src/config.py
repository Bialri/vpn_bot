import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    DB_URI = os.environ.get("DB_URI")