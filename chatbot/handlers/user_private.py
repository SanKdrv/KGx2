from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, or_f, Filter
from aiogram.types import CallbackQuery, Message
import logging
import chatbot.keyboards as kb
from chatbot.keyboards import user_subscriptions, db_tokens

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
    # Проверка пользователя на принятие политики конф.
    userId = message.from_user.id
    # /
    await message.answer(
        text = "Меню криптовалют",
        reply_markup = await kb.inline_tokens_kb(userId)
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

@user_private_router.callback_query(F.data.startswith('token_subscription:'))
async def token_subscription(callback: CallbackQuery):
    userId = callback.from_user.id
    tokenID = callback.data.split(':')[-1]
    print(tokenID)

    if tokenID in user_subscriptions:
        user_subscriptions.remove(tokenID)
    else:
        user_subscriptions.append(tokenID)
        user_subscriptions.sort()

    await callback.message.edit_reply_markup(reply_markup=await kb.inline_tokens_kb(userId))