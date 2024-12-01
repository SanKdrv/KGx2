from .base_model import BaseModel
import sqlalchemy as db
import typing


# Создание моделей:
# users = Users('Users')
# tokens = Tokens('Tokens')
# users_tokens = UsersTokens('UsersTokens')

class Users(BaseModel):
    """Класс для работы с таблицей пользователей"""
    def __init__(self, table_name: str):
        super().__init__(table_name)

    def check_user_existence(self, user_UID: str) -> bool:
        """
        Проверка наличия записей о пользователе в БД
        """
        check_user_already_created_query = db.select(self.table).where(self.table.c.UID == user_UID)
        check_user_already_created_query_result = self.connection.execute(check_user_already_created_query)

        # Пользователь не принимал политику пользования
        if len(check_user_already_created_query_result.fetchall()) == 0:
            return True
        # Пользователь уже принял политику пользования
        else:
            return False

    def check_user_limit(self, user_UID: str) -> int:
        """ Проверка лимита пользователя по его UID
            Метод возвращает -1, если не найден
            пользователь с заданным UID """
        user_limit_query = db.select(self.table.c.Limit).where(self.table.c.UID == user_UID)
        query_result = self.connection.execute(user_limit_query) 
        result = query_result.fetchone()  
        
        if result is not None:
            return int(result[0])
        else:
            return -1     

    def add_user(self, user_UID: str) -> str:
        """ Добавление пользователя по его UID
            Метод возвращает сообщение об успешности 
            операции, оповещая, если пользователь с 
            данным UID уже создан """
        check_user_already_created_query = db.select(self.table).where(self.table.c.UID == user_UID)
        check_user_already_created_query_result = self.connection.execute(check_user_already_created_query)

        if len(check_user_already_created_query_result.fetchall()) == 0:
            inserted_user_query = self.table.insert().values(
                UID = user_UID,
                Limit = 80
            )
            self.connection.execute(inserted_user_query)
            self.connection.commit()
            return 'User successfulle created'
        else:
            return 'User with that UID already created'

    def dec_user_limit(self, user_UID: str) -> str:
        """ Уменьшение лимита пользователя по его UID
            Метод возвращает сообщение об успешности
            операции, оповещая, если данный пользователь
            уже имеет нулевой лимит запросов """
        current_limit = self.check_user_limit(user_UID) 
        if current_limit > 0:
            updated_limit = current_limit - 1 
            update_query = self.table.update().where(self.table.c.UID == user_UID).values(Limit=updated_limit)    
            self.connection.execute(update_query)
            self.connection.commit()
            return 'Limit successfully updated'
        else:
            return 'User already have zero`s limit'
        
    def reset_users_limits(self) -> None:
        """ Восстановление лимитов пользователей 
            Метод устанавливает всем пользователям 
            дневной лимит в дефолтное значение """
        default_limit = 80
        reset_limits_query = db.update(self.table).values(Limit=default_limit) 
        self.connection.execute(reset_limits_query)
        self.connection.commit()


class Tokens(BaseModel):
    """Класс для работы с таблицей токенов"""
    def __init__(self, table_name: str):
        super().__init__(table_name)

    def get_tikers(self) -> typing.List[str]:
        """ Получение тикеров (имен токенов)
            Метод возвращает массив, содержащий
            тикеры всех отслеживаемых криптовалют """
        tikers_query = db.select(self.table.c.Tiker)
        tikers_query_result = self.connection.execute(tikers_query)
        tikers = []

        for tiker in tikers_query_result.fetchall():
            tikers.append(tiker[0])
        
        return tikers

    def get_token_ID(self, tiker: str) -> str:
        """ Получение id криптовалюты по тикеру"""
        token_ID_by_tiker_query = db.select(self.table).where(self.table.c.Tiker == tiker)
        query_result = self.connection.execute(token_ID_by_tiker_query)
        return str(query_result.fetchone()[0])

    def get_tiker_by_token_ID(self, token_ID: int) -> str:
        """ Получение тикера по id криптовалюты
            Метод принимает id криптовалюты и возвращает 
            тикер данной криптовалюты, если такая есть, 
            иначе возвращает соответствующее сообщение """
        tiker_by_token_ID_query = db.select(self.table).where(self.table.c.TokenID == token_ID)
        query_result = self.connection.execute(tiker_by_token_ID_query)

        if len(query_result.fetchone()) == 1:
            return str(query_result.fetchone()[1])
        else:
            return 'No token found with given id'


class UsersTokens(BaseModel):
    """Класс для работы с таблицей пользователей и токенов"""
    def __init__(self, table_name: str):
        super().__init__(table_name)

    def get_users_by_token(self, token_ID: int) -> typing.List[str]:
        """ Получение списка пользователей по ID токена
            Метод принимает token_ID и возвращает список 
            UID пользователя, которые подписаны на этот токен """
        users_by_token_query = db.select(self.table).where(self.table.c.TokenID == token_ID)
        query_result = self.connection.execute(users_by_token_query)
        result = []

        for row in query_result.fetchall():
            result.append(row.UID)

        return result 
        
    def get_tokens_by_user(self, user_UID: str) -> typing.List[int]:
        """ Получение списка токенов по UID пользователя
            Метод принимает UID пользователя и возвращает
            список id криптовалют, на которые подписан 
            данный пользователь """
        tokens_by_user_query = db.select(self.table).where(self.table.c.UID == user_UID)
        query_result = self.connection.execute(tokens_by_user_query)
        result = []

        for row in query_result.fetchall():
            result.append(row.TokenID)

        return result          
    
    def add_token_for_user(self, user_UID: str, token_ID: int) -> str:
        """ Добавление подписки пользователя на криптовалюту
            Метод принимает UID пользователя и id криптовалюты, 
            на которую произошла подписка, выводя сообщение об
            успешности операции """
        try:
            inserted_usertoken_query = self.table.insert().values(
                UID = user_UID,
                TokenID = token_ID
            )
            self.connection.execute(inserted_usertoken_query)
            self.connection.commit()
            return 'Token successfully added to the tracking list'     
        except:
            return 'Error during adding token to the tracking list. Maybe that user already has that token in tracking list'

    def remove_token_for_user(self, user_UID: str, token_ID: int) -> str:
        """ Удаление подписки пользователя на криптовалюту
            Метод принимает UID пользователя и id токена,
            возвращает сообщение об успешности операции """
        exists_query = self.table.select().where(
            (self.table.c.UID == user_UID) & (self.table.c.TokenID == token_ID)
        )
        result = self.connection.execute(exists_query).fetchone()

        if result is not None:
            removes_usertoken_query = self.table.delete().where(
                (self.table.c.UID == user_UID) & (self.table.c.TokenID == token_ID)
            )
            self.connection.execute(removes_usertoken_query)
            self.connection.commit()
            return 'Token successfully removed from the tracking list'  
        
        return ('Error during removing token from the tracking list. Maybe that user does not have this token in his '
                'tracking list')
