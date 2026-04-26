import aiohttp
import feedparser
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RSSFetcher:
    def __init__(self, source_id, url, lang="ar"):
        self.source_id = source_id
        self.url = url
        self.lang = lang

    async def fetch(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, timeout=30) as response:
                    text = await response.text()
            feed = feedparser.parse(text)
            items = []
            for entry in feed.entries[:10]:
                items.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published", datetime.now().isoformat()),
                    "source_id": self.source_id,   # <--- أضف هذا السطر
                })
            return items
        except Exception as e:
            logger.error(f"Error fetching RSS {self.url}: {e}")
            return []
