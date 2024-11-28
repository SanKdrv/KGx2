import os
from aiogram import Bot, Dispatcher
from dotenv import find_dotenv, load_dotenv
from chatbot.handlers.user_private import user_private_router