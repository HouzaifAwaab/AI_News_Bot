import os
import json
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from aiogram.enums import ParseMode

from app.rss_fetcher import RSSFetcher
from app.db import init_db, add_source, get_connection, mark_as_sent, is_source_active
from app.summarizer import process_news
from app.common import logger, get_bot, clean_html, CHANNEL_ID
from app.llm_processor import summarize_news

current_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(current_dir, 'fetchers', 'Config', 'config.json')

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

FETCHER_CLASSES = {'rss': RSSFetcher}

async def process_fetcher_results(source_id, fetcher):
    if not is_source_active(source_id):
        return 0
    items = await fetcher.fetch()
    processed = await process_news(items)
    return len(processed)

def schedule_source(source_id, config):
    url = config.get('url')
    lang = config.get('lang', 'ar')
    fetcher = RSSFetcher(source_id, url, lang)
    scheduler.add_job(process_fetcher_results, 'interval', args=[source_id, fetcher], minutes=config.get('interval', 15), id=f"fetch_{source_id}")
    add_source(source_id, f"{source_id} ({lang})")

scheduler = AsyncIOScheduler(timezone=timezone('UTC'))

async def init_scheduler():
    init_db()
    config = load_config()
    for source_id, source_config in config.items():
        add_source(source_id, f"{source_id} ({source_config.get('lang', 'ar')})")
    for source_id, source_config in config.items():
        if is_source_active(source_id):
            schedule_source(source_id, source_config)
    scheduler.start()
    # Keep running for Actions
    while True:
        await asyncio.sleep(60)
