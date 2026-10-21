"""
Core Assistant Engine for Suzzy AI Voice Assistant
Handles natural language intent detection, command parsing, and response generation.
"""

import datetime
import os
import random
import re
import urllib.parse
import requests

# ✅ SECURITY FIX: API key is now loaded from environment variable, NOT hardcoded.
# Set OPENWEATHER_API_KEY in your environment or in a .env file (never commit .env to git).
DEFAULT_WEATHER_KEY = os.environ.get("OPENWEATHER_API_KEY", "")

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the computer catch a cold? Because it left a window open!",
    "There are 10 types of people in the world: those who understand binary, and those who don't.",
    "Why was the JavaScript developer sad? Because they didn't know how to 'null' their feelings.",
    "Why do Java programmers wear glasses? Because they don't C#!",
    "What do you call an AI that sings? An Algo-rhythm!"
]

def clean_command(text: str) -> str:
    """Normalize user input command."""
    if not text:
        return ""
    text = text.lower().strip()
    # Remove common filler phrases / wake prefixes if present
    wake_words = ["hey suzy", "hey suzzy", "suzy", "suzzy", "suji", "hey suji", "ok suzzy", "ok suzy"]
    for wake in wake_words:
        if text.startswith(wake):
            text = text[len(wake):].strip()
            # remove leading commas or spaces
            text = text.lstrip(" ,.-")
            break
    return text

def calculate_expression(text: str):
    """Safely calculate simple spoken arithmetic expressions."""
    # Replace spoken words with math symbols
    expr = text.lower()
    replacements = {
        "plus": "+",
        "minus": "-",
        "times": "*",
        "multiplied by": "*",
        "into": "*",
        "x": "*",
        "divided by": "/",
        "over": "/",
        "mod": "%",
        "percent of": "* 0.01 *",
    }
    for word, sym in replacements.items():
        expr = expr.replace(word, sym)

    # Extract only numbers, operators and parentheses
    clean_expr = re.sub(r'[^0-9\+\-\*\/\.\(\) ]', '', expr).strip()
    if clean_expr and any(c.isdigit() for c in clean_expr) and any(c in "+-*/" for c in clean_expr):
        try:
            # Safe evaluation with restricted globals/locals
            # Length guard
            if len(clean_expr) > 50:
                return None
            result = eval(clean_expr, {"__builtins__": None}, {})
            if isinstance(result, (int, float)):
                # Format integer if no decimal part
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 4)
                return f"The answer to {clean_expr} is {result}"
        except Exception:
            return None
    return None

def get_weather_info(city: str, api_key: str = None) -> dict:
    """Fetch current weather data for a specified city."""
    key = api_key if api_key and api_key.strip() else DEFAULT_WEATHER_KEY

    if not key:
        return {
            "success": False,
            "speech": "Weather API key is not configured. Please set the OPENWEATHER_API_KEY environment variable."
        }

    url = f"https://api.openweathermap.org/data/2.5/weather?q={urllib.parse.quote(city)}&appid={key}&units=metric"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("cod") == 200:
            temp = round(data["main"]["temp"])
            feels_like = round(data["main"]["feels_like"])
            desc = data["weather"][0]["description"].capitalize()
            weather_main = data["weather"][0]["main"]
            humidity = data["main"]["humidity"]
            wind_speed = round(data["wind"]["speed"] * 3.6, 1) # km/h
            city_name = data.get("name", city.title())
            country = data.get("sys", {}).get("country", "")

            speech = (f"The temperature in {city_name} is currently {temp} degrees Celsius "
                      f"with {desc}. Humidity is {humidity} percent.")

            return {
                "success": True,
                "city": city_name,
                "country": country,
                "temp": temp,
                "feels_like": feels_like,
                "description": desc,
                "main": weather_main,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "speech": speech
            }
        else:
            message = data.get("message", "City not found")
            return {
                "success": False,
                "speech": f"Sorry, I couldn't find the weather for {city}. {message.capitalize()}."
            }
    except Exception as e:
        return {
            "success": False,
            "speech": "I am having trouble connecting to the weather service right now. Please check your internet connection."
        }

def process_command(raw_command: str, weather_api_key: str = None) -> dict:
    """
    Parses user command and determines appropriate speech response,
    browser action, and display details.
    """
    if not raw_command or not raw_command.strip():
        return {
            "command": "",
            "speech_response": "I didn't catch that. Could you please speak again?",
            "action_type": "none",
            "url": None,
            "status": "warning"
        }

    raw = raw_command.strip()
    cmd = clean_command(raw)

    # 1. WHATSAPP
    if "whatsapp" in cmd:
        # Check if user said "send whatsapp message to ..." or just "open whatsapp"
        return {
            "command": raw,
            "speech_response": "Opening WhatsApp Web for you.",
            "action_type": "open_url",
            "url": "https://web.whatsapp.com",
            "action_label": "WhatsApp Web",
            "status": "success",
            "icon": "💬"
        }

    # 2. YOUTUBE
    if "youtube" in cmd:
        # Check if user wants to play or search something on youtube
        # e.g., "play shape of you on youtube" or "youtube search lofi hip hop"
        search_match = re.search(r'(?:play|search|look for|find)\s+(.*?)\s+(?:on|in)?\s*youtube', cmd)
        if not search_match:
            search_match = re.search(r'youtube\s+(?:play|search|for)\s+(.*)', cmd)

        if search_match:
            query = search_match.group(1).strip()
            encoded_query = urllib.parse.quote_plus(query)
            return {
                "command": raw,
                "speech_response": f"Playing {query} on YouTube.",
                "action_type": "open_url",
                "url": f"https://www.youtube.com/results?search_query={encoded_query}",
                "action_label": f"YouTube: {query}",
                "status": "success",
                "icon": "▶️"
            }
        else:
            return {
                "command": raw,
                "speech_response": "Opening YouTube.",
                "action_type": "open_url",
                "url": "https://www.youtube.com",
                "action_label": "YouTube",
                "status": "success",
                "icon": "▶️"
            }

    # 3. TIME (use word boundary so 'times' in math doesn't trigger time)
    if re.search(r'\b(time|clock)\b', cmd) or any(phrase in cmd for phrase in ["what time is it", "current time", "tell me time"]):
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        speech_choices = [
            f"The time is {time_str}.",
            f"It's {time_str} right now.",
            f"Currently, the time is {time_str}."
        ]
        return {
            "command": raw,
            "speech_response": random.choice(speech_choices),
            "action_type": "time",
            "display_data": {"time": time_str, "date": now.strftime("%A, %d %B %Y")},
            "status": "success",
            "icon": "⏰"
        }

    # 4. DATE
    if any(phrase in cmd for phrase in ["date", "today's date", "what is today", "day is it"]):
        now = datetime.datetime.now()
        date_str = now.strftime("%A, %d %B %Y")
        return {
            "command": raw,
            "speech_response": f"Today is {date_str}.",
            "action_type": "date",
            "display_data": {"date": date_str},
            "status": "success",
            "icon": "📅"
        }

    # 5. GOOGLE & GENERAL SEARCH
    if cmd.startswith("search ") or "search for " in cmd or "google search " in cmd or cmd.startswith("google "):
        query = cmd
        for prefix in ["google search for ", "google search ", "search google for ", "search for ", "search ", "google "]:
            if query.startswith(prefix):
                query = query[len(prefix):]
                break
        query = query.strip()
        encoded = urllib.parse.quote_plus(query)
        return {
            "command": raw,
            "speech_response": f"Here are the Google search results for {query}.",
            "action_type": "open_url",
            "url": f"https://www.google.com/search?q={encoded}",
            "action_label": f"Google Search: {query}",
            "status": "success",
            "icon": "🔍"
        }

    if "google" in cmd and "open" in cmd:
        return {
            "command": raw,
            "speech_response": "Opening Google.",
            "action_type": "open_url",
            "url": "https://www.google.com",
            "action_label": "Google",
            "status": "success",
            "icon": "🌐"
        }

    # 6. POPULAR SITES / APPS
    site_mappings = {
        "github": ("https://github.com", "Opening GitHub.", "🐙"),
        "gmail": ("https://mail.google.com", "Opening Gmail.", "📧"),
        "email": ("https://mail.google.com", "Opening your email inbox.", "📧"),
        "instagram": ("https://www.instagram.com", "Opening Instagram.", "📸"),
        "spotify": ("https://open.spotify.com", "Opening Spotify.", "🎵"),
        "linkedin": ("https://www.linkedin.com", "Opening LinkedIn.", "💼"),
        "twitter": ("https://x.com", "Opening Twitter.", "🐦"),
        "facebook": ("https://www.facebook.com", "Opening Facebook.", "👥"),
        "wikipedia": ("https://www.wikipedia.org", "Opening Wikipedia.", "📚"),
        "chatgpt": ("https://chatgpt.com", "Opening ChatGPT.", "🤖"),
        "maps": ("https://maps.google.com", "Opening Google Maps.", "🗺️"),
        "netflix": ("https://www.netflix.com", "Opening Netflix.", "🎬")
    }

    for site_key, (site_url, site_speech, site_icon) in site_mappings.items():
        if site_key in cmd:
            return {
                "command": raw,
                "speech_response": site_speech,
                "action_type": "open_url",
                "url": site_url,
                "action_label": site_key.capitalize(),
                "status": "success",
                "icon": site_icon
            }

    # 7. WEATHER
    if any(word in cmd for word in ["weather", "whether", "temperature", "climate", "forecast"]):
        # Extract city name if present
        # e.g., "weather in Delhi", "temperature of London", "how is weather in New York"
        city = None
        city_match = re.search(r'(?:in|of|at|for)\s+([a-zA-Z\s]+)', cmd)
        if city_match:
            city = city_match.group(1).strip()
            # Clean words like "today", "tomorrow"
            city = re.sub(r'\b(today|now|right now|currently|please)\b', '', city).strip()

        if not city:
            # Default city or ask user
            city = "Delhi"

        weather_res = get_weather_info(city, weather_api_key)
        return {
            "command": raw,
            "speech_response": weather_res["speech"],
            "action_type": "weather",
            "display_data": weather_res,
            "status": "success" if weather_res.get("success") else "warning",
            "icon": "🌤️"
        }

    # 8. MATH & CALCULATION
    if any(term in cmd for term in ["calculate", "what is", "evaluate", "plus", "minus", "times", "multiplied by", "divided by"]):
        math_ans = calculate_expression(cmd)
        if math_ans:
            return {
                "command": raw,
                "speech_response": math_ans,
                "action_type": "calculation",
                "display_data": {"result": math_ans},
                "status": "success",
                "icon": "🧮"
            }

    # 9. JOKES
    if "joke" in cmd or "make me laugh" in cmd or "funny" in cmd:
        joke = random.choice(JOKES)
        return {
            "command": raw,
            "speech_response": joke,
            "action_type": "joke",
            "status": "success",
            "icon": "😂"
        }

    # 10. GREETINGS & IDENTITY
    if any(phrase in cmd for phrase in ["who are you", "what is your name", "what are you", "introduce yourself"]):
        intro = ("I am Suzzy, your intelligent AI voice assistant! "
                 "I can open WhatsApp, YouTube, Google, tell you the time, date, weather, "
                 "perform calculations, tell jokes, and search the web upon your voice command.")
        return {
            "command": raw,
            "speech_response": intro,
            "action_type": "identity",
            "status": "success",
            "icon": "✨"
        }

    if any(phrase in cmd for phrase in ["hello", "hi", "hey", "good morning", "good evening", "good afternoon"]):
        greetings = [
            "Hello! How can I help you today?",
            "Hey there! Ready for your voice command.",
            "Hi! Ask me to open WhatsApp, YouTube, check time, or anything you like!"
        ]
        return {
            "command": raw,
            "speech_response": random.choice(greetings),
            "action_type": "greeting",
            "status": "success",
            "icon": "👋"
        }

    # 11. EXIT / GOODBYE
    if any(phrase in cmd for phrase in ["bye", "goodbye", "exit", "quit", "see you", "shut down", "sleep"]):
        return {
            "command": raw,
            "speech_response": "Goodbye! Have a great day ahead. Call me whenever you need help!",
            "action_type": "exit",
            "status": "info",
            "icon": "👋"
        }

    # 12. HELP
    if any(phrase in cmd for phrase in ["help", "what can you do", "commands", "features"]):
        help_speech = ("You can tell me to: Open WhatsApp, Open YouTube, What is the time, "
                       "What is today's date, Weather in Mumbai, Search Python on Google, "
                       "Tell me a joke, or calculate numbers.")
        return {
            "command": raw,
            "speech_response": help_speech,
            "action_type": "help",
            "status": "info",
            "icon": "💡"
        }

    # 13. FALLBACK: GENERAL QUERY -> SEARCH GOOGLE
    encoded = urllib.parse.quote_plus(raw)
    return {
        "command": raw,
        "speech_response": f"I couldn't find a direct command for that, so I searched Google for {raw}.",
        "action_type": "open_url",
        "url": f"https://www.google.com/search?q={encoded}",
        "action_label": f"Google Search: {raw}",
        "status": "info",
        "icon": "🔎"
    }
