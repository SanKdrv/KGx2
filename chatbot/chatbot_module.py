import os
import time
import asyncio

from aiogram import Bot, Dispatcher

import chatbot.handlers.user_private
# from dotenv import find_dotenv, load_dotenv
from chatbot.handlers.user_private import user_private_router
# from main import q
from alghorizmization import RSI_main


def start_bot():
    # Подключение .env
    # load_dotenv(find_dotenv())

    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()

    # Подключение роутера
    dp.include_routers(user_private_router)

    # Запуск работы бота
    async def starting_polling():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    # Запуск бота asyncio.run(botStart())


async def pull_gueue():
    # await asyncio.sleep(15)
    # print('jopa')
    alg = RSI_main.AlghorizmizationModule()
    q = alg.process_data()
    if not q:
        print('Печалька')
    print(q)
    for data in q:
        await chatbot.handlers.user_private.rsi_signal(data[0])
