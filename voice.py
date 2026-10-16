"""
Desktop CLI Voice Assistant - Suzzy
Run this file directly for desktop local microphone and speaker interaction.
For the Web/Cloud version, run: streamlit run app.py
"""

import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import requests
import time
import logging
import os
import random
import re
from assistant_core import process_command, DEFAULT_WEATHER_KEY

# ---------------- LOGGING ----------------
logging.basicConfig(filename="assistant.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# ---------------- VOICE ENGINE ----------------
try:
    engine = pyttsx3.init('sapi5')
except Exception:
    try:
        engine = pyttsx3.init()
    except Exception:
        engine = None

def speak(text):
    logging.info(f"Assistant: {text}")
    print("\n🤖 Assistant:", text)
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[Speech Output Error: {e}]")

# ---------------- TAKE COMMAND ----------------
def take_command():
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("\n🎙️ Listening...")
            r.pause_threshold = 1
            r.energy_threshold = 300
            r.adjust_for_ambient_noise(source, duration=1)

            try:
                audio = r.listen(source, timeout=8, phrase_time_limit=7)
            except sr.WaitTimeoutError:
                return ""
            except Exception as e:
                return ""

        print("⚡ Recognizing...")
        command = r.recognize_google(audio, language='en-IN')
        print("🗣️ You said:", command)
        return command.lower()

    except sr.UnknownValueError:
        print("⚠️ Could not understand audio")
        return ""
    except sr.RequestError:
        speak("Internet connection issue. Please check your network.")
        return ""
    except Exception as e:
        print(f"⚠️ Microphone error: {e}")
        return ""

# ---------------- MAIN DESKTOP ASSISTANT ----------------
def run_assistant():
    print("=" * 55)
    print("🎙️  SUZZY AI DESKTOP VOICE ASSISTANT")
    print("Commands: 'Open WhatsApp', 'Open YouTube', 'What is the time', etc.")
    print("Say 'Hey Suzy' or 'Hey Suzzy' to activate, or 'exit' to quit.")
    print("=" * 55)

    speak("Say Hey Suzy to activate me")

    wake_words = ["suzy", "suzzy", "suji"]

    while True:
        command = take_command()

        if command == "":
            continue

        # EXIT ANYTIME
        if any(w in command for w in ["exit", "quit", "shutdown"]):
            speak("Shutting down. Goodbye!")
            break

        # WAKE WORD DETECTION
        if any(word in command for word in wake_words) or command.startswith("hey"):
            speak("I am listening. How can I help you?")

            attempts = 0

            while True:
                command = take_command()

                if command == "":
                    attempts += 1
                    if attempts >= 3:
                        speak("No response detected. Going to sleep.")
                        speak("Say Hey Suzy to activate me again.")
                        break
                    continue

                attempts = 0

                # SLEEP OR STOP
                if any(word in command for word in ["stop", "sleep", "pause"]):
                    speak("Going to sleep. Say Hey Suzy to activate me again.")
                    break

                # EXIT
                if any(word in command for word in ["exit", "quit", "goodbye"]):
                    speak("Goodbye! Have a great day!")
                    return

                # DESKTOP SPECIFIC APPS
                if "notepad" in command:
                    speak("Opening Notepad")
                    os.system("notepad")
                elif "calculator" in command:
                    speak("Opening Calculator")
                    os.system("calc")
                else:
                    # Execute through Core Engine
                    result = process_command(command)
                    speak(result["speech_response"])

                    # If URL action, open in default browser
                    if result.get("url"):
                        try:
                            webbrowser.open(result["url"])
                        except Exception as e:
                            print(f"Could not open browser: {e}")

                time.sleep(0.5)

if __name__ == "__main__":
    run_assistant()