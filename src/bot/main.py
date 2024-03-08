import asyncio
import logging
import sys


from dispatcher import dp
from bot import bot



async def main():
    await bot.delete_webhook()
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())