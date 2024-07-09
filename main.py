import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
import speech_recognition as sr
import pyttsx3
import spacy
import subprocess
import webbrowser
from pytube import Search
from datetime import datetime
from weather import get_weather
from news import get_news
from reminder import add_reminder, get_reminders
from search import google_search
import random
from bs4 import BeautifulSoup
# Initialize text-to-speech engine
tts_engine = pyttsx3.init()

# Set up the speech recognizer
recognizer = sr.Recognizer()

# Ensure the spaCy model is installed
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load('en_core_web_sm')

def speak(text):
    """Convert text to speech"""
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen():
    """Listen for user input and convert it to text"""
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            text = recognizer.recognize_google(audio)
            print(f"User said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            print("Sorry, my speech service is down.")
            return ""

def play_video(query):
    """Search for a YouTube video and play it in the default browser"""
    try:
        search_results = Search(query).results
        if search_results:
            first_result = search_results[0]
            webbrowser.open(first_result.watch_url)
            return f"Playing video: {first_result.title}"
        else:
            return "No video found for the given query."
    except Exception as e:
        return f"An error occurred while trying to play the video: {e}"

def get_today_date():
    """Get today's date in a readable format"""
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y")

def process_command(command):
    """Process the user's command using NLP"""
    doc = nlp(command)
    if any([token.lemma_ in ["hello", "hi"] for token in doc]):
        return "Hello! How can I assist you today?"
    elif any([token.lemma_ in ["bye", "goodbye"] for token in doc]):
        return "Goodbye! Have a great day!"
    elif any(token.text == "time" for token in doc):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        return f"The current time is {current_time}."
    elif any(token.text == "date" for token in doc):
        return f"Today's date is {get_today_date()}."
    elif any([token.lemma_ in ["play", "watch"] for token in doc]) and "video" in command:
        query = command.replace("play", "").replace("watch", "").replace("video", "").strip()
        if query:
            return play_video(query)
        else:
            return "Please provide a specific video to play."
    elif any(token.text == "weather" for token in doc):
        city = command.replace("weather", "").strip()
        if city:
            return get_weather(city)
        else:
            return "Please specify a city to check the weather."
    elif "news" in command:
        # Extract the limit from user command
        words = command.split()
        for i, word in enumerate(words):
            if word.isdigit():
                limit = int(word)
                break
        else:
            limit = 5  # Default limit if not specified

        # Fetch news with the specified limit
        speak(f"Fetching news with a limit of {limit} articles.")
        news_headlines = get_news(limit)
        speak(news_headlines)
        return news_headlines
    # Call get_news function from news.py
    doc = nlp(command)
    if "set reminder" in command:
        reminder_text = command.replace("set reminder", "").strip()
        if reminder_text:
            add_reminder(reminder_text)
            return f"Reminder '{reminder_text}' has been set."
        else:
            return "Please provide the text for the reminder."
    elif "reminders" in command:
        reminders_list = get_reminders()
        if reminders_list:
            return "Your reminders are:\n" + "\n".join(reminders_list)
        else:
            return "You have no reminders set."
    elif "search" in command:
        query = command.replace("search", "").strip()
        if query:
            speak(f"Searching Google for {query}.")
            result = google_search(query)
            speak(result)
            return result
        else:
            speak("Please provide a search query after saying 'search'.")
    elif any(token.lemma_ in ["mood", "feeling", "emotion"] for token in doc):
        # Ask about the user's mood
        return ask_mood()
    else:
        return "I'm not sure how to respond to that."
def ask_mood():
    """Ask the user about their mood and suggest an activity"""
    speak("How are you feeling today?")
    mood_response = listen()
    return suggest_activity_based_on_mood(mood_response)


def suggest_activity_based_on_mood(mood_response):
    """Suggest an activity based on the user's mood"""
    doc = nlp(mood_response)
    mood = None

    if any(token.lemma_ in ["happy", "joyful", "excited"] for token in doc):
        mood = "happy"
    elif any(token.lemma_ in ["sad", "down", "unhappy"] for token in doc):
        mood = "sad"
    elif any(token.lemma_ in ["stressed", "anxious", "nervous"] for token in doc):
        mood = "stressed"
    elif any(token.lemma_ in ["relaxed", "calm", "peaceful"] for token in doc):
        mood = "relaxed"

    suggestions = {
        "happy": [
            "How about listening to some upbeat music?",
            "Maybe watch a comedy video to keep the good mood going?",
            "You could share your happiness with a friend!"
        ],
        "sad": [
            "Would you like to listen to some soothing music?",
            "How about watching a motivational video to lift your spirits?",
            "Maybe a walk in nature would help you feel better."
        ],
        "stressed": [
            "Let's try some deep breathing exercises together.",
            "How about a relaxing video to calm your mind?",
            "Listening to calming music might help you unwind."
        ],
        "relaxed": [
            "How about some mellow music to keep you in a relaxed state?",
            "Would you like to watch a peaceful nature video?",
            "You could try a guided meditation to stay relaxed."
        ]
    }

    if mood in suggestions:
        suggestion = random.choice(suggestions[mood])
        speak(suggestion)
        return suggestion
    else:
        return "I'm not sure how to help with that mood, but I'm here to listen if you want to talk more."

class VoiceAssistantThread(QThread):
    text_output = pyqtSignal(str)

    def run(self):
        while True:
            command = listen()
            if command:
                response = process_command(command)
                self.text_output.emit(response)
                if "goodbye" in response.lower():
                    speak(response)
                    break
                speak(response)

class VoiceAssistantUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.voice_thread = VoiceAssistantThread()
        self.voice_thread.text_output.connect(self.update_text_output)

    def initUI(self):
        self.setWindowTitle("Voice Assistant")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.title_label = QLabel("Voice Assistant", self)
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.text_output = QTextEdit(self)
        self.text_output.setReadOnly(True)
        self.text_output.setStyleSheet("background-color: #f0f0f0; color: #333;")
        self.layout.addWidget(self.text_output)

        self.start_button = QPushButton("Start Assistant", self)
        self.start_button.setFont(QFont("Arial", 14))
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.start_button.clicked.connect(self.start_assistant)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Assistant", self)
        self.stop_button.setFont(QFont("Arial", 14))
        self.stop_button.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_button.clicked.connect(self.stop_assistant)
        self.layout.addWidget(self.stop_button)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QPushButton {
                height: 40px;
            }
        """)

    def start_assistant(self):
        self.voice_thread.start()

    def stop_assistant(self):
        self.voice_thread.terminate()

    def update_text_output(self, text):
        self.text_output.append(text)
def main():
    app = QApplication(sys.argv)
    mainWindow = VoiceAssistantUI()
    mainWindow.show()
    sys.exit(app.exec_())
    """Main loop for the voice assistant"""
    while True:
        command = listen()
        if command:
            response = process_command(command)
            if "goodbye" in response.lower():
                speak(response)
                break
            speak(response)

if __name__ == "__main__":
    main()
