MYSQL_CONFIG = {
    'HOST': 'имя хоста',
    'USER': 'логин',
    'PASSWORD': 'пароль',
    'DATABASE': 'бд'
}

CONNECT_MYSQL_STRING = (
    f"mysql+pymysql://"
    f"{MYSQL_CONFIG['USER']}:"  
    f"{MYSQL_CONFIG['PASSWORD']}@"  
    f"{MYSQL_CONFIG['HOST']}/" 
    f"{MYSQL_CONFIG['DATABASE']}"
)

TELEGRAM_BOT_TOKEN = 'токен бота'

REDIS_CONFIG = {
    'HOST': 'имя хоста',
    'PORT': 6379,
    'DATABASE': 0,
    'PASSWORD': 'пароль'
}

admins_id = [int('Тг айди админа'), int('Тг айди админа')]
