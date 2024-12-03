from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery
from config import *
from main import tokens as db_tokens
from main import users_tokens, users


# Основная клавиатура снизу
# async def reply_main_kb_init(user_id):
#     reply_menu = ReplyKeyboardMarkup(
#         keyboard = [[KeyboardButton(text='Меню')]],
#         resize_keyboard=True,
#         one_time_keyboard=False,
#         input_field_placeholder='Выберите любой пункт меню...'
#     )
#
#     return reply_menu


async def inline_main_kb(user_id):
    menu = InlineKeyboardBuilder()
    menu.row(InlineKeyboardButton(text='Криптовалюты 🏦', callback_data='crypto_menu'))
    menu.row(InlineKeyboardButton(text='Мои подписки ❤', callback_data='checktokens'))
    menu.row(InlineKeyboardButton(text='О боте 👾', callback_data='help'))
    if user_id in admins_id:
        menu.row(InlineKeyboardButton(text='Админ панель 🛑', callback_data='admin_message'))

    return menu.as_markup()


# Inline-клавиатура "регистрации"
start = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Политика конфиденциальности', url='https://yandex.ru/search/?clid=2456108&text=Политика+конфиденциальности&l10n=ru&lr=18')],
        [InlineKeyboardButton(text='Согласиться', callback_data='agreement')]
    ]
)

# admin_kb = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [InlineKeyboardButton(text='Рассылка 📧', callback_data='admin_message')]
#     ]
# )

# Inline-клавиатура команды "О боте"
async def help_kb_init(userID):
    buttons = [
        [InlineKeyboardButton(text='Wiki-страница 🧾', url='https://se.cs.petrsu.ru/wiki/KGx2')],
        [InlineKeyboardButton(text='GitHub ⬛', url='https://github.com/SanKdrv/KGx2')]
    ]

    if users.check_user_existence(userID) == False:
        buttons.append([InlineKeyboardButton(text='Меню ⬅', callback_data='back_to_menu')])

    help = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
    # help = InlineKeyboardMarkup(
    #     inline_keyboard=[
    #         [InlineKeyboardButton(text='Wiki-страница 🧾', url='https://se.cs.petrsu.ru/wiki/KGx2')],
    #         [InlineKeyboardButton(text='GitHub ⬛', url='https://github.com/SanKdrv/KGx2')],
    #         [InlineKeyboardButton(text='Меню ⬅', callback_data='back_to_menu')]
    #     ]
    # )
    return help


async def checktokens_message(userID):
    text = 'Вы подписаны на: '
    tokens_list = []

    user_tokens = users_tokens.get_tokens_by_user(userID)

    db_tokens_list = db_tokens.get_tikers()

    for token in db_tokens_list:
        tokenID = int(db_tokens.get_token_ID(token))
        if tokenID in user_tokens:

            tokens_list.append(token)

    # Создаем строку с токенами, соединяя их через запятую
    formatted_tokens = ', '.join(tokens_list)

    if len(user_tokens) > 0:
        # Добавляем отформатированные токены к началу сообщения
        full_text = f"{text}{formatted_tokens}"
    else:
        full_text = "Ваш список подписок пустой."

    return full_text


class Pagination(CallbackData, prefix='pag'):
    action: str
    page: int

# Inline-клавиатура команды "Меню"
async def inline_tokens_kb(userID, page: int=0):
    # Подтягивание подписок пользователя по TokenID
    menu = InlineKeyboardBuilder()  # Создание объекта InlineKeyboardBuilder
    start_offset = page * 5  # Вычисление начального смещения на основе номера страницы
    limit = 5  # Определение лимита пользователей на одной странице
    end_offset = start_offset + limit  # Вычисление конечного смещения

    user_tokens = users_tokens.get_tokens_by_user(userID)

    for token in db_tokens.get_tikers()[start_offset:end_offset]:
        tokenID = int(db_tokens.get_token_ID(token))
        if tokenID in user_tokens:
            menu.row(InlineKeyboardButton(text=f'{token} ✔', callback_data=f'token_subscription:{tokenID}:{page}'))
        else:
            menu.row(InlineKeyboardButton(text=f'{token.split(":")[-1]} ❌', callback_data=f'token_subscription:{tokenID}:{page}'))
    buttons_row = []
    if page > 0:
        buttons_row.append(InlineKeyboardButton(text="⬅️", callback_data=Pagination(action="prev", page=page - 1).pack()))  # Добавление кнопки "назад"
    if end_offset < len(db_tokens.get_tikers()):  # Проверка, что ещё есть пользователи для следующей страницы
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination(action="next", page=page + 1).pack()))  # Добавление кнопки "вперед"
    else:  # Если пользователи закончились
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination(action="next", page=0).pack()))  # Возвращение на первую страницу
    menu.row(*buttons_row)  # Добавление кнопок навигации
    menu.row(InlineKeyboardButton(text="Отписаться от всех", callback_data=f'tokens_unsubscribe:{page}'))
    return menu.as_markup()  # Возвращение клавиатуры в виде разметки 💩

def cancel_btn():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Или нажмите на 'ОТМЕНА' для отмены",
    )
