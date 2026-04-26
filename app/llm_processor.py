import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=os.path.join("keys", "keys.env"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

async def summarize_news(articles_text):
    prompt = f"""
    لخّص الأخبار التالية باللغة العربية في نقاط قصيرة وموجزة:
    {articles_text}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return ""

def detect_language(text):
    return "ar" if any('\u0600' <= c <= '\u06ff' for c in text) else "en"
