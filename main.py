import threading
from message_broker import message_broker_module
import asyncio
from aiogram import Bot, Dispatcher
import config
import os
from parse import parse_module
from models.models import *
from config import *
from chatbot.handlers.user_private import user_private_router


# Инициализация ORM моделей
users = Users('Users')
tokens = Tokens('Tokens')
users_tokens = UsersTokens('UsersTokens')

# Инициализация модулей
broker = message_broker_module.MessageBroker()
parser = parse_module.Parse(tokens_table=tokens)

# Создание потоков
thread1 = threading.Thread(target=parser.parse_bybit())
# thread2 = threading.Thread(target=task_module_2)
# thread3 = threading.Thread(target=task_module_3)
# thread4 = threading.Thread(target=task_module_4)
thread5 = threading.Thread(target=broker.run_broker())


bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

async def botStart():
    # Подключение роутера
    dp.include_routers(user_private_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


# Запуск бота
if __name__ == '__main__':
    asyncio.run(botStart())
