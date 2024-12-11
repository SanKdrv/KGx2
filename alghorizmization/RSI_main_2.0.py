import redis
import pandas as pd
from datetime import datetime
from config import *
import time

class AlghorizmizationModule:
    def __init__(self):  # 900 секунд = 15 минут
        super().__init__()
        self.redis_client = self.create_redis_connection()
        self.interval_seconds = 40

    def create_redis_connection(self) -> redis.Redis:
        """Создание клиента Redis"""
        return redis.Redis(host=REDIS_CONFIG['HOST'],
                            port=REDIS_CONFIG['PORT'],
                            db=REDIS_CONFIG['DATABASE'],
                            password=REDIS_CONFIG['PASSWORD'])

    def save_last_coin_data_to_redis(self, ticker: str, timestamp: int, close_price: float, prices: list, rsi: float):
        """Сохранение всех данных о монете в Redis."""
        key = f"last_coin_data___{ticker}"
        data = {
            'timestamp': timestamp,
            'close_price': close_price,
            'prices': prices,  # Массив цен закрытия с временными метками
            'rsi': rsi  # Значение RSI для данной монеты
        }
        # Сохраняем данные как JSON строку в Redis
        self.redis_client.set(key, str(data))

    def get_last_coin_data_from_redis(self, ticker: str):
        """Получение последних данных о монете из Redis."""
        key = f"last_coin_data___{ticker}"
        data = self.redis_client.get(key)
        if data:
            # Декодируем данные и возвращаем
            return eval(data.decode('utf-8'))
        else:
            return None

    def fetch_last_14_data_from_redis(self):
        """
        Получение последних 14 данных для каждого тикера из Redis.
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
        ticker_data = {}
        for key in keys:
            try:
                _, ticker_timestamp = key.split("___")
                ticker, timestamp = ticker_timestamp.split(".")
                timestamp = int(timestamp)  # Преобразуем метку времени

                # Получаем значение (цена закрытия)
                value = client.get(key).decode('utf-8')
                close_price = float(value.strip('}'))

                # Добавляем данные в список по тикеру
                if ticker not in ticker_data:
                    ticker_data[ticker] = []
                ticker_data[ticker].append((timestamp, close_price))
            except ValueError as e:
                print(f"Ошибка обработки ключа {key}: {e}")
                continue

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

        results = []
        for ticker in data['ticker'].unique():
            ticker_data = data[data['ticker'] == ticker].sort_values('timestamp')
            prices = ticker_data['close_price'].tolist()

            # Если недостаточно данных для расчета RSI, пропускаем
            if len(prices) < 14:
                continue

            rsi = self.calculate_rsi(prices)
            latest_entry = ticker_data.iloc[-1]
            timestamp = latest_entry['timestamp']
            price = float(latest_entry['close_price'])

            # 14 Цен закрытий графика (массив цен и меток времени)
            points_14 = []
            for row in ticker_data.iterrows():
                timestamp_1 = row[1]['timestamp']
                price_1 = float(row[1]['close_price'])
                points_14.append([timestamp_1, price_1])

            # Сохраняем все данные о монете в Redis
            self.save_last_coin_data_to_redis(ticker, timestamp, price, points_14, rsi)

            if (round(rsi, 2) < 25 or round(rsi, 2) > 75):
                results.append([ticker, timestamp, price, round(rsi, 2), points_14])

        # Вывод результатов
        for result in results:
            print(result)

        return results
