import json # Fixed case
import re
import google.generativeai as genai
from config import GEMINI_API_KEY, logger

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_json(text: str):
    # Improved regex to handle markdown code blocks
    text = re.sub(r"`json|```", "", text)
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return None
    return json.loads(match.group())

async def analyze_request(text: str):
    prompt = f"Classify this message for a movie bot: '{text}'. Return ONLY JSON with keys: intent (request/chat/unclear), title (if movie), reply (your response)."
    try:
        r = await model.generate_content_async(prompt)
        return extract_json(r.text)
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return None

async def get_witty_rejection(title: str):
    try:
        r = await model.generate_content_async(
            f"Funny short rejection reason for {title}"
        )
        return r.text.strip()
    except:
        return "Request rejected."

async def get_admin_acceptance_msg(title: str):
    try:
        r = await model.generate_content_async(
            f"Short hype message for {title} upload"
        )
        return r.text.strip()
    except:
        return "Your request is completed!"   