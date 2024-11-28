import threading
from message_broker import message_broker_module
import asyncio
from dotenv import find_dotenv, load_dotenv
from aiogram import Bot, Dispatcher
import os
from parse.parse_module import Parse
from models.models import *
from config import Config

# Инициализация config
config = Config()

# Инициализация ORM моделей
users = Users('Users')
tokens = Tokens('Tokens')
users_tokens = UsersTokens('UsersTokens')

# Инициализация модулей
broker = message_broker_module.MessageBroker()
parser = Parse(tokens_table=tokens, config=config)

# Создание потоков
thread1 = threading.Thread(target=parser.parse_bybit())
# thread2 = threading.Thread(target=task_module_2)
# thread3 = threading.Thread(target=task_module_3)
# thread4 = threading.Thread(target=task_module_4)
thread5 = threading.Thread(target=broker.run_broker())

# / Запуск бота
# Подключение .env
load_dotenv(find_dotenv())

from chatbot.handlers.user_private import user_private_router

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

async def botStart():
    # Подключение роутера
    dp.include_routers(user_private_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


# Запуск бота
if __name__ == '__main__':
    asyncio.run(botStart())
