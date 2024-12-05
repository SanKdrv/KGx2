import redis
import pandas as pd
from datetime import datetime
from config import *
import time

# # Конфигурация для подключения к Redis
# REDIS_CONFIG = {
#     'HOST': '192.168.112.103',
#     'PORT': 6379,
#     'DATABASE': 0,
#     'PASSWORD': 'student'
# }


class AlghorizmizationModule:
    def __init__(self):  # 900 секунд = 15 минут
        super().__init__()
        self.redis_client = self.create_redis_connection()
        self.interval_seconds = 40

    def create_redis_connection(self) -> redis.Redis:
        """ Создание клиента Redis
            метод возвращает redis-клиент, записывает результат
            в поле redis_cli """
        return redis.Redis(host=REDIS_CONFIG['HOST'],
                            port=REDIS_CONFIG['PORT'],
                            db=REDIS_CONFIG['DATABASE'],
                            password=REDIS_CONFIG['PASSWORD'])


    def fetch_last_14_data_from_redis(self):
        """
        Получение последних 14 данных для каждого тикера из Redis.

        :param client: объект подключения Redis
        :return: DataFrame с колонками: ['ticker', 'timestamp', 'close_price']
        """
        client = self.redis_client
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


    def calculate_rsi(self, data, period=14):
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


    def process_data(self):
        """
        Основная логика обработки данных.
        """
        client = self.redis_client
        data = self.fetch_last_14_data_from_redis()

        if data.empty:
            print("Нет данных в Redis.")
            return

        # print(data)
        results = []
        for ticker in data['ticker'].unique():
            ticker_data = data[data['ticker'] == ticker].sort_values('timestamp')
            prices = ticker_data['close_price'].tolist()

            # Если недостаточно данных для расчета RSI, пропускаем
            if len(prices) < 14:
                continue

            rsi = self.calculate_rsi(prices)
            latest_entry = ticker_data.iloc[-1]
            timestamp = datetime.fromtimestamp(latest_entry['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            price = float(latest_entry['close_price'])

            # 14 Цен закрытий графика
            points_14 = []
            for row in ticker_data.iterrows():
                timestamp_1 = datetime.fromtimestamp(row[1]['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                price_1 = float(row[1]['close_price'])
                points_14.append([timestamp_1, price_1])

            # if (round(rsi, 2) < 25 or round(rsi, 2) > 80):
            #     results.append([ticker, timestamp, price, round(rsi, 2), points_14])
            results.append([ticker, timestamp, price, round(rsi, 2), points_14])

        # Вывод результатов
        for result in results:
            print(result)

        return results
