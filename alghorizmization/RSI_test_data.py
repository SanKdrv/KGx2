import pandas as pd
from datetime import datetime


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

    return float(df['rsi'].iloc[-1])  # Приведение к типу float


# Тестовые данные с уникальными временными метками
test_data = [
    "KGx2___BTCUSDT.1732791446430: 95136.7}",
    "KGx2___BTCUSDT.1732791446431: 95036.7}",
    "KGx2___BTCUSDT.1732791446432: 95436.7}",
    "KGx2___BTCUSDT.1732791446433: 95236.7}",
    "KGx2___BTCUSDT.1732791446434: 95186.7}",
    "KGx2___BTCUSDT.1732791446435: 95146.7}",
    "KGx2___BTCUSDT.1732791446436: 95096.7}",
    "KGx2___BTCUSDT.1732791446437: 95256.7}",
    "KGx2___BTCUSDT.1732791446438: 95306.7}",
    "KGx2___BTCUSDT.1732791446439: 95386.7}",
    "KGx2___BTCUSDT.1732791446440: 95446.7}",
    "KGx2___BTCUSDT.1732791446441: 95396.7}",
    "KGx2___BTCUSDT.1732791446442: 95246.7}",
    "KGx2___BTCUSDT.1732791446443: 95196.7}",
]

# Парсинг тестовых данных
parsed_data = []
for entry in test_data:
    ticker, value = entry.split(": ")
    timestamp = int(ticker.split(".")[1])  # Извлечение временной метки
    price = float(value.rstrip("}"))  # Извлечение цены
    clean_ticker = ticker.split(".")[0].split("___")[1]  # Удаление KGx2___
    parsed_data.append((clean_ticker, timestamp, price))

# Преобразование временной метки в читаемый формат
for i, (ticker, timestamp, price) in enumerate(parsed_data):
    readable_time = datetime.fromtimestamp(
        timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
    parsed_data[i] = (ticker, readable_time, price)

# Извлечение цен для расчета RSI
prices = [price for _, _, price in parsed_data]

# Основной код для расчета RSI
if len(prices) < 14:
    print("Недостаточно данных для расчета RSI.")
else:
    rsi = calculate_rsi(prices)
    current_price = prices[-1]
    ticker = parsed_data[-1][0]
    time = parsed_data[-1][1]
    result = [ticker, time, current_price, round(rsi, 2)]
    print(result)
