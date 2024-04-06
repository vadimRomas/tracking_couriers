import pytz
from dotenv import dotenv_values
from telebot import TeleBot

telegram_token = dotenv_values(".env")['telegram_token']
tz = pytz.timezone("Europe/Kyiv")
proxy_url = dotenv_values(".env")['proxy_url'] if 'proxy_url' in dotenv_values("env") else None

bot = TeleBot(telegram_token)
