from aiohttp import ClientSession
import sys
sys.path.append("..")

from config import Config

class BotRequesterSession(ClientSession):
    def __init__(self, host: str):
        headers = {"X-API-Key": Config.API_TOKEN}
        super().__init__(base_url=f'http://{host}', headers=headers)