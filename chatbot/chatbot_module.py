import os
from aiogram import Bot, Dispatcher
from ..config import *
from chatbot.handlers.user_private import user_private_router


def start_bot():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    # Подключение роутера
    dp.include_routers(user_private_router)

    # Запуск работы бота
    async def starting_polling():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    # Запуск бота asyncio.run(botStart())