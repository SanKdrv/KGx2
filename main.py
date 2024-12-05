import threading

from pandas.core._numba import executor

import chatbot.chatbot_module
from message_broker import message_broker_module
import asyncio
from aiogram import Bot, Dispatcher
import config
import os
from parse import parse_module
from models.models import *
from config import *
from alghorizmization import RSI_main
from queue import Queue


# Инициализация ORM моделей
users = Users('Users')
tokens = Tokens('Tokens')
users_tokens = UsersTokens('UsersTokens')

# # Инициализация модулей
# broker = message_broker_module.MessageBroker()
parser = parse_module.Parse(tokens_table=tokens)
alg = RSI_main.AlghorizmizationModule()

q = Queue()

# # Создание потоков
thread1 = threading.Thread(target=parser.parse_bybit)
# thread2 = threading.Thread(target=alg.run)
# thread3 = threading.Thread(target=task_module_3)
# # thread4 = threading.Thread(target=task_module_4)
# thread5 = threading.Thread(target=broker.run_broker)
#
# thread5.start()

thread1.start()
# thread2.start()
# print(thread2.)
# thread2.join()
# thread2.result()

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


async def botStart():
    from chatbot.handlers.user_private import user_private_router
    # Подключение роутера
    dp.include_routers(user_private_router)
    await bot.delete_webhook(drop_pending_updates=True)
    task = asyncio.create_task(coro=scheduler(delay=15))
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def scheduler(delay):
    while True:
        # users_id_list = users.select_all()
        # users_id = [user['UID'] for user in users_id_list]
        # if len(users_id_list) == 0:
        #     print('fdasfs')
        # else:
        #     print('okayu')
        # for user in users_id:
        #     await bot.send_message(user, 'privetqtqeteqwqeteqwtgewq')
        print('jopa')
        await chatbot.chatbot_module.pull_gueue()
        await asyncio.sleep(delay=delay)


# Запуск бота
if __name__ == '__main__':
    asyncio.run(botStart())

