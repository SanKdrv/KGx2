import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeAllPrivateChats
from dotenv import find_dotenv, load_dotenv


# Подключение .env
load_dotenv(find_dotenv())

from chatbot.handlers.user_private import user_private_router

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

# Подключение роутера
dp.include_routers(user_private_router)

# Запуск работы бота
async def botStart():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# Запуск бота asyncio.run(botStart())