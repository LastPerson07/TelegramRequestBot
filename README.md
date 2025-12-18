# 🤖 Telegram Request Acceptor Bot

A **smart Telegram Request Acceptor Bot** that understands **natural language requests** (even if users don’t explicitly say “request”), processes them intelligently, and forwards them to admins or a request channel for action.

This bot is **NOT an AutoFilter bot**.
It is designed specifically to **accept, analyze, and manage user requests** (movies, series, anime, files, etc.).

---

## ✨ Features

* 🧠 **AI-powered request understanding**

  * Understands messages like:

    * *“Interstellar movie”*
    * *“My girlfriend wants Titanic”*
    * *“Any good anime like Naruto?”*
  * No need for users to type `/request`

* 📩 **Automatic request detection**

  * Identifies whether a message is a request or casual chat
  * Ignores spam / non-relevant messages

* 📨 **Admin / Channel forwarding**

  * Forwards clean, formatted requests to:

    * Admins
    * Request group
    * Request channel

* 🔄 **Interactive UI**

  * Modern `/start` menu
  * Back button navigation
  * Inline keyboard support

* 🛡 **Admin controls**

  * Accept / Reject requests
  * Reply directly to users
  * Log all actions

* 🎨 **Terminal startup banner**

  * Clean ASCII banner on bot startup
  * Shows bot status & loaded modules

* ⚙️ **Environment-based configuration**

  * Easy `.env` setup
  * Secure token handling

---

## 🚀 How It Works

1. User sends **any message**
2. AI analyzes intent:

   * Is it a request?
   * What is being requested?
3. Bot formats the request
4. Request is sent to admins / request channel
5. Admin responds or fulfills request

---

## 📂 Project Structure

```
telegram-request-acceptor/
│
├── bot.py
├── handlers/
│   ├── start.py
│   ├── request_handler.py
│   ├── admin.py
│
├── utils/
│   ├── ai_parser.py
│   ├── keyboards.py
│   ├── logger.py
│
├── .env
├── requirements.txt
└── README.md
```

---

## 🛠 Requirements

* Python **3.9+**
* Telegram Bot Token
* Telegram **API_ID** & **API_HASH**
* (Optional) Google Gemini API / OpenAI API for AI understanding

---

## 📦 Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/telegram-request-acceptor.git
cd telegram-request-acceptor
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables (`.env`)

```env
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id
API_HASH=your_api_hash

BOT_OWNER_ID=123456789
ADMIN_CHAT_ID=-100xxxxxxxxxx

REQUEST_CHANNEL_ID=-100xxxxxxxxxx
LOG_CHANNEL_ID=-100xxxxxxxxxx

AI_PROVIDER=gemini
GEMINI_API_KEY=your_google_api_key
```

---

## ▶️ Run the Bot

```bash
python bot.py
```

You should see a **terminal banner** like:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TELEGRAM REQUEST BOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status  : Online
AI      : Enabled
Modules : Loaded
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🧠 AI Message Understanding

The bot can detect requests even when:

* No `/request` command is used
* Message is indirect
* Slang or broken English is used

Example messages it understands:

* `Interstellar 2014`
* `bro any south movie`
* `my gf wants romantic movie`
* `anime like one piece`

---

## 🎯 Use Case

Perfect for:

* Movie request groups
* Streaming communities
* Anime & series channels
* File request bots
* Premium content communities

---

## 🔒 Privacy & Safety

* No messages are stored permanently
* API keys are loaded securely
* Admin-only commands protected

---

## 📜 License

MIT License
Free to use, modify, and distribute.

---

## 👤 Author

**Dhanpal Sharma**
📧 [sharmadhanpal950@gmail.com](mailto:sharmadhanpal950@gmail.com)
🌐 GitHub: [https://github.com/LastPerson07](https://github.com/LastPerson07)
