from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


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
db_tokens = {'00': 'BTC', '01': 'ETH', '02': 'THE', '03': 'DOGE', '04': 'PEPE'}
user_subscriptions = ['00', '03', '04']

class Pagination(CallbackData, prefix='pag'):
    action: str
    page: int

# Inline-клавиатура команды "Меню"
async def inline_tokens_kb(page=0):
    # Подтягивание подписок пользователя по TokenID
    menu = InlineKeyboardBuilder()

    for tokenID in db_tokens.keys():
        if tokenID in user_subscriptions:
            menu.row(InlineKeyboardButton(text=f'{db_tokens[tokenID]} ✔', callback_data=f'token_subscription:{tokenID}'))
        else:
            menu.row(InlineKeyboardButton(text=f'{db_tokens[tokenID]} ❌', callback_data=f'token_subscription:{tokenID}'))

    # for tokenID in db_tokens.keys():
    #     if tokenID in user_subscriptions:
    #         menu.add(InlineKeyboardButton(text=f'{db_tokens[tokenID]} ✔', callback_data=f'token_subscription:{tokenID}'))
    #     else:
    #         menu.add(InlineKeyboardButton(text=f'{db_tokens[tokenID]} ❌', callback_data=f'token_subscription:{tokenID}'))
    return menu.adjust(1).as_markup()

