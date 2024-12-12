import asyncio
from datetime import datetime

import pandas as pd
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from matplotlib import pyplot as plt
from matplotlib.dates import date2num, DateFormatter

from alghorizmization import RSI_main
from main import tokens, users_tokens, bot


class MessageBroker:
    def __init__(self, redis_cli: str=None):
        self.redis_cli = None

    def run_broker(self):
        ...
    # create_redis_connection

    def stop_broker(self) -> None:
        ...

    def create_redis_connection(self):
        ...

    # Пока что фикстура
    def get_actual_data_from_redis(self, token_name: str) -> dict:
        data = {'BTCUSDT': {
            # Ключ- временная метка; Значение - сигнал RSI по этой временной метке
            "21312414231": 10.1,
            "21312414232": 22.5,
            "21312414233": 15.66,
            "21312414234": 13.23,
            "21312414235": 33.221,
            "21312414236": 38.1,
            "21312414237": 45.0,
            "21312414238": 55.55,
            "21312414239": 50.342,
            "21312414240": 63.12312,
            "21312414241": 31.1432,
            "21312414242": 23.1434,
            "21312414243": 14.35,
            "21312414244": 34.23,
            "21312414245": 87.76,
            "21312414246": 67.65,
            "21312414247": 89.12,
            "21312414248": 23.65,
            "21312414249": 43.231,
            "21312414250": 46.52,
            "21312414251": 11.23,
            "21312414252": 14.48,
            "21312414253": 42.98,
            "21312414254": 90.12,
            "21312414255": 89.34,
        }}
        return data

    # Можно отказаться, т.к логика будет в модуле чат-бота
    def get_new_subscribtions(self, token_name: str) -> [str]:
        ...

    def get_subscribtions(self, token_name: str) -> [str]:
        ...

    def send_data_to_chatbot(self, data: str) -> str:
        ...


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
                saved_png_path = draw_chart(tiker, item[4])
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
