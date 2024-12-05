import threading
import time

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


# async def botStart():
#     from chatbot.handlers.user_private import user_private_router
#     # Подключение роутера
#     dp.include_routers(user_private_router)
#     await bot.delete_webhook(drop_pending_updates=True)
#     task = asyncio.create_task(coro=scheduler(delay=15))
#     # await scheduler(delay=15)
#     await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), skip_updates = True,)


# async def scheduler(delay):
#     while True:
#         # print('jopa')
#         # await chatbot.chatbot_module.pull_gueue()
#         alg = RSI_main.AlghorizmizationModule()
#         data = alg.process_data()
#         tasks = []
#         for item in data:
#             tiker = item[0][:-4]
#             print(tiker)
#             token_UID = tokens.get_token_ID(item[0])
#             s = f'https://www.bybit.com/ru-RU/trade/spot/{tiker}/USDT'
#             users_id_list = users_tokens.get_users_by_token(int(token_UID))
#             tasks += [bot.send_message(chat_id=user,
#                                        text=f'Заносик, покупай здесь: https://www.bybit.com/ru-RU/trade/spot/{tiker}/USDT')
#                       for user in users_id_list]
#         # all_tasks = asyncio.all_tasks()
#         # print(all_tasks)
#         await asyncio.gather(*tasks)
#         await asyncio.sleep(delay=delay)
#         # time.sleep(10)
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


async def scheduler(delay):
    while True:
        try:
            alg = RSI_main.AlghorizmizationModule()
            data = alg.process_data()
            tasks = []
            print(data)
            for item in data:
                tiker = item[0][:-4]
                print(tiker)
                token_UID = tokens.get_token_ID(item[0])
                s = f'https://www.bybit.com/ru-RU/trade/spot/{tiker}/USDT'
                users_id_list = users_tokens.get_users_by_token(int(token_UID))
                tasks += [bot.send_message(
                    chat_id=user,
                    text=f'Заносик, покупай здесь: {s}'
                ) for user in users_id_list]
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Ошибка в scheduler: {e}")
            continue
        await asyncio.sleep(delay)

# Запуск бота
if __name__ == '__main__':
    asyncio.run(botStart())

