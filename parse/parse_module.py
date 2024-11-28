import pybit.unified_trading
import redis
import time
import threading
from ..config import *
from ..models.models import Tokens


class Parse():
    """ Класс парсинга биржи Bybit
        Принимает параметрами при инициализации ORM модель
        таблицы токенов и кофигурационный класс.
        Пример данных в redis - {KGx2___BTCUSDT.1732791446430: 95136.7} """
    def __init__(self, tokens_table: Tokens):
        self.redis_cli = self.create_redis_connection()
        self.tokens_table = tokens_table
        self.tokens = self.get_tokens()
        self.last_timestamps = {}
        self.websocket = self.create_websocket()
        self.stop_event = threading.Event()

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        """ Метод для завершения всех потоков """
        self.stop_event.set() 
        self.websocket.exit() 
        self.close_redis_connection() 

    def get_tokens(self) -> list:
        """ Получение списка криптовалют из таблицы
            Метод записывает тикеры криптовалют в поле tokens """
        tokens = []
        tikers = self.tokens_table.get_tikers()
        
        for tiker in tikers:
            tokens.append(tiker)

        return tokens

    def create_redis_connection(self) -> redis.Redis:
        """ Создание клиента Redis
            метод возвращает redis-клиент, записывает результат 
            в поле redis_cli """
        return redis.Redis(host=REDIS_CONFIG['HOST'], 
                            port=REDIS_CONFIG['PORT'], 
                            db=REDIS_CONFIG['DATABASE'],
                            password=REDIS_CONFIG['PASSWORD'])

    def close_redis_connection(self) -> None:
        """Закрытие соединения с Redis"""
        self.redis_cli.close()

    def create_websocket(self) -> pybit.unified_trading.WebSocket:
        """ Создание веб-сокета для работы с Bybit
            Метод возвращает веб-сокет, записывая его в поле websocket """
        ws = pybit.unified_trading.WebSocket(
            testnet=False,
            channel_type="linear",
        )
        return ws

    def parse_bybit(self) -> None:
        """ Парсинг биржи ByBit
            Метод выводит свечи криптовалют на экран, а также 
            записывает их в Redis. Время жизни свечи в Redis - 6ч30м.
            Метод обрабатывет ошибки, влекующие к остановке работы, в 
            подобных случаях произойдет переподключение, максимальное 
            количество переподключений - 5"""
        def handle_message(message):
            try:
                topic = message['topic']
                symbol = topic.split('.')[2] 
                timestamp = message['ts']  
                close_price = message['data'][0]['close']  

                if symbol not in self.last_timestamps:
                    self.last_timestamps[symbol] = timestamp
                    self.redis_cli.set(name=f"KGx2___{symbol}.{timestamp}", value=float(close_price), ex=23400)
                    print(f'KGx2___{symbol}.{timestamp}: {float(close_price)}')
                else:
                    last_timestamp = self.last_timestamps[symbol]
                    time_difference = abs(timestamp - last_timestamp)

                    if time_difference >= 900000:
                        self.last_timestamps[symbol] = timestamp
                        self.redis_cli.set(name=f"KGx2___{symbol}.{timestamp}", value=float(close_price), ex=23400)
                        print(f'KGx2___{symbol}.{timestamp}: {float(close_price)}')

            except Exception as e:
                print(f"Error processing message: {e}")

        for token in self.tokens:
            attempts = 0
            max_attempts_count = 5  
            
            while attempts < max_attempts_count:
                try:
                    self.websocket.kline_stream(
                        interval=15,  
                        symbol=token,
                        callback=handle_message
                    )
                    break  
                
                except Exception as e:
                    attempts += 1
                    print(f"Error subscribing to {token}: {e}. Attempt {attempts}/{max_attempts_count}")
                    time.sleep(2)  

        while True:
            time.sleep(1)