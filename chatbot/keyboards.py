from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

# Основная клавиатура снизу
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Меню'), KeyboardButton(text='О боте')]
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

# Подтягивание из таблицы Tokens пар TokenID : Tiker
db_tokens = ['00:BTC', '01:ETH', '02:THE', '03:DOGE', '04:PEPE', '05:BOBKA', '06:PIPKA']
user_subscriptions = ['00', '03', '04']

class Pagination(CallbackData, prefix='pag'):
    action: str
    page: int

# Inline-клавиатура команды "Меню"
async def inline_tokens_kb(page: int=0):
    # Подтягивание подписок пользователя по TokenID
    # menu = InlineKeyboardBuilder()

    menu = InlineKeyboardBuilder()  # Создание объекта InlineKeyboardBuilder
    start_offset = page * 5  # Вычисление начального смещения на основе номера страницы
    limit = 5  # Определение лимита пользователей на одной странице
    end_offset = start_offset + limit  # Вычисление конечного смещения

    for token in db_tokens[start_offset:end_offset]:

        if token.split(":")[0] in user_subscriptions:
            menu.row(InlineKeyboardButton(text=f'{token.split(":")[-1]} ✔', callback_data=f'token_subscription:{token.split(":")[0]}:{page}'))
        else:
            menu.row(InlineKeyboardButton(text=f'{token.split(":")[-1]} ❌', callback_data=f'token_subscription:{token.split(":")[0]}:{page}'))
    buttons_row = []
    if page > 0:
        buttons_row.append(InlineKeyboardButton(text="⬅️", callback_data=Pagination(action="prev", page=page - 1).pack()))  # Добавление кнопки "назад"
    if end_offset < len(db_tokens):  # Проверка, что ещё есть пользователи для следующей страницы
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination(action="next", page=page + 1).pack()))  # Добавление кнопки "вперед"
    else:  # Если пользователи закончились
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination(action="next", page=0).pack()))  # Возвращение на первую страницу
    menu.row(*buttons_row)  # Добавление кнопок навигации
    menu.row(InlineKeyboardButton(text="❎Отписаться от всех", callback_data=f'tokens_unsubscribe:{page}'))
    return menu.as_markup()  # Возвращение клавиатуры в виде разметки

    # for tokenID in db_tokens.keys():
    #     if tokenID in user_subscriptions:
    #         menu.row(InlineKeyboardButton(text=f'{db_tokens[tokenID]} ✔', callback_data=f'token_subscription:{tokenID}'))
    #     else:
    #         menu.row(InlineKeyboardButton(text=f'{db_tokens[tokenID]} ❌', callback_data=f'token_subscription:{tokenID}'))
    #
    # # for tokenID in db_tokens.keys():
    # #     if tokenID in user_subscriptions:
    # #         menu.add(InlineKeyboardButton(text=f'{db_tokens[tokenID]} ✔', callback_data=f'token_subscription:{tokenID}'))
    # #     else:
    # #         menu.add(InlineKeyboardButton(text=f'{db_tokens[tokenID]} ❌', callback_data=f'token_subscription:{tokenID}'))
    # return menu.adjust(1).as_markup()

