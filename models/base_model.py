import sqlalchemy as db
import typing
from config import *

class BaseModel():
    """Базовый класс для работы с таблицами MySQL."""
    def __init__(self, table_name: str):
        self.engine = db.create_engine(CONNECT_MYSQL_STRING)
        self.connection = self.engine.connect()
        self.metaData = db.MetaData()
        self.metaData.reflect(bind = self.engine)
        self.table = db.Table(table_name, self.metaData, autoload_with = self.engine)
    
    def close_connection(self) -> None:
        """Закрытие соединения с базой данных"""
        self.connection.close()

    def select_all(self) -> typing.List[dict]:
        """ Выбор всех записей из таблицы и вывод их на экран
            Метод возвращает массив словарей (записи таблицы) """
        select_all_query = db.select(self.table)
        query_result = self.connection.execute(select_all_query)
        result = []
        column_names = list(query_result.keys())

        for row in query_result.fetchall():
            element = dict(zip(column_names, row))
            result.append(element)

        return result