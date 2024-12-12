import unittest
from unittest.mock import MagicMock, patch
import redis
import pandas as pd
from datetime import datetime
from alghorizmization_module import Algorithmization

class TestAlghorizmizationModule(unittest.TestCase):

    def setUp(self):
        self.module = AlghorizmizationModule()
        self.module.redis_client = MagicMock()  # Мокаем Redis клиент
# Проверяет, что Redis-клиент инициализируется с правильными параметрами.
    def test_create_redis_connection(self):
        with patch('your_module.redis.Redis') as mock_redis:
            self.module.create_redis_connection()
            mock_redis.assert_called_with(
                host='localhost',  # Замените на реальные значения из REDIS_CONFIG
                port=6379,
                db=0,
                password=None
            )
# Тестирует корректность сохранения и извлечения данных о монете.
    def test_save_and_get_last_coin_data_to_redis(self):
        ticker = 'BTCUSDT'
        data = {
            'timestamp': 1672531200,
            'close_price': 50000.0,
            'prices': [[1672531200, 50000.0], [1672531260, 50050.0]],
            'rsi': 60.5
        }
        key = f"last_coin_data___{ticker}"

        # Тестируем сохранение
        self.module.save_last_coin_data_to_redis(ticker, **data)
        self.module.redis_client.set.assert_called_with(key, str(data))

        # Тестируем получение
        self.module.redis_client.get.return_value = str(data).encode('utf-8')
        result = self.module.get_last_coin_data_from_redis(ticker)
        self.assertEqual(result, data)
# Проверяет, что функция правильно извлекает последние 14 записей из Redis.
    def test_fetch_last_14_data_from_redis(self):
        mock_keys = [b"KGx2___BTCUSDT.1672531200", b"KGx2___BTCUSDT.1672531260"]
        self.module.redis_client.scan = MagicMock(return_value=(0, mock_keys))
        self.module.redis_client.get = MagicMock(side_effect=[b'50000.0', b'50050.0'])

        result = self.module.fetch_last_14_data_from_redis()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]['close_price'], 50000.0)
# Убедиться, что расчет RSI работает корректно.
    def test_calculate_rsi(self):
        prices = [50, 51, 52, 53, 54, 55, 56, 55, 54, 53, 52, 51, 50, 49]
        expected_rsi = 42.86  # Примерное значение

        result = self.module.calculate_rsi(prices)
        self.assertAlmostEqual(result, expected_rsi, places=2)
# Имитирует полный процесс обработки данных, включая вызовы вспомогательных функций.
    def test_process_data(self):
        mock_data = pd.DataFrame({
            'ticker': ['BTCUSDT'] * 14,
            'timestamp': list(range(1672531200, 1672531200 + 14 * 60, 60)),
            'close_price': [50, 51, 52, 53, 54, 55, 56, 55, 54, 53, 52, 51, 50, 49]
        })

        with patch.object(self.module, 'fetch_last_14_data_from_redis', return_value=mock_data), \
             patch.object(self.module, 'save_last_coin_data_to_redis') as mock_save:

            results = self.module.process_data()

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0][0], 'BTCUSDT')
            self.assertEqual(results[0][3], 42.86)  # Примерное значение RSI
            mock_save.assert_called()

if __name__ == '__main__':
    unittest.main()
