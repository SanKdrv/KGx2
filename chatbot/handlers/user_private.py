from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import CallbackQuery
import logging
import chatbot.keyboards as kb


# Логи-бота
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

user_private_router = Router()

# Обработчик /start
@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        text = "Примите, пожалуйста, политику конфиденциальности:",
        reply_markup=kb.start
    )
    # Обработка принятия п.к.

@user_private_router.message(or_f(Command('menu'), (F.text.lower() == "меню")))
async def menu_cmd(message: types.Message):
    await message.answer(
        text = "Меню криптовалют",
        reply_markup = await kb.inline_tokens_kb()
    )

# Обработчик /help
@user_private_router.message(or_f(Command('help'), (F.text.lower() == "о боте")))
async def help_cmd(message: types.Message):
    await message.answer(
        text = 'Подробнее о боте',
        reply_markup=kb.help
    )

# Обработчик принятия политики конфиденциальности
@user_private_router.callback_query(F.data == 'agreement')
async def users_agreement(callback: CallbackQuery):
    await callback.message.answer(
        text='Приятного пользования!🍀',
        reply_markup=kb.main_kb
        )

    # Добавление пользователя в БД
    # user_id = callback.from_user.id

    # Добавление на экран основной клавиатуры Replykeyboard

