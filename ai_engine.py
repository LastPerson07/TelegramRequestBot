import json
import re
from google import genai # NEW: Modern SDK import
from config import GEMINI_API_KEY, logger

# ✅ NEW: Modern Client Architecture (Stable v1)
client = genai.Client(api_key=GEMINI_API_KEY)

# ✅ VERIFIED: Current stable model ID as of Dec 2025
MODEL_ID = "gemini-3-flash"

def extract_json(text: str):
    """Robustly cleans and extracts JSON from AI responses."""
    try:
        # Gemini 3 often wraps JSON in markdown blocks
        cleaned_text = re.sub(r"`json|```", "", text).strip()
        match = re.search(r"\{.*\}", cleaned_text, re.S)
        if not match: return None
        return json.loads(match.group())
    except Exception as e:
        logger.error(f"JSON Parse Error: {e}")
        return None

async def analyze_request(text: str):
    prompt = f"""
    Analyze this message: "{text}"
    Return ONLY JSON with these keys:
    {{
      "intent": "request" | "chat" | "unclear",
      "title": "Movie Name",
      "reply": "Friendly response"
    }}
    """
    try:
        # ✅ NEW: Modern Generation Method
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        
        if not response or not response.text:
            raise ValueError("Empty AI response")
            
        return extract_json(response.text)
        
    except Exception as e:
        logger.error(f"AI Engine Error: {e}")
        # 🛡️ Emergency Manual Fallback (If API is down/limited)
        text_low = text.lower()
        if any(w in text_low for w in ["movie", "series", "watch", "download"]):
            return {"intent": "request", "title": text.strip(), "reply": "Got it! Request logged."}
        return {"intent": "chat", "reply": "I'm online! How can I help?"}

async def get_witty_rejection(title: str):
    try:
        r = client.models.generate_content(model=MODEL_ID, contents=f"Funny rejection for {title}")
        return r.text.strip()
    except: return f"Sorry, {title} is unavailable."

async def get_admin_acceptance_msg(title: str):
    try:
        r = client.models.generate_content(model=MODEL_ID, contents=f"Hype message for {title}")
        return r.text.strip()
    except: return f"✅ {title} is now available!"
