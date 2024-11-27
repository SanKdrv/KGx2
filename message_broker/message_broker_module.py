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

    def get_new_subscribtions(self, token_name: str) -> [str]:
        ...

    def get_subscribtions(self, token_name: str) -> [str]:
        ...

    def send_data_to_chatbot(self, data: str) -> str:
        ...
