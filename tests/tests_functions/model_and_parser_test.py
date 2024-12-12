import pytest
from models.models import Users, Tokens, UsersTokens
from unittest.mock import MagicMock, patch
from parse.parse_module import Parse
from config import CONNECT_MYSQL_STRING
import random
import string
import redis
import threading


def generate_random_string(length: int) -> str:
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


@pytest.fixture(scope="module")
def setup_database():
    yield


class TestUsers:
    @pytest.fixture(autouse=True)
    def setup(self, setup_database):
        self.users = Users("Users")

    def test_add_user_success(self):
        """Позитивный тест для добавления пользователя"""
        secure_random_str = generate_random_string(10)
        result = self.users.add_user(secure_random_str)
        assert result == "User successfulle created"

    def test_add_user_failure(self):
        """Негативный тест для добавления существующего пользователя"""
        secure_random_str = generate_random_string(10)
        self.users.add_user(secure_random_str)
        result = self.users.add_user(secure_random_str)
        assert result == "User with that UID already created"

    def test_check_user_existence_success(self):
        """Позитивный тест для проверки существования пользователя"""
        secure_random_str = generate_random_string(10)
        self.users.add_user(secure_random_str)
        exists = self.users.check_user_existence(secure_random_str)
        assert exists is False

    def test_check_user_existence_failure(self):
        """Негативный тест для проверки несуществующего пользователя"""
        secure_random_str = generate_random_string(10)
        exists = self.users.check_user_existence(secure_random_str)
        assert exists is True

    def test_dec_user_limit_success(self):
        """Позитивный тест для уменьшения лимита пользователя"""
        secure_random_str = generate_random_string(10)
        self.users.add_user(secure_random_str)
        result = self.users.dec_user_limit(secure_random_str)
        assert result == "Limit successfully updated"

    def test_reset_users_limits(self):
        """Тест для сброса лимитов пользователей"""
        secure_random_str = generate_random_string(10)
        self.users.add_user(secure_random_str)
        self.users.dec_user_limit(secure_random_str)
        self.users.reset_users_limits()
        limit = self.users.check_user_limit(secure_random_str)
        assert limit == 80


class TestTokens:
    @pytest.fixture(autouse=True)
    def setup(self, setup_database):
        self.tokens = Tokens("Tokens")

    def test_get_tikers(self):
        """Позитивный тест для получения тикеров"""
        tikers = self.tokens.get_tikers()
        assert isinstance(tikers, list)

    def test_get_token_ID_success(self):
        """Позитивный тест для получения ID токена по тикеру"""
        token_id = self.tokens.get_token_ID("BTCUSDT")
        assert isinstance(token_id, str)



@pytest.fixture
def tokens_table_mock():
    """Фикстура для создания заглушки таблицы токенов."""
    mock = MagicMock(spec=Tokens)
    mock.get_tikers.return_value = ['BTCUSDT', 'ETHUSDT']
    return mock

@pytest.fixture
def parse_instance(tokens_table_mock):
    """Фикстура для создания экземпляра класса Parse."""
    return Parse(tokens_table=tokens_table_mock)

def test_create_redis_connection(parse_instance):
    """Тест на создание соединения с Redis.
    Входные данные: нет.
    Ожидаемый результат: возвращается объект Redis."""
    redis_client = parse_instance.create_redis_connection()
    assert redis_client is not None
    assert isinstance(redis_client, redis.Redis)

def test_get_tokens(parse_instance):
    """Тест на получение токенов.
    Входные данные: mock таблицы токенов с двумя тикерами.
    Ожидаемый результат: возвращается список с двумя токенами."""
    tokens = parse_instance.get_tokens()
    assert tokens == ['BTCUSDT', 'ETHUSDT']

def test_create_websocket(parse_instance):
    """Тест на создание веб-сокета.
    Входные данные: нет.
    Ожидаемый результат: возвращается объект WebSocket."""
    websocket = parse_instance.create_websocket()
    assert websocket is not None