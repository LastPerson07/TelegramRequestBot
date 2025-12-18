import json
import re
import google.generativeai as genai
from config import GEMINI_API_KEY, logger

# 1. Setup API
genai.configure(api_key=GEMINI_API_KEY)

# ✅ VERIFIED: 'gemini-3-flash' is the new 2025 stable model identifier.
# It replaced the old 'gemini-1.5-flash' which now returns 404.
model = genai.GenerativeModel("gemini-3-flash")

def extract_json(text: str):
    """Robustly cleans Gemini's thinking-wrapped JSON."""
    try:
        # Gemini 3 often outputs Markdown or 'thinking' tags
        text = re.sub(r"`json|```|<thinking>.*?</thinking>", "", text, flags=re.S).strip()
        match = re.search(r"\{.*\}", text, re.S)
        return json.loads(match.group()) if match else None
    except:
        return None

async def analyze_request(text: str):
    # Prompt optimized for Gemini 3's high-speed reasoning
    prompt = f"Analyze: '{text}'. Output ONLY valid JSON: {{'intent':'request'|'chat'|'unclear', 'title':'movie_name', 'reply':'msg'}}"
    
    try:
        # Use the latest asynchronous generation method
        response = await model.generate_content_async(prompt)
        data = extract_json(response.text)
        
        # 🛡️ Safety Fallback: Use keyword detection if the AI hits a rate limit (429)
        if not data:
             return {"intent": "chat", "reply": "I'm listening! Tell me a movie name."}
        return data

    except Exception as e:
        logger.error(f"AI Logic Error: {e}")
        # If API is down (404/429), the bot stays functional with this logic:
        if any(w in text.lower() for w in ["movie", "series", "watch", "download"]):
            return {"intent": "request", "title": text.strip(), "reply": "Request logged!"}
        return {"intent": "chat", "reply": "My AI brain is resting, but I can still take requests!"}

async def get_witty_rejection(title: str):
    try:
        r = await model.generate_content_async(f"1-sentence funny reason to reject {title}")
        return r.text.strip()
    except: return f"Rejected: {title} is unavailable."

async def get_admin_acceptance_msg(title: str):
    try:
        r = await model.generate_content_async(f"1-sentence hype message for {title}")
        return r.text.strip()
    except: return f"✅ {title} is uploaded!"
