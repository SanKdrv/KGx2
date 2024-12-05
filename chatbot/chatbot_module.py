import os
import time
import asyncio

from aiogram import Bot, Dispatcher
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
    while True:
        alg = RSI_main.AlghorizmizationModule()
        q = alg.process_data()
        print(q)
        # try:
        #     # Проверяем наличие элементов в очереди
        #     if len(q) > 0:
        #
        #         # Получаем первое сообщение из очереди
        #         message = q # Ограничиваем время ожидания
        #
        #         # Обрабатываем полученное сообщение
        #         print(f"Получено сообщение: {message}")
        #
        #         # Очищаем очередь после обработки
        #         # q.task_done()
        #
        # except q.Empty:
        #     print("Очередь пуста или время ожидания истекло.")
        #
        # except Exception as e:
        #     print(f"Ошибка при проверке очереди: {str(e)}")

        # Ожидаем 15 минут перед следующей проверкой
        await asyncio.sleep(15)
        time.sleep(15)  # 900 секунд = 15 минут