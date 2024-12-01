from models.models import *
# Запуск: E:\study\5sem\tppo\KGx2\.venv\Scripts\python.exe .\reset_users_limits_script.py

if __name__ == '__main__':
    users = Users('Users')
    users.reset_users_limits()
