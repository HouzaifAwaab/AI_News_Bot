import asyncio
import json
import os
import logging
from app.rss_fetcher import RSSFetcher
from app.db import init_db, add_source
from app.summarizer import process_news
from app.publisher import post_digest
from app.common import get_bot, set_bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join('fetchers', 'Config', 'config.json')

async def main():
    # 1. تجهيز قاعدة البيانات
    init_db()

    # 2. تحميل قائمة المصادر
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        sources = json.load(f)

    bot = get_bot()
    all_new_news = []

    for source_id, cfg in sources.items():
        if cfg.get("type") != "rss":
            continue
        # إضافة المصدر في قاعدة البيانات لو أول مرة (نشط دائماً)
        add_source(source_id, f"{source_id} ({cfg.get('lang', 'ar')})")

        fetcher = RSSFetcher(source_id, cfg["url"], cfg.get("lang", "ar"))
        items = await fetcher.fetch()
        if not items:
            continue

        # معالجة وإضافة الجديد فقط
        new_items = await process_news(items)
        if new_items:
            logger.info(f"[{source_id}] تم جلب {len(new_items)} خبر جديد")
            all_new_news.extend(new_items)

    # 3. إذا في أخبار جديدة، نبني الملخص ونرسله
    if all_new_news:
        await post_digest(all_new_news)
    else:
        logger.info("لا توجد أخبار جديدة")

    # 4. إغلاق جلسة البوت
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
