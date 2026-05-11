import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import requests
import time
import logging
import os
import random

# ---------------- LOGGING ----------------
logging.basicConfig(filename="assistant.log", level=logging.INFO)

# ---------------- VOICE ENGINE ----------------
engine = pyttsx3.init('sapi5')

def speak(text):
    logging.info(f"Assistant: {text}")
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# ---------------- TAKE COMMAND ----------------
def take_command():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.energy_threshold = 300
        r.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = r.listen(source, timeout=8, phrase_time_limit=6)
        except:
            return ""

    try:
        print("Recognizing...")
        command = r.recognize_google(audio, language='en-IN')
        print("You said:", command)
        return command.lower()

    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""

    except sr.RequestError:
        speak("Internet connection issue")
        return ""

# ---------------- WEATHER ----------------
def get_weather(city):
    api_key = "REDACTED_REMOVED_KEY"

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()

        if data["cod"] != 200:
            speak("City not found")
            return

        temp = data["main"]["temp"]
        weather = data["weather"][0]["main"]

        speak(f"The temperature in {city} is {temp} degree Celsius with {weather}")

    except:
        speak("Unable to fetch weather. Check your internet.")

# ---------------- MAIN ASSISTANT ----------------
def run_assistant():
    print("\n--- Voice Assistant Running ---\n")
    speak("Say Hey Suzy to activate me")

    wake_words = ["suzy", "suji"]

    while True:
        command = take_command()

        if command == "":
            continue

        # EXIT ANYTIME
        if "exit" in command or "quit" in command:
            speak("Shutting down. Goodbye!")
            break

        # WAKE WORD
        if "hey" in command and any(word in command for word in wake_words):
            speak("I'm listening")

            attempts = 0

            while True:
                command = take_command()

                # ❌ NO INPUT
                if command == "":
                    attempts += 1

                    if attempts >= 3:
                        speak("No response detected. Going to sleep.")
                        speak("Say Hey Suzy to activate me again")
                        break   # go back to outer loop

                    continue

                # ✅ RESET attempts when user speaks
                attempts = 0

                # STOP COMMAND
                if any(word in command for word in ["stop", "sleep"]):
                    speak("Going to sleep")
                    speak("Say Hey Suzy to activate me again")
                    break

                # TIME
                elif "time" in command:
                    now = datetime.datetime.now().strftime("%I:%M %p")
                    responses = [
                        f"The time is {now}",
                        f"It's {now} right now",
                        f"Current time is {now}"
                    ]
                    speak(random.choice(responses))

                # DATE
                elif "date" in command:
                    today = datetime.datetime.now().strftime("%d %B %Y")
                    speak(f"Today's date is {today}")

                # GOOGLE
                elif "google" in command:
                    speak("Opening Google")
                    webbrowser.open("https://www.google.com")

                # YOUTUBE
                elif "youtube" in command:
                    speak("Opening YouTube")
                    webbrowser.open("https://www.youtube.com")

                # SEARCH
                elif "search" in command:
                    speak("What should I search?")
                    query = take_command()
                    if query:
                        webbrowser.open(f"https://www.google.com/search?q={query}")
                        speak("Here are the results")

                # WEATHER
                elif any(word in command for word in ["weather", "whether", "temperature", "climate"]):
                    speak("Which city?")
                    city = take_command()
                    if city:
                        get_weather(city)
                    else:
                        speak("City not detected")

                # OPEN APPS
                elif "notepad" in command:
                    speak("Opening Notepad")
                    os.system("notepad")

                elif "calculator" in command:
                    speak("Opening Calculator")
                    os.system("calc")

                # HELP
                elif "help" in command:
                    speak("You can ask time, date, weather, open apps or search Google")

                # UNKNOWN
                else:
                    speak("Sorry, I didn't understand. Please try again.")

                time.sleep(1)

# ---------------- RUN ----------------
run_assistant()