import sounddevice as sd
import pyttsx3
import os
import datetime
import subprocess
import requests
import spacy
import langdetect
import whisper
import numpy as np
import openai
from bs4 import BeautifulSoup
from googlesearch import search as googlesearch_query
import tkinter as tk
from tkinter import scrolledtext
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pytesseract
from PIL import Image
import cv2
import yfinance as yf

engine = pyttsx3.init()
# select female voice (Zira) on Windows
voices = engine.getProperty('voices')
if len(voices) > 1:  # Assuming Zira is the second voice
    engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 170)

# PyAutoGUI settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

# Selenium setup
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("detach", True)  # Keep browser open
driver = None

# Pytesseract setup (assuming tesseract is installed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust path if needed

nlp = spacy.load("en_core_web_sm")
model = whisper.load_model("base")

print("sounddevice available devices:")
try:
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"{idx}: {dev['name']} (input)")
    print("Default device:", sd.default.device)
    sd.default.device = (1, 3)  # input=Microphone Array, output=Speaker
    print("Set sd.default.device to", sd.default.device)
except Exception as e:
    print("Could not query sounddevice devices:", e)

# Simple command DB for learned phrases
import sqlite3
conn = sqlite3.connect("command_memory.db")
cursor = conn.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS command_memory (id INTEGER PRIMARY KEY, trigger TEXT UNIQUE, response TEXT)"""
)
conn.commit()

# GUI interface
root = None
chat_box = None
user_mode = "command"  # default mode: command-based
connectivity_mode = "auto"  # auto, online, offline

def setup_ui():
    global root, chat_box
    root = tk.Tk()
    root.title("Tommy AI Interface")
    root.geometry("700x520")
    title = tk.Label(root, text="Tommy Chatbot", font=("Arial", 18, "bold"), fg="#2E8B57")
    title.pack(pady=8)

    chat_box = scrolledtext.ScrolledText(root, state="disabled", wrap="word", font=("Arial", 11))
    chat_box.pack(fill="both", expand=True, padx=10, pady=5)

    # Input area and buttons
    input_frame = tk.Frame(root)
    input_frame.pack(fill="x", padx=10, pady=4)

    command_entry = tk.Entry(input_frame, font=("Arial", 11))
    command_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))

    def send_text_command():
        user_cmd = command_entry.get().strip().lower()
        if not user_cmd:
            return
        add_to_interface("User", user_cmd)
        command_entry.delete(0, tk.END)
        if "exit" in user_cmd or "quit" in user_cmd:
            speak("Goodbye!")
            root.quit()
            return
        process_command(user_cmd)

    send_button = tk.Button(input_frame, text="Send", command=send_text_command, bg="#4CAF50", fg="white", padx=10)
    send_button.pack(side="left", padx=2)

    text_button = tk.Button(input_frame, text="Text", command=send_text_command, bg="#FFA500", fg="white", padx=10)
    text_button.pack(side="left", padx=2)

    voice_button = tk.Button(input_frame, text="Voice", command=lambda: on_voice_button(), bg="#007ACC", fg="white", padx=10)
    voice_button.pack(side="left", padx=2)

    status_frame = tk.Frame(root)
    status_frame.pack(fill="x", padx=10, pady=2)
    status_label = tk.Label(status_frame, text="Mode: Unknown", font=("Arial", 10, "italic"), fg="#555")
    status_label.pack(side="left")

    mode_frame = tk.Frame(root)
    mode_frame.pack(fill="x", padx=10, pady=2)
    conversation_mode_btn = tk.Button(mode_frame, text="Conversation Mode", bg="#6A5ACD", fg="white", padx=8, command=lambda: set_mode("conversation"))
    conversation_mode_btn.pack(side="left", padx=2)
    command_mode_btn = tk.Button(mode_frame, text="Command Mode", bg="#20B2AA", fg="white", padx=8, command=lambda: set_mode("command"))
    command_mode_btn.pack(side="left", padx=2)

    connectivity_frame = tk.Frame(root)
    connectivity_frame.pack(fill="x", padx=10, pady=2)
    online_btn = tk.Button(connectivity_frame, text="Online Mode", bg="#FF6347", fg="white", padx=8, command=lambda: set_connectivity("online"))
    online_btn.pack(side="left", padx=2)
    offline_btn = tk.Button(connectivity_frame, text="Offline Mode", bg="#4169E1", fg="white", padx=8, command=lambda: set_connectivity("offline"))
    offline_btn.pack(side="left", padx=2)
    auto_btn = tk.Button(connectivity_frame, text="Auto Mode", bg="#32CD32", fg="white", padx=8, command=lambda: set_connectivity("auto"))
    auto_btn.pack(side="left", padx=2)

    button_frame = tk.Frame(root)
    button_frame.pack(fill="x", padx=10, pady=4)

    quick_actions = [
        ("Time", lambda: process_command("time")),
        ("Notepad", lambda: process_command("open notepad")),
        ("Calculator", lambda: process_command("open calculator")),
        ("Compare", lambda: process_command("compare best")),
    ]
    for caption, action in quick_actions:
        btn = tk.Button(button_frame, text=caption, command=action, bg="#565656", fg="white", padx=10, pady=5)
        btn.pack(side="left", padx=4, pady=2)

    root.command_entry = command_entry
    root.status_label = status_label

    return root


def add_to_interface(sender, text):
    if chat_box is None:
        return
    chat_box.config(state="normal")
    if sender == "User":
        chat_box.insert(tk.END, f"{sender}: {text}\n", "user")
    else:
        chat_box.insert(tk.END, f"{sender}: {text}\n", "assistant")
    chat_box.tag_config("user", foreground="#1E90FF")
    chat_box.tag_config("assistant", foreground="#8B008B")
    chat_box.config(state="disabled")
    chat_box.yview(tk.END)

def speak(text):
    if chat_box is not None:
        add_to_interface("Tommy", text)
    engine.say(text)
    engine.runAndWait()


def on_voice_button():
    try:
        # prevent hanging UI: run listen in background thread
        def listen_and_process():
            command = listen()
            if command and command not in ["", None]:
                if "exit" in command or "quit" in command:
                    speak("Goodbye!")
                    if root:
                        root.quit()
                    return
                process_command(command)
        import threading
        threading.Thread(target=listen_and_process, daemon=True).start()
    except Exception as e:
        print("Voice button error:", e)
        speak("Unable to process voice command right now.")


def listen():
    # Primary path: direct microphone capture via sounddevice + Whisper
    for attempt in range(2):
        try:
            duration = 3  # faster response
            samplerate = 16000
            speak("Listening for your command.")
            recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="int16")
            sd.wait()
            audio_array = recording.flatten().astype(np.float32) / 32768.0
            result = model.transcribe(audio_array, language=None, fp16=False, verbose=False)
            command = result.get("text", "").strip().lower()
            if command:
                print("You said: " + command)
                add_to_interface("User", command)
                if "tommy" in command:
                    command = command.replace("tommy", "").strip()
                return command
            else:
                speak("I did not catch that. Please speak again.")
        except Exception as ex:
            print(f"Attempt {attempt+1} speech capture error: {ex}")
            if attempt == 0:
                speak("Retrying voice capture.")
            else:
                speak("Voice capture unavailable, please type your command.")

    command = input("You (type command): ").strip().lower()
    print("You said: " + command)
    add_to_interface("User", command)
    if "tommy" in command:
        command = command.replace("tommy", "").strip()
    return command


def lookup_learned_command(command):
    cursor.execute("SELECT response FROM command_memory WHERE trigger = ?", (command,))
    row = cursor.fetchone()
    return row[0] if row else None


def google_search(query, limit=3):
    results = []
    try:
        for url in googlesearch_query(query, num_results=limit):
            results.append(url)
    except Exception as e:
        print("Google search error:", e)
    return results


conversation_history = [
    {"role": "system", "content": "You are a helpful AI assistant that can answer questions conversationally, run automation commands, and persist context for follow-up interactions."}
]


def gpt_search(query):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OpenAI API key not set (OPENAI_API_KEY)."
    openai.api_key = api_key
    try:
        prompt = f"Summarize briefly the best answer for this question: {query}"
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT search error: {e}"


def gpt_chat(user_message):
    # Respect connectivity mode setting
    if connectivity_mode == "offline":
        return None  # Force offline mode to use spaCy
    
    if connectivity_mode == "auto" and not is_internet_available():
        return None  # No internet in auto mode, use spaCy fallback
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OpenAI API key not set. Set OPENAI_API_KEY to enable conversational mode."

    openai.api_key = api_key
    conversation_history.append({"role": "user", "content": user_message})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=conversation_history,
            max_tokens=350,
            temperature=0.8,
        )
        assistant_text = response.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": assistant_text})
        return assistant_text
    except Exception as e:
        return f"GPT conversational error: {e}"


def is_internet_available():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except Exception:
        return False


def set_mode(mode):
    global user_mode
    user_mode = mode
    update_ui_mode()
    speak(f"Switched to {mode} mode")


def set_connectivity(mode):
    global connectivity_mode
    connectivity_mode = mode
    update_ui_mode()
    speak(f"Switched to {mode} connectivity mode")


def update_ui_mode():
    if root is None or not hasattr(root, 'status_label'):
        return
    # Build status string showing both user mode and connectivity mode
    mode_str = f"User: {user_mode.capitalize()} | Connectivity: {connectivity_mode.capitalize()}"
    
    # Update color based on network/API status
    if is_internet_available() and os.getenv("OPENAI_API_KEY"):
        root.status_label.config(text=mode_str + " | Online (OpenAI)", fg="#0A7D00")
    elif is_internet_available():
        root.status_label.config(text=mode_str + " | Online (No API)", fg="#A64700")
    else:
        root.status_label.config(text=mode_str + " | Offline (spaCy)", fg="#0074B8")


def spacy_chat(user_message):
    doc = nlp(user_message)
    lower_text = user_message.lower()

    if any(tok.lemma_.lower() in ["joke", "funny"] for tok in doc):
        return "Why did the robot cross the road? Because it was programmed by the chicken!"
    if any(tok.lemma_.lower() in ["hello", "hi", "hey"] for tok in doc):
        return "Hi there! I'm Tommy, your offline-capable assistant. How can I help?"
    if any(tok.lemma_.lower() in ["time", "clock"] for tok in doc):
        return f"The time is {datetime.datetime.now().strftime('%H:%M')}"
    if any(tok.lemma_.lower() in ["date", "day"] for tok in doc):
        return f"Today's date is {datetime.datetime.now().strftime('%Y-%m-%d')}"
    if "weather" in lower_text:
        return "I can't fetch live weather without internet, but you can ask when online."
    if "stock" in lower_text or "bitcoin" in lower_text or "crypto" in lower_text:
        return "Offline mode can't pull market prices. Please connect internet for live financial data."

    # Simple entity-based fallback
    entities = [ent.text for ent in doc.ents]
    if entities:
        return f"You asked about {', '.join(entities)}. I can provide more when online."

    return None


def compare_search(query):
    speak("Searching Google and ChatGPT, please wait...")
    google_results = google_search(query, limit=5)
    gpt_results = gpt_search(query)

    report = "--- Google Top URLs ---\n"
    if google_results:
        for idx, url in enumerate(google_results, start=1):
            report += f"{idx}. {url}\n"
    else:
        report += "No Google results available.\n"

    report += "\n--- ChatGPT Summary ---\n"
    report += gpt_results + "\n"

    report += "\n--- Recommendation ---\n"
    if google_results and "OpenAI API key" not in gpt_results:
        report += "Use ChatGPT summary for quick understanding, and follow Google links for deep details."
    else:
        report += "Use whatever result is available."  

    return report


def take_screenshot(filename="screenshot.png"):
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    return filename


def analyze_screenshot(filename="screenshot.png"):
    img = cv2.imread(filename)
    text = pytesseract.image_to_string(img)
    return text


def control_mouse(command):
    if "move to" in command:
        parts = command.split("move to")
        if len(parts) > 1:
            coords = parts[1].strip().split()
            if len(coords) == 2:
                try:
                    x, y = int(coords[0]), int(coords[1])
                    pyautogui.moveTo(x, y)
                    speak(f"Moved mouse to {x}, {y}")
                except ValueError:
                    speak("Invalid coordinates")
    elif "click" in command:
        pyautogui.click()
        speak("Clicked")
    elif "right click" in command:
        pyautogui.rightClick()
        speak("Right clicked")
    elif "double click" in command:
        pyautogui.doubleClick()
        speak("Double clicked")


def control_keyboard(command):
    if "type" in command:
        text = command.replace("type", "").strip()
        pyautogui.typewrite(text)
        speak(f"Typed: {text}")
    elif "press" in command:
        key = command.replace("press", "").strip()
        pyautogui.press(key)
        speak(f"Pressed {key}")


def auto_fill_form(data):
    # Simple auto fill, assuming focused on form
    for field, value in data.items():
        pyautogui.typewrite(value)
        pyautogui.press('tab')
    speak("Form filled")


def send_whatsapp_message(number, message):
    global driver
    if driver is None:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://web.whatsapp.com/")
    speak("Please scan QR code if prompted")
    time.sleep(10)  # Wait for login
    try:
        search_box = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
        search_box.click()
        search_box.send_keys(number + Keys.ENTER)
        time.sleep(2)
        message_box = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
        message_box.send_keys(message + Keys.ENTER)
        speak(f"Sent message to {number}")
    except Exception as e:
        speak(f"Error sending WhatsApp message: {str(e)}")


def get_weather(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "OpenWeather API key not set. Please set OPENWEATHER_API_KEY environment variable."
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            return f"Weather in {city}: {temp}°C, {desc}"
        else:
            return "Weather data not available"
    except Exception as e:
        return f"Weather API error: {str(e)}"


def get_news():
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        return "NewsAPI key not set. Please set NEWSAPI_KEY environment variable."
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            articles = data['articles'][:3]  # Top 3
            news = "Latest news:\n"
            for article in articles:
                news += f"- {article['title']}\n"
            return news
        else:
            return "News not available"
    except Exception as e:
        return f"News API error: {str(e)}"


def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return f"{symbol.upper()} price: ${price:.2f}"
    except Exception as e:
        return f"Stock data not available for {symbol}"


def get_crypto_price(crypto):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        if crypto in data:
            price = data[crypto]['usd']
            return f"{crypto.capitalize()} price: ${price}"
        else:
            return f"Crypto data not available for {crypto}"
    except Exception as e:
        return f"Crypto API error: {str(e)}"


def learn_command(trigger, response):
    cursor.execute(
        "INSERT INTO command_memory(trigger,response) VALUES (?, ?) ON CONFLICT(trigger) DO UPDATE SET response=excluded.response",
        (trigger, response),
    )
    conn.commit()


def process_command(command):
    global user_mode

    if "switch to conversation mode" in command or "conversation mode" in command:
        set_mode("conversation")
        return
    if "switch to command mode" in command or "command mode" in command:
        set_mode("command")
        return

    learned = lookup_learned_command(command)
    if learned:
        speak(learned)
        return

    # In conversation mode, delegate to GPT/spacy fallback for general text
    if user_mode == "conversation":
        # Try GPT first if internet is available
        if connectivity_mode != "offline" and is_internet_available() and os.getenv("OPENAI_API_KEY"):
            gpt_response = gpt_chat(command)
            if gpt_response and not gpt_response.startswith("GPT conversational error"):
                speak(gpt_response)
                return
        # Fallback to offline spaCy response
        offline_response = spacy_chat(command)
        if offline_response:
            speak(offline_response)
            return
        # Final fallback message
        speak("I couldn't answer that directly in conversation mode. Try command mode for system operations.")
        return

    doc = nlp(command)
    if command.startswith("learn ") or command.startswith("train "):
        speak("Please type the phrase I should learn.")
        trigger = input("Trigger phrase: ").strip().lower()
        speak("Please type the response to return.")
        response = input("Response: ").strip()
        if trigger and response:
            learn_command(trigger, response)
            speak(f"Learned command '{trigger}'.")
        else:
            speak("Unable to learn empty trigger or response.")
        return

    # Multilingual command matching (English, Hindi, Bengali)
    if any(word in command for word in ["time", "samay", "সময়", "घड़ी", "घडी"]):
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
    elif any(word in command for word in ["open notepad", "notepad kholo", "নোটপ্যাড খুলো", "নোটপ্যাড" , "नोटपैड"]):
        subprocess.run(["notepad"])
        speak("Opening Notepad")
    elif any(word in command for word in ["open calculator", "calculator kholo", "ক্যালকুলেটর খুলো", "कैलकुलेटर"]):
        subprocess.run(["calc"])
        speak("Opening Calculator")
    elif any(word in command for word in ["compare", "best", "comparison"]):
        query = command
        for token in ["compare", "best", "comparison", "search", "talash", "খুঁজুন", "Khoj", "खोज"]:
            query = query.replace(token, "")
        query = query.strip()
        if query:
            result = compare_search(query)
            print(result)
            speak("Comparison complete. Check the console for details.")
        else:
            speak("What do you want to compare?")
    elif any(word in command for word in ["search", "talash", "খুঁজুন", "Khoj", "खोज"]):
        query = command
        for token in ["search", "talash", "খুঁজুন", "Khoj", "खोज"]:
            query = query.replace(token, "")
        query = query.strip()
        if query:
            os.system(f"start https://www.google.com/search?q={query}")
            speak(f"Searching for {query}")
        else:
            speak("What do you want to search for?")
    elif any(word in command for word in ["play music", "music bajao", "গান চালাও", "म्यूजिक चलाओ"]):
        os.system("start C:\\Users\\YourUser\\Music")
        speak("Playing music")
    elif command.startswith("start ") or command.startswith("open "):
        target = command.replace("start", "").replace("open", "").strip()
        if "notepad" in target or "notepad" in command or "নোটপ্যাড" in command or "नोटपैड" in command:
            subprocess.run(["notepad"])
            speak("Opening Notepad")
        elif "calculator" in target or "calculator" in command or "ক্যালকুলেটর" in command or "कैलकुलेटर" in command:
            subprocess.run(["calc"])
            speak("Opening Calculator")
        else:
            speak(f"Attempting to start {target}")
            os.system(f"start {target}")
    elif "shutdown" in command:
        speak("Shutting down the system")
        os.system("shutdown /s /t 1")
    elif "restart" in command:
        speak("Restarting the system")
        os.system("shutdown /r /t 1")
    elif "weather" in command:
        city = command.replace("weather", "").replace("in", "").strip()
        if city:
            result = get_weather(city)
            speak(result)
        else:
            speak("Please specify a city for weather")
    elif "news" in command:
        result = get_news()
        speak(result[:200])  # Limit for speech
    elif "stock" in command and "price" in command:
        symbol = command.split("of")[-1].strip().upper()
        if symbol:
            result = get_stock_price(symbol)
            speak(result)
        else:
            speak("Please specify a stock symbol")
    elif any(word in command for word in ["bitcoin", "crypto", "cryptocurrency"]):
        if "bitcoin" in command:
            crypto = "bitcoin"
        else:
            # Extract crypto name, assume last word
            words = command.split()
            crypto = words[-1].lower()
        result = get_crypto_price(crypto)
        speak(result)
    elif "mouse" in command:
        control_mouse(command)
    elif "keyboard" in command or "type" in command:
        control_keyboard(command)
    elif "fill form" in command:
        # Example data, can be customized
        data = {"name": "John Doe", "email": "john@example.com", "phone": "1234567890"}
        auto_fill_form(data)
    elif "whatsapp" in command and "send" in command:
        # Parse "send whatsapp to 1234567890 message hello"
        parts = command.split("to")
        if len(parts) > 1:
            number_part = parts[1].split("message")
            if len(number_part) == 2:
                number = number_part[0].strip()
                message = number_part[1].strip()
                send_whatsapp_message(number, message)
            else:
                speak("Please specify number and message")
        else:
            speak("Please specify recipient")
    elif "screenshot" in command:
        if "analyze" in command:
            filename = take_screenshot()
            text = analyze_screenshot(filename)
            speak(f"Analyzed text: {text[:200]}...")  # Limit for speech
        else:
            filename = take_screenshot()
            speak(f"Screenshot saved as {filename}")
    else:
        # Conversational fallback: hybrid offline/online
        gpt_response = None
        if os.getenv("OPENAI_API_KEY") and is_internet_available():
            gpt_response = gpt_chat(command)

        if gpt_response and not (gpt_response.startswith("GPT conversational error") or gpt_response.startswith("OpenAI API key not set")):
            speak(gpt_response)
            return

        offline_fallback = spacy_chat(command)
        if offline_fallback:
            speak(offline_fallback)
            return

        if not is_internet_available():
            speak("No internet right now. I can answer small local questions or run commands, otherwise connect for full AI results.")
        else:
            speak("I couldn't understand that locally. Searching Google now.")
            os.system(f"start https://www.google.com/search?q={command}")

def main():
    root = setup_ui()
    root.geometry("900x700")
    speak("Hello, I am Tommy. I can understand speech in multiple languages and control your system. How can I help you?")
    add_to_interface("Tommy", "Hello! I am Tommy. Use Send/Text/Voice buttons and toggle Conversation/Command mode.")

    def on_close():
        speak("Goodbye!")
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    update_ui_mode()
    root.mainloop()

if __name__ == "__main__":
    main()