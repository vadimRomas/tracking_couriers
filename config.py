import os

import pytz


telegram_token = os.getenv('telegram_token')
tz = pytz.timezone("Europe/Kyiv")
proxy_url = os.getenv('proxy_url')
