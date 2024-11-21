import threading
from message_broker import message_broker_module


# Инициализация модулей
broker = message_broker_module.MessageBroker()

# Создание потоков
# thread1 = threading.Thread(target=task_module_1)
# thread2 = threading.Thread(target=task_module_2)
# thread3 = threading.Thread(target=task_module_3)
# thread4 = threading.Thread(target=task_module_4)
thread5 = threading.Thread(target=broker.run_broker())
