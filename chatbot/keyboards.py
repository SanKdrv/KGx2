from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from main import tokens as db_tokens, users
from main import users_tokens


# Основная клавиатура снизу
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Меню'), KeyboardButton(text='Подписки'), KeyboardButton(text='О боте')]
    ],
    resize_keyboard=True,
)

# Inline-клавиатура "регистрации"
start = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Политика конфиденциальности', url='https://yandex.ru/search/?clid=2456108&text=Политика+конфиденциальности&l10n=ru&lr=18')],
        [InlineKeyboardButton(text='Согласиться', callback_data='agreement')]
    ]
)

# Inline-клавиатура команды "О боте"
help = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='🧾Wiki-страница', url='https://se.cs.petrsu.ru/wiki/KGx2')],
        [InlineKeyboardButton(text='⬛GitHub', url='https://github.com/SanKdrv/KGx2')],
    ]
)

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
    if len(formatted_tokens) > len(text):
        # Добавляем отформатированные токены к началу сообщения
        full_text = f"{text}{formatted_tokens}"
    else:
        full_text = f"{text}Ничего"

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
