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

    def get_actual_data_from_redis(self, token_name: str) -> str:
        ...

    def get_new_subscribtions(self, token_name: str) -> [str]:
        ...

    def get_subscribtions(self, token_name: str) -> [str]:
        ...

    def send_data_to_chatbot(self, data: str) -> str:
        ...
