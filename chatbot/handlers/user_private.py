from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, or_f, Filter
from aiogram.types import CallbackQuery, Message
import logging
import chatbot.keyboards as kb
from chatbot.keyboards import inline_tokens_kb, checktokens_message
from chatbot.keyboards import Pagination
from main import users, users_tokens
from main import tokens as db_tokens


# Логи-бота
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

user_private_router = Router()


# Обработчик /start
@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    #Если пользователя нет в БД
    userId = message.from_user.id # ID пользователя
    if users.check_user_existence(user_UID=userId) == True:
        await message.answer(
            text = "Примите, пожалуйста, политику конфиденциальности:",
            reply_markup=kb.start
        )
    else:
        await message.answer(
            text = "Вы уже принимали политику конфиденциальности",
            reply_markup = kb.main_kb
        )


@user_private_router.message(or_f(Command('menu'), (F.text.lower() == "меню")))
async def menu_cmd(message: types.Message):
    userId = message.from_user.id
    if users.check_user_existence(user_UID=userId) == False:
        await message.answer(
            text = "Меню криптовалют",
            reply_markup = await kb.inline_tokens_kb(userID=userId)
        )
        # -1 Запрос в limit
        # users.dec_user_limit(userId)
    else:
        await message.answer(
            text= "Сперва примите политику конфиденциальности",
            reply_markup=kb.start
        )


# Обработчик /help
@user_private_router.message(or_f(Command('help'), (F.text.lower() == "о боте")))
async def help_cmd(message: types.Message):
    await message.answer(
        text = 'Подробнее о боте',
        reply_markup=kb.help
    )


# Обработчик /checktokens
@user_private_router.message(or_f(Command('checktokens'), (F.text.lower() == 'подписки')))
async def checktokens_cmd(message: types.Message):
    userId = message.from_user.id
    if users.check_user_existence(user_UID=userId) == False:
        await message.answer(
            text=await checktokens_message(userID=userId)
        )
    else:
        await message.answer(
            text= "Сперва примите политику конфиденциальности",
            reply_markup=kb.start
        )


# Обработчик принятия политики конфиденциальности
@user_private_router.callback_query(F.data == 'agreement')
async def users_agreement(callback: CallbackQuery):
    userId = callback.from_user.id
    await callback.message.answer(
        text='Приятного пользования!🍀',
        reply_markup=kb.main_kb
        )
    users.add_user(user_UID=userId)


@user_private_router.callback_query(F.data.startswith('token_subscription:'))
async def token_subscription(callback: CallbackQuery):
    userID = callback.from_user.id
    tokenID = int(callback.data.split(':')[-2])

    user_tokens = users_tokens.get_tokens_by_user(userID)

    print(tokenID, user_tokens)

    current_page = int(callback.data.split(':')[-1])
    if tokenID in user_tokens:
        users_tokens.remove_token_for_user(user_UID=userID, token_ID=tokenID)
    else:
        users_tokens.add_token_for_user(user_UID=userID, token_ID=tokenID)

    await callback.message.edit_reply_markup(reply_markup=await kb.inline_tokens_kb(userID=userID,page=current_page))


# Обработчик нажатия кнопок навигации
@user_private_router.callback_query(Pagination.filter())
async def pagination_handler(call: CallbackQuery, callback_data: Pagination):
    page = callback_data.page  # Получение номера страницы из callback data
    userID = call.from_user.id
    await call.message.edit_reply_markup(reply_markup=await inline_tokens_kb(userID=userID ,page=page))  # Обновление клавиатуры при нажатии кнопок "вперед" или "назад"


@user_private_router.callback_query(F.data.startswith('tokens_unsubscribe'))
async def token_unsubscribe(callback: CallbackQuery):
    userID = callback.from_user.id
    user_tokens = users_tokens.get_tokens_by_user(userID)
    current_page = int(callback.data.split(":")[-1])

    for tokenID in user_tokens:
        users_tokens.remove_token_for_user(user_UID=userID, token_ID=tokenID)

    await callback.message.edit_reply_markup(reply_markup=await kb.inline_tokens_kb(userID=userID, page=current_page))

# Обработчик остальных сообщений

