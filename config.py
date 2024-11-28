MYSQL_CONFIG = {
    'HOST': 'lapluquetri.beget.app',
    'USER': 'KGx2_database',
    'PASSWORD': 'KGx2_db_password_tppo',
    'DATABASE': 'KGx2_database'
}

CONNECT_MYSQL_STRING = (
    f"mysql+pymysql://"
    f"{MYSQL_CONFIG['USER']}:"  
    f"{MYSQL_CONFIG['PASSWORD']}@"  
    f"{MYSQL_CONFIG['HOST']}/" 
    f"{MYSQL_CONFIG['DATABASE']}"
)

TELEGRAM_BOT_TOKEN = '7562890523:AAHunLwe5hVVQrGBP3RzYv7qcP3lIxVmGt4'

REDIS_CONFIG = {
    'HOST': '192.168.112.103',
    'PORT': 6379,
    'DATABASE': 0,
    'PASSWORD': 'student'
}