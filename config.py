class Config:
    """Класс для хранения конфигурационных данных приложения."""
    def __init__(self):
        self.MYSQL_CONFIG = {
            'HOST': 'lapluquetri.beget.app',  
            'USER': 'KGx2_database', 
            'PASSWORD': 'KGx2_db_password_tppo',  
            'DATABASE': 'KGx2_database' 
        }

        self.CONNECT_MYSQL_STRING = (
            f"mysql+pymysql://"
            f"{self.MYSQL_CONFIG['USER']}:"  
            f"{self.MYSQL_CONFIG['PASSWORD']}@"  
            f"{self.MYSQL_CONFIG['HOST']}/" 
            f"{self.MYSQL_CONFIG['DATABASE']}"  
        )

        self.TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token'  

        self.REDIS_CONFIG = {
            'HOST': '192.168.112.103', 
            'PORT': 6379,  
            'DATABASE': 0,
            'PASSWORD': 'student'
        }