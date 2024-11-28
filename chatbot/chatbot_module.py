import os
from aiogram import Bot, Dispatcher
from dotenv import find_dotenv, load_dotenv
from chatbot.handlers.user_private import user_private_router


def start_bot():
    # Подключение .env
    load_dotenv(find_dotenv())

    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()

    # Подключение роутера
    dp.include_routers(user_private_router)

    # Запуск работы бота
    async def starting_polling():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    # Запуск бота asyncio.run(botStart())