from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, or_f


user_private_router = Router()

# Обработчик /start
@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        text = "Примите, пожалуйста, политику конфиденциальности:",
    )
    # Обработка принятия п.к.

@user_private_router.message(or_f(Command('menu'), (F.text.lower() == "меню")))
async def menu_cmd(message: types.Message):
    await message.answer(
        text = "Меню криптовалют",
    )

# Обработчик /help
@user_private_router.message(or_f(Command('help'), (F.text.lower() == "о боте")))
async def help_cmd(message: types.Message):
    await message.answer(
        text = 'W',
    )