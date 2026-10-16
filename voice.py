"""
Dual-Mode Voice Assistant - Suzzy
- Runs as a Web AI Voice Assistant when launched in Streamlit (or deployed to Streamlit Cloud).
- Runs as a Desktop CLI Assistant when launched in terminal via `python voice.py`.
"""

import os
import sys

def is_running_in_streamlit() -> bool:
    """Detects whether the file is being executed within a Streamlit process."""
    # 1. Streamlit Cloud container path
    if any("mount" in str(arg).lower() for arg in sys.argv):
        return True
    # 2. Executed via `streamlit run voice.py`
    if any("streamlit" in str(arg).lower() for arg in sys.argv):
        return True
    # 3. Streamlit environment variables
    for key in os.environ:
        if key.startswith("STREAMLIT_"):
            return True
    # 4. Streamlit script execution context
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx() is not None:
            return True
    except Exception:
        pass
    # 5. Check if streamlit is imported by the parent runner
    if "streamlit" in sys.modules:
        return True
    return False

if is_running_in_streamlit():
    # Execute the Streamlit web application on every rerun
    import app
    app.main()
else:
    # ---------------- DESKTOP CLI ASSISTANT MODE ----------------
    import datetime
    import webbrowser
    import requests
    import time
    import logging
    import random
    import re
    from assistant_core import process_command, DEFAULT_WEATHER_KEY

    logging.basicConfig(filename="assistant.log", level=logging.INFO, format="%(asctime)s - %(message)s")

    # Speech output engine
    try:
        import pyttsx3
        try:
            engine = pyttsx3.init('sapi5')
        except Exception:
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

    def take_command():
        try:
            import speech_recognition as sr
        except ImportError:
            print("SpeechRecognition not installed. Run: pip install SpeechRecognition")
            return ""

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
                except Exception:
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

            if any(w in command for w in ["exit", "quit", "shutdown"]):
                speak("Shutting down. Goodbye!")
                break

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

                    if any(word in command for word in ["stop", "sleep", "pause"]):
                        speak("Going to sleep. Say Hey Suzy to activate me again.")
                        break

                    if any(word in command for word in ["exit", "quit", "goodbye"]):
                        speak("Goodbye! Have a great day!")
                        return

                    if "notepad" in command:
                        speak("Opening Notepad")
                        os.system("notepad")
                    elif "calculator" in command:
                        speak("Opening Calculator")
                        os.system("calc")
                    else:
                        result = process_command(command)
                        speak(result["speech_response"])
                        if result.get("url"):
                            try:
                                webbrowser.open(result["url"])
                            except Exception as e:
                                print(f"Could not open browser: {e}")

                    time.sleep(0.5)

    if __name__ == "__main__":
        run_assistant()