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

# Inline-клавиатура команды "Меню"
async def inline_tokens_kb():
    menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='👷‍♂️В разработке', callback_data='token_subscription')],
        ]
    )
    return menu
    # db_tokens = ...
    # #db_subscribe???
    # menu = InlineKeyboardBuilder()
    # for token in db_tokens:
    #     menu.add(InlineKeyboardButton(text=token))
    #     return menu.as_markup()