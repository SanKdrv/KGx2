from aiogram import Router, types, F
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart, Command, or_f, Filter, and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
import logging
import chatbot.keyboards as kb
from chatbot.keyboards import inline_tokens_kb, checktokens_message, cancel_btn
from chatbot.keyboards import Pagination
from main import users, users_tokens, bot
from main import tokens as db_tokens
from config import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import asyncio


class Form(StatesGroup):
    start_broadcast = State()

async def broadcast_message(users_data: list, text: str = None, photo_id: int = None, document_id: int = None,
                            video_id: int = None, audio_id: int = None, caption: str = None, content_type: str = None):
    good_send = 0
    bad_send = 0
    for user in users_data:
        try:
            chat_id = user
            if content_type == ContentType.TEXT:
                await bot.send_message(chat_id=chat_id, text=text)
            elif content_type == ContentType.PHOTO:
                await bot.send_photo(chat_id=chat_id, photo=photo_id, caption=caption)
            elif content_type == ContentType.DOCUMENT:
                await bot.send_document(chat_id=chat_id, document=document_id, caption=caption)
            elif content_type == ContentType.VIDEO:
                await bot.send_video(chat_id=chat_id, video=video_id, caption=caption)
            elif content_type == ContentType.AUDIO:
                await bot.send_audio(chat_id=chat_id, audio=audio_id, caption=caption)
            good_send += 1
        except Exception as e:
            print(e, 'ba')
            bad_send += 1
        finally:
            await asyncio.sleep(1)
    return good_send, bad_send


# TODO: Добавить лимиты запросов

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
        if userId in admins_id:
            await message.answer(
                text = "Вы уже принимали политику конфиденциальности",
                reply_markup = kb.admin_main_kb
            )
        else:
            await message.answer(
                text = "Вы уже принимали политику конфиденциальности",
                reply_markup = kb.main_kb
            )

@user_private_router.callback_query(or_f(F.data.startswith('menu'), (F.text.lower() == "криптовалюты")))
async def menu_cmd(callback: CallbackQuery):
    userId = callback.from_user.id
    if users.check_user_existence(user_UID=userId) == False:
        await callback.message.answer(
            text = "<b>Меню криптовалют</b>",
            reply_markup = await kb.inline_tokens_kb(userID=userId),
            parse_mode=ParseMode.HTML
        )
        # -1 Запрос в limit
        # users.dec_user_limit(userId)
    else:
        await callback.message.answer(
            text= "Сперва примите политику конфиденциальности",
            reply_markup=kb.start
        )

# Обработчик /help
@user_private_router.callback_query(or_f(F.data.startswith('help'), (F.text.lower() == "о боте")))
async def help_cmd(callback: CallbackQuery):
    await callback.message.answer(
        text = 'Подробнее о боте',
        reply_markup=kb.help
    )

# Обработчик /checktokens
@user_private_router.callback_query(or_f(F.data.startswith('checktokens'), (F.text.lower() == 'подписки')))
async def checktokens_cmd(callback: CallbackQuery):
    userId = callback.from_user.id
    if users.check_user_existence(user_UID=userId) == False:
        await callback.message.answer(
            text=await checktokens_message(userID=userId)
        )
    else:
        await callback.message.answer(
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

    # print(tokenID, user_tokens)

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

# Обработчик сообщения от админа всем пользователям
@user_private_router.callback_query(F.data.startswith('admin'))
async def custom_message(callback: CallbackQuery, state: FSMContext):
    userID = callback.from_user.id

    if userID in admins_id:
        await callback.message.answer('Введите ваше сообщение для пользователей бота👾',
                                      reply_markup=cancel_btn())
        await state.set_state(Form.start_broadcast)
    else:
        await callback.message.answer(
            text='У вас недостаточно прав😯',
            reply_markup=kb.main_kb
        )

# TODO: Добавить alert при отписке

@user_private_router.callback_query(F.data.startswith('tokens_unsubscribe'))
async def token_unsubscribe(callback: CallbackQuery):
    userID = callback.from_user.id
    user_tokens = users_tokens.get_tokens_by_user(userID)
    current_page = int(callback.data.split(":")[-1])

    for tokenID in user_tokens:
        users_tokens.remove_token_for_user(user_UID=userID, token_ID=tokenID)

    await callback.message.edit_reply_markup(reply_markup=await kb.inline_tokens_kb(userID=userID, page=current_page))

# Сообщение от админа
@user_private_router.message(F.content_type.in_({'text', 'photo', 'document', 'video', 'audio'}), Form.start_broadcast)
async def universe_broadcast(message: Message, state: FSMContext):
    users_id_list = users.select_all()
    users_id = [user['UID'] for user in users_id_list]

    # Определяем параметры для рассылки в зависимости от типа сообщения
    content_type = message.content_type

    if content_type == ContentType.TEXT and message.text == '❌ Отмена':
        await state.clear()
        await message.answer('Рассылка отменена!', reply_markup=kb.admin_main_kb())
        return

    await message.answer(f'Начинаю рассылку на {len(users_id)} пользователей.')

    good_send, bad_send = await broadcast_message(
        users_data=users_id,
        text=message.text if content_type == ContentType.TEXT else None,
        photo_id=message.photo[-1].file_id if content_type == ContentType.PHOTO else None,
        document_id=message.document.file_id if content_type == ContentType.DOCUMENT else None,
        video_id=message.video.file_id if content_type == ContentType.VIDEO else None,
        audio_id=message.audio.file_id if content_type == ContentType.AUDIO else None,
        caption=message.caption,
        content_type=content_type
    )

    await state.clear()
    await message.answer(f'Рассылка завершена. Сообщение получило <b>{good_send}</b>, '
                         f'НЕ получило <b>{bad_send}</b> пользователей.', reply_markup=kb.admin_main_kb, parse_mode=ParseMode.HTML)

# Обработчик остальных сообщений
@user_private_router.message()
async def answer(message: types.Message):
    userID = message.from_user.id
    if userID in admins_id:
        await message.answer(
            text='<strong>Меню бота</strong> 🤖',
            reply_markup=kb.admin_main_kb,
            parse_mode=ParseMode.HTML
        )
    else:
        await message.answer(
            text='<strong>Меню бота</strong> 🤖',
            reply_markup=kb.main_kb,
            parse_mode = ParseMode.HTML
        )