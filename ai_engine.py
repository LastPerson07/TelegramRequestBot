import json
import re
from google import genai
from config import GEMINI_API_KEY, logger

# ✅ NEW: Initialize the modern Client
client = genai.Client(api_key=GEMINI_API_KEY)

# ✅ VERIFIED: Use 'gemini-3-flash' on the stable v1 path
MODEL_ID = "gemini-3-flash"

def extract_json(text: str):
    """Clean the AI response and extract valid JSON."""
    try:
        # Gemini 3 often wraps output in markdown blocks
        cleaned_text = re.sub(r"`json|```", "", text).strip()
        match = re.search(r"\{.*\}", cleaned_text, re.S)
        if not match: return None
        return json.loads(match.group())
    except Exception as e:
        logger.error(f"JSON Parse Error: {e}")
        return None

async def analyze_request(text: str):
    prompt = f"""
    Classify this message: "{text}"
    Return ONLY JSON:
    {{
      "intent": "request" | "chat" | "unclear",
      "title": "Movie/Series Name",
      "reply": "Short response"
    }}
    """
    try:
        # ✅ NEW: The modern SDK uses models.generate_content
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        
        if not response or not response.text:
            return {"intent": "unclear", "reply": "I'm a bit lost. Try again?"}
            
        return extract_json(response.text)
        
    except Exception as e:
        logger.error(f"AI Engine Error: {e}")
        # 🛡️ Emergency Fallback: If API fails, check for keywords manually
        if any(w in text.lower() for w in ["movie", "series", "watch", "download"]):
            return {"intent": "request", "title": text.strip(), "reply": "Logged your request!"}
        return {"intent": "chat", "reply": "My AI is updating, but I can still hear you!"}

async def get_witty_rejection(title: str):
    try:
        r = client.models.generate_content(model=MODEL_ID, contents=f"Short funny rejection for {title}")
        return r.text.strip()
    except: return f"Sorry, {title} is unavailable."

async def get_admin_acceptance_msg(title: str):
    try:
        r = client.models.generate_content(model=MODEL_ID, contents=f"Short hype message for {title}")
        return r.text.strip()
    except: return f"✅ {title} is ready!"
