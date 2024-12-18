import threading
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from matplotlib import pyplot as plt
from matplotlib.dates import date2num, DateFormatter
import pandas as pd
from datetime import datetime
import asyncio
from aiogram import Bot, Dispatcher
from parse import parse_module
from models.models import *
from config import *
from alghorizmization import RSI_main
from queue import Queue

from message_broker.message_broker_module import *


# Инициализация ORM моделей
users = Users('Users')
tokens = Tokens('Tokens')
users_tokens = UsersTokens('UsersTokens')

# # Инициализация модулей
parser = parse_module.Parse(tokens_table=tokens)
alg = RSI_main.AlghorizmizationModule()

q = Queue()

# # Создание потоков
thread1 = threading.Thread(target=parser.parse_bybit)

thread1.start()

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


async def botStart():
    from chatbot.handlers.user_private import user_private_router

    # Подключение роутеров
    dp.include_routers(user_private_router)
    await bot.delete_webhook(drop_pending_updates=True)

    # Параллельный запуск бота и scheduler
    await asyncio.gather(
        dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), skip_updates=True),
        scheduler(delay=15)
    )


# Запуск бота
if __name__ == '__main__':
    asyncio.run(botStart())

