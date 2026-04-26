import logging
from app.db import add_news_item
from app.ranker import compute_score
from datetime import datetime

logger = logging.getLogger(__name__)

async def process_news(items):
    processed = []
    for item in items:
        url = item.get("link")
        title = item.get("title")
        source_id = item.get("source_id")
        published = item.get("published") or datetime.now().isoformat()
        if isinstance(published, str):
            try:
                published = datetime.fromisoformat(published)
            except:
                published = datetime.now()
        score = compute_score(url=url, title=title, source_id=source_id, published=published)
        impact = min(3, max(1, int(score / 2)))
        added = add_news_item(url, title, source_id, published, score, impact, "")
        if added:
            processed.append({"url": url, "title": title, "source_id": source_id, "impact": impact})
    return processed
