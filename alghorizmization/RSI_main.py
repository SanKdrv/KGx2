import redis
import pandas as pd
from datetime import datetime
from config import *

# # Конфигурация для подключения к Redis
# REDIS_CONFIG = {
#     'HOST': '192.168.112.103',
#     'PORT': 6379,
#     'DATABASE': 0,
#     'PASSWORD': 'student'
# }


def create_redis_connection():
    """
    Создание клиента Redis.
    """
    try:
        client = redis.Redis(
            host=REDIS_CONFIG['HOST'],
            port=REDIS_CONFIG['PORT'],
            db=REDIS_CONFIG['DATABASE'],
            password=REDIS_CONFIG['PASSWORD'],
            # decode_responses=True
        )
        client.ping()
        print("Успешно подключено к Redis")
        return client
    except redis.ConnectionError as e:
        print(f"Ошибка подключения к Redis: {e}")
        exit(1)


def fetch_last_14_data_from_redis(client):
    """
    Получение последних 14 данных для каждого тикера из Redis.

    :param client: объект подключения Redis
    :return: DataFrame с колонками: ['ticker', 'timestamp', 'close_price']
    """
    data = []
    keys = []
    cursor = 0
    while True:
        cursor, partial_keys = client.scan(cursor=cursor, match="KGx2___*", count=1000)
        keys.extend(partial_keys)
        if cursor == 0:
            break

    keys = [key.decode('utf-8') for key in keys]
    # print(keys)

    # print(keys)
    # Группируем ключи по тикеру
    ticker_data = {}
    for key in keys:
        try:
            _, ticker_timestamp = key.split("___")
            ticker, timestamp = ticker_timestamp.split(".")
            timestamp = int(timestamp)  # Преобразуем метку времени

            # Получаем значение (цена закрытия)
            value = client.get(key).decode('utf-8')
            # print(value)
            close_price = float(value.strip('}'))

            # Добавляем данные в список по тикеру
            if ticker not in ticker_data:
                ticker_data[ticker] = []
            ticker_data[ticker].append((timestamp, close_price))
        except ValueError as e:
            print(f"Ошибка обработки ключа {key}: {e}")
            continue

    # Оставляем только последние 14 записей для каждого тикера
    for ticker, values in ticker_data.items():
        sorted_values = sorted(values, key=lambda x: x[0], reverse=True)[:14]
        for timestamp, close_price in sorted_values:
            data.append({
                'ticker': ticker,
                'timestamp': timestamp,
                'close_price': close_price
            })

    return pd.DataFrame(data)


def calculate_rsi(data, period=14):
    """
    Рассчитать RSI по данным цен закрытия.

    :param data: Список цен закрытия.
    :param period: Период RSI.
    :return: Значение RSI.
    """
    df = pd.DataFrame(data, columns=['close'])
    df['change'] = df['close'].diff()
    df['gain'] = df['change'].apply(lambda x: x if x > 0 else 0)
    df['loss'] = df['change'].apply(lambda x: -x if x < 0 else 0)
    df['avg_gain'] = df['gain'].rolling(window=period).mean()
    df['avg_loss'] = df['loss'].rolling(window=period).mean()
    df['rs'] = df['avg_gain'] / df['avg_loss']
    df['rsi'] = 100 - (100 / (1 + df['rs']))

    return float(df['rsi'].iloc[-1])  # Приведение к float


def process_data():
    """
    Основная логика обработки данных.
    """
    client = create_redis_connection()
    data = fetch_last_14_data_from_redis(client)

    if data.empty:
        print("Нет данных в Redis.")
        return

    results = []
    for ticker in data['ticker'].unique():
        ticker_data = data[data['ticker'] == ticker].sort_values('timestamp')
        prices = ticker_data['close_price'].tolist()

        # Если недостаточно данных для расчета RSI, пропускаем
        if len(prices) < 14:
            continue

        rsi = calculate_rsi(prices)
        latest_entry = ticker_data.iloc[-1]
        timestamp = datetime.fromtimestamp(
            latest_entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        price = float(latest_entry['close_price'])
        results.append([ticker, timestamp, price, round(rsi, 2)])

    # Вывод результатов
    for result in results:
        print(result)


# Запуск программы
if __name__ == "__main__":
    process_data()
