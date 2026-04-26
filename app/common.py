import os
import logging
from aiogram import Bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("TG_CHANNEL_ID")

_bot = None

def get_bot():
    global _bot
    if _bot is None:
        _bot = Bot(token=TOKEN)
    return _bot

def set_bot(bot_instance):
    global _bot
    _bot = bot_instance

import re

def clean_html(raw_html):
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()
