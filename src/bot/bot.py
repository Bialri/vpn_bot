from src.bot.config import Config
from aiogram import Bot


bot = Bot(token=Config.BOT_TOKEN, parse_mode="HTML")