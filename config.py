import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "0"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DATA_FILE = "bot_data.json"
DEFAULT_DEADLINE_HOURS = 12

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RequestBot")


def load_deadline(bot_data):
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                bot_data.update(json.load(f))
        except Exception as e:
            logger.error(e)
    bot_data.setdefault("deadline_hours", DEFAULT_DEADLINE_HOURS)


def save_deadline(bot_data):
    with open(DATA_FILE, "w") as f:
        json.dump({"deadline_hours": bot_data["deadline_hours"]}, f)