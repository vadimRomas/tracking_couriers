import pytz
from dotenv import dotenv_values
from telebot import TeleBot

telegram_token = dotenv_values(".env")['telegram_token']
proxy_url = dotenv_values(".env")['proxy_url'] if 'proxy_url' in dotenv_values("env") else None
spreadsheet_id = dotenv_values(".env")['spreadsheet_id']
google_json = dotenv_values(".env")['google_json']

tz = pytz.timezone("Europe/Kyiv")

bot = TeleBot(telegram_token)


