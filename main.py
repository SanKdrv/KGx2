import threading
import time
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from matplotlib import pyplot as plt
from matplotlib.dates import date2num, DateFormatter
from pandas.core._numba import executor
import pandas as pd
from datetime import datetime
import chatbot.chatbot_module
from message_broker import message_broker_module
import asyncio
from aiogram import Bot, Dispatcher
import config
import os
from parse import parse_module
from models.models import *
from config import *
from alghorizmization import RSI_main
from queue import Queue


# Инициализация ORM моделей
users = Users('Users')
tokens = Tokens('Tokens')
users_tokens = UsersTokens('UsersTokens')

# # Инициализация модулей
# broker = message_broker_module.MessageBroker()
parser = parse_module.Parse(tokens_table=tokens)
alg = RSI_main.AlghorizmizationModule()

q = Queue()

# # Создание потоков
thread1 = threading.Thread(target=parser.parse_bybit)
# thread2 = threading.Thread(target=alg.run)
# thread3 = threading.Thread(target=task_module_3)
# # thread4 = threading.Thread(target=task_module_4)
# thread5 = threading.Thread(target=broker.run_broker)
#
# thread5.start()

thread1.start()
# thread2.start()
# print(thread2.)
# thread2.join()
# thread2.result()

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


# async def botStart():
#     from chatbot.handlers.user_private import user_private_router
#     # Подключение роутера
#     dp.include_routers(user_private_router)
#     await bot.delete_webhook(drop_pending_updates=True)
#     task = asyncio.create_task(coro=scheduler(delay=15))
#     # await scheduler(delay=15)
#     await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), skip_updates = True,)


# async def scheduler(delay):
#     while True:
#         # print('jopa')
#         # await chatbot.chatbot_module.pull_gueue()
#         alg = RSI_main.AlghorizmizationModule()
#         data = alg.process_data()
#         tasks = []
#         for item in data:
#             tiker = item[0][:-4]
#             print(tiker)
#             token_UID = tokens.get_token_ID(item[0])
#             s = f'https://www.bybit.com/ru-RU/trade/spot/{tiker}/USDT'
#             users_id_list = users_tokens.get_users_by_token(int(token_UID))
#             tasks += [bot.send_message(chat_id=user,
#                                        text=f'Заносик, покупай здесь: https://www.bybit.com/ru-RU/trade/spot/{tiker}/USDT')
#                       for user in users_id_list]
#         # all_tasks = asyncio.all_tasks()
#         # print(all_tasks)
#         await asyncio.gather(*tasks)
#         await asyncio.sleep(delay=delay)
#         # time.sleep(10)
async def botStart():
    from chatbot.handlers.user_private import user_private_router

    # Подключение роутеров
    dp.include_routers(user_private_router)
    await bot.delete_webhook(drop_pending_updates=True)

    # Параллельный запуск бота и scheduler
    await asyncio.gather(
        dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), skip_updates=True),
        scheduler(delay=15)
    )


async def scheduler(delay):
    while True:
        try:
            alg = RSI_main.AlghorizmizationModule()
            data = alg.process_data()
            tasks = []
            print(data)
            for item in data:
                tiker = item[0][:-4]
                print(tiker)
                token_UID = tokens.get_token_ID(item[0])
                saved_png_path = draw_chart(tiker)
                s = f'https://www.bybit.com/ru-RU/trade/spot/{tiker}/USDT'
                users_id_list = users_tokens.get_users_by_token(int(token_UID))

                caption_addon = str()
                if float(item[3]) >= 75:
                    caption_addon = 'Советуем продать.'
                elif float(item[3]) <= 25:
                    caption_addon = 'Рекомендуем докупить.'

                tasks += [bot.send_photo(
                    chat_id=user,
                    photo=FSInputFile(saved_png_path),
                    caption=f'Алгоритм для <b>{tiker}</b> отработан. \n {caption_addon} \nСсылка на покупку: {s}',
                    parse_mode=ParseMode.HTML
                ) for user in users_id_list]
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Ошибка в scheduler: {e}")
            continue
        await asyncio.sleep(delay)


def draw_chart(ticker_name: str, chart_data: list = None) -> str:
    if chart_data is None:
        chart_data = [['2024-12-11 12:52:03', 0.9505], ['2024-12-11 12:53:00', 0.9498],
                      ['2024-12-11 12:53:04', 0.9502], ['2024-12-11 12:54:00', 0.9508],
                      ['2024-12-11 12:54:05', 0.9509], ['2024-12-11 12:55:00', 0.9524],
                      ['2024-12-11 12:55:07', 0.9524], ['2024-12-11 12:56:02', 0.9529],
                      ['2024-12-11 12:56:15', 0.9522], ['2024-12-11 12:56:18', 0.9524],
                      ['2024-12-11 12:57:16', 0.9521], ['2024-12-11 12:57:18', 0.9518],
                      ['2024-12-11 12:58:20', 0.9523], ['2024-12-11 12:59:22', 0.9525]]

    saved_name = f'buffer/{ticker_name}_chart.png'
    prepared_data = prepare_data(chart_data)

    dates = pd.to_datetime([item[0] for item in prepared_data])
    prices = [float(item[1]) for item in prepared_data]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Convert dates to matplotlib's date number format
    date_numbers = date2num(dates)

    # Plot the data
    ax.plot(date_numbers, prices, 'b-', linewidth=2)

    # Format the x-axis dates
    date_format = DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate(rotation=45, ha='right')

    # Add axis labels and title
    ax.set_xlabel('Время')
    ax.set_ylabel('Цена закрытия')
    ax.set_title(f'График цен {ticker_name}')

    # Add legend
    ax.legend(['Цена'])

    # Save the figure instead of displaying it
    plt.savefig(saved_name, dpi=300, bbox_inches='tight')
    plt.close(fig)

    return saved_name

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')


def prepare_data(chart_data):
    formatted_data = [(parse_date(item[0]), item[1]) for item in chart_data]
    formatted_data.sort(key=lambda x: x[0])
    return formatted_data


# Запуск бота
if __name__ == '__main__':
    asyncio.run(botStart())

