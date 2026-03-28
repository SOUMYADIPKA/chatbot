# Tommy-like AI Chatbot

This is an advanced AI chatbot inspired by Jarvis from Iron Man. It uses speech recognition with Whisper (supports multiple languages), NLP with spaCy, and can control your laptop system and access the internet.

## Features
- Speech recognition in multiple languages (auto-detected)
- Text-to-speech responses with female voice (Zira)
- NLP for command understanding
- System control: open apps, shutdown, restart
- Internet access: web search, AI-powered search comparison
- Smart screen automation: mouse/keyboard control, auto form filling, WhatsApp messaging, screenshot with OCR analysis
- Real-time data: weather, news, stock prices, cryptocurrency prices
- Offline hybrid mode: local spaCy NLP for offline requests, OpenAI for online natural conversations
- GUI interface with chat display and controls (Send, Text, Voice, Conversation/Command Mode)
- Database learning for custom commands
- Multilingual support (English, Hindi, Bengali)

## Requirements
- Python 3.14
- Microphone
- Internet for speech recognition and searches

## Installation
1. Install dependencies: `pip install speechrecognition pyttsx3 spacy langdetect requests torch openai-whisper numpy pyautogui selenium webdriver-manager pytesseract opencv-python pillow yfinance`
2. Download spaCy model: `python -m spacy download en_core_web_sm`
3. Install Tesseract OCR: Download from https://github.com/UB-Mannheim/tesseract/wiki and add to PATH
4. Set API keys as environment variables:
   - `OPENWEATHER_API_KEY` (OpenWeather)
   - `NEWSAPI_KEY` (NewsAPI)
   - `OPENAI_API_KEY` (OpenAI for conversational fallback)
5. Run: `"c:/Users/Sanjib Karan/OneDrive/Documents/Documents/Custom Office Templates/Desktop/chatbot/.venv/Scripts/python.exe" main.py`

## Usage
- Speak commands in English, Hindi and Bengali:
  - English: "What is the time?", "Open Calculator", "Search for Python", "Shutdown", "Move mouse to 100 200", "Click", "Type hello world", "Fill form", "Send WhatsApp to 1234567890 message Hello", "Take screenshot", "Analyze screenshot", "Weather in London", "Latest news", "Stock price of AAPL", "What's Bitcoin price?", "Tell me a joke"
  - Hindi: "समय बताओ", "नोटपैड खोलो", "कैलकुलेटर खोलो", "खोजो"
  - Bengali: "সময় বলো", "নোটপ্যাড খুলো", "ক্যালকুলেটর খুলো", "অনুসন্ধান করুন"
- UI mode buttons:
  - use **Conversation Mode** for natural AI chat (GPT/spaCy fallback)
  - use **Command Mode** for deterministic system operations
  - you can also say "switch to conversation mode" or "switch to command mode"
- Say "Exit" to quit.

## Note
For system commands, ensure permissions. For advanced AI, it searches unknown queries via conversational fallback using OpenAI.