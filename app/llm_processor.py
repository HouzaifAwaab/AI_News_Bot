import os
import asyncio
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

# المفتاح بيُقرأ من البيئة بعد ما GitHub يضخه
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

async def summarize_news(articles_text):
    prompt = f"""
    لخّص الأخبار التالية باللغة العربية في 3-4 جمل موجزة:
    {articles_text}
    """
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return ""

def detect_language(text):
    return "ar" if any('\u0600' <= c <= '\u06ff' for c in text) else "en"
