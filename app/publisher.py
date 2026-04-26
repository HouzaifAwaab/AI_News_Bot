from app.llm_processor import summarize_news
from app.common import get_bot, CHANNEL_ID
import logging

logger = logging.getLogger(__name__)

async def post_digest(news_items):
    """
    news_items: قائمة من dict فيها title, link, source_id
    """
    if not news_items:
        return

    # تجهيز نص للـ LLM من العناوين فقط
    titles_only = "\n".join(f"- {item['title']}" for item in news_items)
    summary_text = await summarize_news(f"لخّص هذه الأخبار في 3-4 جمل عربية موجزة:\n{titles_only}")

    # بناء الرسالة النهائية
    message = ""
    if summary_text:
        message += f"📰 *ملخص الأخبار*\n\n{summary_text}\n\n"

    message += "🔗 *المراجع:*\n"
    for idx, item in enumerate(news_items, 1):
        title = item.get('title', 'خبر')
        link = item.get('link', '#')
        message += f"{idx}. [{title}]({link})\n"

    bot = get_bot()
    try:
        await bot.send_message(
            chat_id=int(CHANNEL_ID),      # تأكد إنه رقم صحيح
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        logger.info(f"تم إرسال ملخص {len(news_items)} خبر")
    except Exception as e:
        logger.error(f"فشل الإرسال: {e}")
