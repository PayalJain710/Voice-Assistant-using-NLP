import pickle
from datetime import datetime

REMINDERS_FILE = 'reminders.pkl'

def add_reminder(reminder_text):
    reminders = load_reminders()
    reminders.append((reminder_text, datetime.now()))
    save_reminders(reminders)

def get_reminders():
    reminders = load_reminders()
    reminders_list = []
    for reminder, timestamp in reminders:
        reminders_list.append(f"{reminder} (set at {timestamp.strftime('%H:%M:%S on %d-%m-%Y')})")
    return reminders_list

def load_reminders():
    try:
        with open(REMINDERS_FILE, 'rb') as f:
            reminders = pickle.load(f)
    except (FileNotFoundError, EOFError):
        reminders = []
    return reminders

def save_reminders(reminders):
    with open(REMINDERS_FILE, 'wb') as f:
        pickle.dump(reminders, f)
