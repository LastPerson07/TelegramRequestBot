import json
import re
import google.generativeai as genai
from config import GEMINI_API_KEY, logger

# Configure the API
genai.configure(api_key=GEMINI_API_KEY)

# ✅ FIX: Use 'gemini-1.5-flash' which automatically points to the latest stable v1 endpoint
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_json(text: str):
    """Clean the AI response and extract valid JSON."""
    try:
        # Remove markdown code blocks if present
        cleaned_text = re.sub(r"`json|```", "", text).strip()
        match = re.search(r"\{.*\}", cleaned_text, re.S)
        if not match:
            return None
        return json.loads(match.group())
    except Exception as e:
        logger.error(f"JSON Parse Error: {e}")
        return None

async def analyze_request(text: str):
    prompt = f"""
    You are a classification assistant for a movie bot. 
    Analyze the message: "{text}"
    Return ONLY JSON:
    {{"intent": "request", "title": "Movie Name", "type": "Movie/Series", "reply": "Confirming..."}}
    {{"intent": "chat", "reply": "Friendly response"}}
    {{"intent": "unclear", "reply": "Ask for movie name"}}
    """
    
    try:
        # Set a short timeout to prevent the bot from hanging
        response = await model.generate_content_async(prompt)
        
        if not response or not response.text:
            return {"intent": "unclear", "reply": "I couldn't process that. Try again?"}
            
        result = extract_json(response.text)
        return result if result else {"intent": "unclear", "reply": "I'm a bit confused, could you be more specific?"}
        
    except Exception as e:
        logger.error(f"AI Logic Error: {e}")
        # 🛡️ Fallback: If AI fails, try a simple keyword check so the bot keeps working
        if any(word in text.lower() for word in ["movie", "series", "watch", "download"]):
            return {"intent": "request", "title": text, "reply": "Got it! Checking for that..."}
        return {"intent": "chat", "reply": "I'm online, but my brain is a bit foggy. Try again in a second!"}

async def get_witty_rejection(title: str):
    try:
        r = await model.generate_content_async(f"Give a funny 1-sentence reason why we can't upload {title}")
        return r.text.strip()
    except:
        return f"Sorry, we can't fulfill the request for {title} right now."

async def get_admin_acceptance_msg(title: str):
    try:
        r = await model.generate_content_async(f"Give a high-energy 1-sentence hype message for the upload of {title}")
        return r.text.strip()
    except:
        return f"✅ {title} is now available! Enjoy!"
