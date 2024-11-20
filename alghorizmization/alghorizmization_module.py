import redis
import requests
from typing import List

class Algorithmization:
    def init(self, tokens: List[str], telegram_api_key: str, chat_id: str, redis_cli: redis.Redis, rsi_period: int = 14, overbought_level: int = 70, oversold_level: int = 30):
        """
        Инициализация класса с основными параметрами.
        :param tokens: Список тикеров криптовалют.
        :param telegram_api_key: API-ключ для подключения к Telegram-боту.
        :param chat_id: ID чата пользователя для отправки уведомлений.
        :param redis_cli: Redis клиент для взаимодействия с данными.
        :param rsi_period: Период для расчета RSI.
        :param overbought_level: Уровень RSI для перекупленности.
        :param oversold_level: Уровень RSI для перепроданности.
        """
        self.redis_cli = redis_cli  # Redis клиент для хранения данных.
        self.telegram_api_key = telegram_api_key  # API-ключ Telegram.
        self.chat_id = chat_id  # ID чата для уведомлений.
        self.tokens = tokens  # Список отслеживаемых токенов.
        self.rsi_period = rsi_period  # Период для расчета RSI.
        self.overbought_level = overbought_level  # RSI уровень перекупленности.
        self.oversold_level = oversold_level  # RSI уровень перепроданности.
        self.signals_log = []  # Журнал сигналов.

    def fetch_price_data(self, token: str, period: int) -> List[float]:
        """
        Получение исторических данных о ценах актива из Redis.
        :param token: Тикер криптовалюты.
        :param period: Количество последних цен.
        :return: Список цен.
        """
        key = f"prices:{token}"
        data = self.redis_cli.lrange(key, -period, -1)
        return [float(price) for price in data]

    def calculate_rsi(self, prices: List[float]) -> float:
        """
        Расчет значения RSI на основе списка цен.
        :param prices: Список цен актива.
        :return: Значение RSI.
        """
        if len(prices) < self.rsi_period:
            return 0.0

        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains[-self.rsi_period:]) / self.rsi_period
        avg_loss = sum(losses[-self.rsi_period:]) / self.rsi_period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def analyze_rsi(self, token: str):
        """
        Проверка значения RSI и генерация торгового сигнала.
        :param token: Тикер криптовалюты.
        """
        prices = self.fetch_price_data(token, self.rsi_period + 1)
        rsi = self.calculate_rsi(prices)

        if rsi > self.overbought_level:
            signal = "Sell"
            recommendation = "Consider selling."
        elif rsi < self.oversold_level:
            signal = "Buy"
            recommendation = "Consider buying."
        else:
            return  # Нет сигнала

        self.send_telegram_signal(token, signal, rsi, recommendation)
        self.log_signal(token, rsi, signal)

    def send_telegram_signal(self, token: str, signal: str, rsi: float, recommendation: str):
        """
        Отправка сигнала в Telegram-чат.
        :param token: Тикер криптовалюты.
        :param signal: Тип сигнала (Buy/Sell).
        :param rsi: Значение RSI.
        :param recommendation: Рекомендация для пользователя.
        """
        message = (f"Signal for {token}:\n"
                   f"RSI: {rsi:.2f}\n"
                   f"Signal: {signal}\n"
                   f"Recommendation: {recommendation}")
        url = f"https://api.telegram.org/bot{self.telegram_api_key}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message
        }
        requests.post(url, json=payload)

    def log_signal(self, token: str, rsi: float, signal: str):
        """
        Добавление записи о сигнале в журнал сигналов.
        :param token: Тикер криптовалюты.
        :param rsi: Значение RSI.
        :param signal: Тип сигнала (Buy/Sell).
        """
        self.signals_log.append({
            "token": token,
            "rsi": rsi,
            "signal": signal
        })

    def start_analysis(self):
        """
        Запуск анализа для всех токенов из списка.
        """
        for token in self.tokens:
            self.analyze_rsi(token)