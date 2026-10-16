import streamlit as st
import datetime
import io
import time
import requests
import speech_recognition as sr
from gtts import gTTS
import streamlit.components.v1 as components
from assistant_core import process_command, DEFAULT_WEATHER_KEY

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Suzzy AI - Voice Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- CUSTOM CSS STYLING -----------------
st.markdown("""
<style>
    /* Main container styling */
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        background-color: #1e293b;
        color: #38bdf8;
        border: 1px solid #0284c7;
    }
    .action-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    .history-card {
        background: #1e293b;
        border-left: 4px solid #6366f1;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .command-chip {
        display: inline-block;
        background: #334155;
        color: #f1f5f9;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 4px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE -----------------
if "history" not in st.session_state:
    st.session_state.history = [
        {
            "timestamp": datetime.datetime.now().strftime("%I:%M %p"),
            "command": "Hey Suzzy",
            "speech_response": "Hello! I am Suzzy, your AI voice assistant. Say 'Open WhatsApp', 'Open YouTube', or ask for the time!",
            "action_type": "greeting",
            "icon": "✨",
            "url": None
        }
    ]

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# ----------------- AUDIO GENERATOR HELPER -----------------
def generate_speech_audio(text: str, tld: str = "co.in") -> bytes:
    """Generates MP3 audio bytes using gTTS."""
    try:
        tts = gTTS(text=text, lang="en", tld=tld, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        return b""

def transcribe_audio_file(audio_file) -> str:
    """Transcribes an uploaded or recorded audio file using SpeechRecognition."""
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="en-IN")
            return text
    except sr.UnknownValueError:
        return "Could not understand audio. Please speak clearly."
    except sr.RequestError:
        return "Network error while connecting to speech recognition service."
    except Exception as e:
        return f"Error processing audio: {str(e)}"

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("### 🎙️ **Suzzy Assistant Settings**")
    
    st.info("💡 **Voice Assistant for Web & Mobile**\nSay commands to open WhatsApp, YouTube, check time, weather, and more!")
    
    accent = st.selectbox(
        "Voice Accent / Dialect",
        options=["Indian English (co.in)", "US English (com)", "UK English (co.uk)", "Australian (com.au)"],
        index=0
    )
    tld_map = {
        "Indian English (co.in)": "co.in",
        "US English (com)": "com",
        "UK English (co.uk)": "co.uk",
        "Australian (com.au)": "com.au"
    }
    selected_tld = tld_map[accent]

    weather_key = st.text_input(
        "OpenWeatherMap API Key",
        value=DEFAULT_WEATHER_KEY,
        type="password",
        help="Optional: Enter custom API key from openweathermap.org"
    )

    st.markdown("---")
    st.markdown("### ⚡ **Common Voice Commands**")
    st.markdown("""
    - 💬 **"Open WhatsApp"** → Opens WhatsApp Web
    - ▶️ **"Open YouTube"** → Opens YouTube
    - 🎵 **"Play Believer on YouTube"** → Searches & plays song
    - ⏰ **"What is the time?"** → Speaks current time
    - 📅 **"What is today's date?"** → Speaks current date
    - 🌤️ **"Weather in Delhi"** → Temperature & climate
    - 🔍 **"Search Quantum Computing"** → Google search
    - 🧮 **"What is 25 times 40?"** → Solves math
    - 😂 **"Tell me a joke"** → Tells a fun joke
    - 🐙 **"Open GitHub"** / 📧 **"Open Gmail"**
    """)

    st.markdown("---")
    if st.button("🗑️ Clear Conversation History", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #64748b; font-size: 0.8rem;'>
        Project: <b>Suzzy AI Voice Assistant</b><br>
        Deployed on Streamlit
    </div>
    """, unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.markdown("<h1 class='main-title'>🎙️ Suzzy AI Voice Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Speak to Suzzy to open WhatsApp, YouTube, tell time, check weather, search, and more!</p>", unsafe_allow_html=True)

# ----------------- TABS -----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🔴 Live Browser Voice (Instant)",
    "🎙️ Streamlit Audio Recorder",
    "💬 Text Commands",
    "🚀 Deployment Guide"
])

# ----------------- TAB 1: LIVE BROWSER VOICE ASSISTANT -----------------
with tab1:
    st.markdown("""
    <div style='background: #1e293b; padding: 12px 18px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #38bdf8;'>
        <b>✨ Real-Time Browser Voice Mode:</b> Works directly in Chrome, Edge, Safari, and Android. 
        Click <b>"Start Listening"</b> below and speak your command like <b>"Open WhatsApp"</b>, <b>"Open YouTube"</b>, or <b>"What is the time"</b>.
        Suzzy will respond with voice and open the app/website directly in your browser!
    </div>
    """, unsafe_allow_html=True)

    # Embed Interactive Web Speech Component
    web_speech_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            * {{
                box-sizing: border-box;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}
            body {{
                background: #0f172a;
                color: #f8fafc;
                margin: 0;
                padding: 16px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }}
            .orb-container {{
                position: relative;
                width: 170px;
                height: 170px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 20px;
            }}
            .orb {{
                width: 130px;
                height: 130px;
                border-radius: 50%;
                background: radial-gradient(circle at 30% 30%, #a855f7, #6366f1, #06b6d4);
                box-shadow: 0 0 35px rgba(99, 102, 241, 0.6), inset 0 0 20px rgba(255, 255, 255, 0.4);
                transition: all 0.3s ease;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 42px;
            }}
            .orb.listening {{
                animation: pulse 1.2s infinite alternate;
                box-shadow: 0 0 65px rgba(236, 72, 153, 0.8), inset 0 0 30px rgba(255, 255, 255, 0.7);
                background: radial-gradient(circle at 30% 30%, #ec4899, #8b5cf6, #3b82f6);
            }}
            .orb.speaking {{
                animation: wave 0.8s infinite alternate;
                box-shadow: 0 0 55px rgba(16, 185, 129, 0.8);
                background: radial-gradient(circle at 30% 30%, #10b981, #06b6d4, #6366f1);
            }}
            @keyframes pulse {{
                0% {{ transform: scale(0.95); }}
                100% {{ transform: scale(1.15); }}
            }}
            @keyframes wave {{
                0% {{ transform: scale(1.0); }}
                100% {{ transform: scale(1.08); filter: hue-rotate(45deg); }}
            }}
            .controls {{
                display: flex;
                gap: 12px;
                margin-bottom: 16px;
                flex-wrap: wrap;
                justify-content: center;
            }}
            .btn {{
                background: #6366f1;
                color: white;
                border: none;
                padding: 10px 22px;
                border-radius: 25px;
                font-weight: 600;
                font-size: 15px;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .btn:hover {{
                background: #4f46e5;
                transform: translateY(-1px);
            }}
            .btn.danger {{
                background: #ef4444;
            }}
            .status-text {{
                font-size: 15px;
                color: #38bdf8;
                font-weight: 600;
                margin-bottom: 12px;
                text-align: center;
                min-height: 22px;
            }}
            .transcript-box {{
                width: 100%;
                max-width: 680px;
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 14px 18px;
                margin-top: 10px;
            }}
            .message-row {{
                margin-bottom: 8px;
                font-size: 14.5px;
                line-height: 1.5;
            }}
            .user-msg {{
                color: #cbd5e1;
            }}
            .user-msg b {{
                color: #38bdf8;
            }}
            .assistant-msg {{
                color: #f1f5f9;
            }}
            .assistant-msg b {{
                color: #a855f7;
            }}
            .action-link-btn {{
                display: inline-block;
                margin-top: 8px;
                background: #10b981;
                color: white;
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }}
            .action-link-btn:hover {{
                background: #059669;
            }}
            .chips-container {{
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
                justify-content: center;
                margin-top: 14px;
            }}
            .sample-chip {{
                background: #334155;
                color: #cbd5e1;
                font-size: 12.5px;
                padding: 5px 12px;
                border-radius: 16px;
                cursor: pointer;
                border: 1px solid #475569;
                transition: 0.2s;
            }}
            .sample-chip:hover {{
                background: #475569;
                color: #fff;
            }}
        </style>
    </head>
    <body>

        <div class="orb-container">
            <div id="voiceOrb" class="orb" onclick="toggleListening()">🎙️</div>
        </div>

        <div id="statusLabel" class="status-text">Click the Orb or "Start Listening" to speak</div>

        <div class="controls">
            <button id="listenBtn" class="btn" onclick="toggleListening()">
                <span>🎙️</span> <span id="btnText">Start Listening</span>
            </button>
            <button class="btn" style="background: #334155;" onclick="stopSpeaking()">
                <span>⏹️</span> Stop Voice
            </button>
        </div>

        <div class="transcript-box" id="transcriptBox">
            <div class="message-row user-msg"><b>You:</b> <span id="userSpeech">Ready for your command...</span></div>
            <div class="message-row assistant-msg"><b>Suzzy:</b> <span id="assistantSpeech">"Hello! Tell me: Open WhatsApp, Open YouTube, or ask what time it is!"</span></div>
            <div id="actionArea"></div>
        </div>

        <div class="chips-container">
            <span class="sample-chip" onclick="simulateCommand('open whatsapp')">💬 Open WhatsApp</span>
            <span class="sample-chip" onclick="simulateCommand('open youtube')">▶️ Open YouTube</span>
            <span class="sample-chip" onclick="simulateCommand('what is the time')">⏰ What is the time</span>
            <span class="sample-chip" onclick="simulateCommand('what is today date')">📅 Today's Date</span>
            <span class="sample-chip" onclick="simulateCommand('weather in Mumbai')">🌤️ Weather in Mumbai</span>
            <span class="sample-chip" onclick="simulateCommand('tell me a joke')">😂 Tell me a joke</span>
            <span class="sample-chip" onclick="simulateCommand('what is 50 times 8')">🧮 What is 50 * 8</span>
        </div>

        <script>
            let recognition = null;
            let isListening = false;
            let synth = window.speechSynthesis;

            // Initialize Speech Recognition
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

            if (SpeechRecognition) {{
                recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = true;
                recognition.lang = 'en-IN';

                recognition.onstart = () => {{
                    isListening = true;
                    document.getElementById('voiceOrb').className = "orb listening";
                    document.getElementById('statusLabel').innerText = "🔴 Listening... Speak now!";
                    document.getElementById('btnText').innerText = "Stop Listening";
                    document.getElementById('listenBtn').className = "btn danger";
                }};

                recognition.onresult = (event) => {{
                    let currentTranscript = "";
                    for (let i = event.resultIndex; i < event.results.length; ++i) {{
                        currentTranscript += event.results[i][0].transcript;
                    }}
                    document.getElementById('userSpeech').innerText = currentTranscript;

                    if (event.results[0].isFinal) {{
                        handleVoiceCommand(currentTranscript);
                    }}
                }};

                recognition.onerror = (event) => {{
                    console.error("Speech Recognition Error:", event.error);
                    document.getElementById('statusLabel').innerText = "⚠️ Voice error: " + event.error;
                    resetOrb();
                }};

                recognition.onend = () => {{
                    resetOrb();
                }};
            }} else {{
                document.getElementById('statusLabel').innerHTML = "⚠️ Web Speech API not supported in this iframe/browser. Please use the <b>Streamlit Audio Recorder</b> tab above!";
            }}

            function resetOrb() {{
                isListening = false;
                document.getElementById('voiceOrb').className = "orb";
                document.getElementById('statusLabel').innerText = "Click to speak again";
                document.getElementById('btnText').innerText = "Start Listening";
                document.getElementById('listenBtn').className = "btn";
            }}

            function toggleListening() {{
                if (!recognition) {{
                    alert("Speech Recognition not supported in this browser. Try Chrome/Edge or use the Streamlit Audio Recorder tab.");
                    return;
                }}
                if (isListening) {{
                    recognition.stop();
                }} else {{
                    stopSpeaking();
                    try {{
                        recognition.start();
                    }} catch (e) {{
                        console.error(e);
                    }}
                }}
            }}

            function speakText(text, callback) {{
                if (!synth) return;
                synth.cancel(); // cancel any active speech

                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 1.0;
                utterance.pitch = 1.0;
                utterance.lang = 'en-IN';

                document.getElementById('voiceOrb').className = "orb speaking";
                document.getElementById('statusLabel').innerText = "🔊 Suzzy is speaking...";

                utterance.onend = () => {{
                    resetOrb();
                    if (callback) callback();
                }};

                utterance.onerror = () => {{
                    resetOrb();
                    if (callback) callback();
                }};

                synth.speak(utterance);
            }}

            function stopSpeaking() {{
                if (synth) {{
                    synth.cancel();
                }}
                resetOrb();
            }}

            function handleVoiceCommand(rawText) {{
                const cmd = rawText.toLowerCase().trim();
                const actionArea = document.getElementById('actionArea');
                actionArea.innerHTML = "";
                let response = "";
                let openUrl = null;
                let openLabel = "";

                // 1. WHATSAPP
                if (cmd.includes("whatsapp")) {{
                    response = "Opening WhatsApp Web for you.";
                    openUrl = "https://web.whatsapp.com";
                    openLabel = "💬 Open WhatsApp Web";
                }}
                // 2. YOUTUBE
                else if (cmd.includes("youtube")) {{
                    if (cmd.includes("play") || cmd.includes("search")) {{
                        const query = cmd.replace(/play|search|on youtube|in youtube|youtube/gi, "").trim();
                        response = "Playing " + query + " on YouTube.";
                        openUrl = "https://www.youtube.com/results?search_query=" + encodeURIComponent(query);
                        openLabel = "▶️ Open YouTube: " + query;
                    }} else {{
                        response = "Opening YouTube.";
                        openUrl = "https://www.youtube.com";
                        openLabel = "▶️ Open YouTube";
                    }}
                }}
                // 3. TIME
                else if (cmd.match(/\\btime\\b/) || cmd.includes("clock")) {{
                    const now = new Date();
                    let hours = now.getHours();
                    let minutes = now.getMinutes();
                    const ampm = hours >= 12 ? 'PM' : 'AM';
                    hours = hours % 12;
                    hours = hours ? hours : 12;
                    minutes = minutes < 10 ? '0' + minutes : minutes;
                    const timeStr = hours + ':' + minutes + ' ' + ampm;
                    response = "The current time is " + timeStr + ".";
                }}
                // 4. DATE
                else if (cmd.includes("date") || cmd.includes("today")) {{
                    const now = new Date();
                    const options = {{ weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }};
                    response = "Today is " + now.toLocaleDateString('en-US', options) + ".";
                }}
                // 5. GOOGLE & SEARCH
                else if (cmd.startsWith("search") || cmd.includes("google search")) {{
                    const query = cmd.replace(/search for|search|google search for|google search/gi, "").trim();
                    response = "Searching Google for " + query + ".";
                    openUrl = "https://www.google.com/search?q=" + encodeURIComponent(query);
                    openLabel = "🔍 Google Search: " + query;
                }}
                else if (cmd.includes("google")) {{
                    response = "Opening Google.";
                    openUrl = "https://www.google.com";
                    openLabel = "🌐 Open Google";
                }}
                // 6. POPULAR SITES
                else if (cmd.includes("github")) {{
                    response = "Opening GitHub.";
                    openUrl = "https://github.com";
                    openLabel = "🐙 Open GitHub";
                }}
                else if (cmd.includes("gmail") || cmd.includes("email")) {{
                    response = "Opening your Gmail.";
                    openUrl = "https://mail.google.com";
                    openLabel = "📧 Open Gmail";
                }}
                else if (cmd.includes("instagram")) {{
                    response = "Opening Instagram.";
                    openUrl = "https://www.instagram.com";
                    openLabel = "📸 Open Instagram";
                }}
                else if (cmd.includes("spotify")) {{
                    response = "Opening Spotify.";
                    openUrl = "https://open.spotify.com";
                    openLabel = "🎵 Open Spotify";
                }}
                // 7. WEATHER
                else if (cmd.includes("weather") || cmd.includes("temperature")) {{
                    let city = "Delhi";
                    const match = cmd.match(/(?:in|of|for)\\s+([a-zA-Z\\s]+)/);
                    if (match && match[1]) {{
                        city = match[1].trim();
                    }}
                    fetchWeather(city);
                    return;
                }}
                // 8. JOKES
                else if (cmd.includes("joke") || cmd.includes("funny")) {{
                    const jokes = [
                        "Why do programmers prefer dark mode? Because light attracts bugs!",
                        "Why did the computer catch a cold? Because it left a window open!",
                        "There are 10 types of people in the world: those who understand binary, and those who don't.",
                        "Why do Java programmers wear glasses? Because they don't C-sharp!"
                    ];
                    response = jokes[Math.floor(Math.random() * jokes.length)];
                }}
                // 9. MATH
                else if (cmd.includes("times") || cmd.includes("plus") || cmd.includes("minus") || cmd.includes("divided by")) {{
                    try {{
                        let expr = cmd.replace(/times|into|x/g, "*")
                                      .replace(/plus/g, "+")
                                      .replace(/minus/g, "-")
                                      .replace(/divided by|over/g, "/")
                                      .replace(/[^0-9\\+\\-\\*/\\.\\(\\)]/g, "");
                        const result = Function('"use strict";return (' + expr + ')')();
                        response = "The result is " + result;
                    }} catch(e) {{
                        response = "I couldn't calculate that math expression.";
                    }}
                }}
                // 10. GREETINGS
                else if (cmd.includes("who are you") || cmd.includes("your name")) {{
                    response = "I am Suzzy, your intelligent AI voice assistant. I can open WhatsApp, YouTube, tell the time, and assist you with anything!";
                }}
                else if (cmd.includes("hello") || cmd.includes("hi") || cmd.includes("hey")) {{
                    response = "Hello there! Ready for your command. Say open WhatsApp, open YouTube, or ask what time it is.";
                }}
                else {{
                    response = "Searching Google for " + rawText;
                    openUrl = "https://www.google.com/search?q=" + encodeURIComponent(rawText);
                    openLabel = "🔍 Search: " + rawText;
                }}

                document.getElementById('assistantSpeech').innerText = response;

                // Open URL if applicable
                if (openUrl) {{
                    window.open(openUrl, '_blank');
                    actionArea.innerHTML = `<a href="${{openUrl}}" target="_blank" class="action-link-btn">${{openLabel}} ↗</a>`;
                }}

                // Speak voice out loud
                speakText(response);
            }}

            function fetchWeather(city) {{
                const apiKey = "{DEFAULT_WEATHER_KEY}";
                const url = `https://api.openweathermap.org/data/2.5/weather?q=${{encodeURIComponent(city)}}&appid=${{apiKey}}&units=metric`;
                
                fetch(url)
                    .then(res => res.json())
                    .then(data => {{
                        let speech = "";
                        if (data.cod === 200) {{
                            const temp = Math.round(data.main.temp);
                            const desc = data.weather[0].description;
                            speech = `The temperature in ${{city}} is ${{temp}} degrees Celsius with ${{desc}}.`;
                        }} else {{
                            speech = `Sorry, I couldn't find the weather for ${{city}}.`;
                        }}
                        document.getElementById('assistantSpeech').innerText = speech;
                        speakText(speech);
                    }})
                    .catch(err => {{
                        const speech = "Unable to fetch weather right now. Check internet connection.";
                        document.getElementById('assistantSpeech').innerText = speech;
                        speakText(speech);
                    }});
            }}

            function simulateCommand(text) {{
                document.getElementById('userSpeech').innerText = text;
                handleVoiceCommand(text);
            }}
        </script>
    </body>
    </html>
    """

    components.html(web_speech_html, height=480, scrolling=False)

# ----------------- TAB 2: STREAMLIT AUDIO RECORDER (Server-side transcription + gTTS) -----------------
with tab2:
    st.markdown("### 🎙️ Record Voice with Streamlit Recorder")
    st.markdown("Click below to record your voice. Say **'Open WhatsApp'**, **'Open YouTube'**, **'What is the time'**, or **'Weather in Mumbai'**.")

    col_rec, col_info = st.columns([1, 1])

    with col_rec:
        audio_prompt = st.audio_input("Record your voice command:")

        if audio_prompt is not None and audio_prompt != st.session_state.last_processed_audio:
            st.session_state.last_processed_audio = audio_prompt
            with st.spinner("🎧 Transcribing audio with Google Speech Recognition..."):
                transcribed_text = transcribe_audio_file(audio_prompt)

            if transcribed_text and not transcribed_text.startswith("Could not understand") and not transcribed_text.startswith("Error"):
                st.success(f"🗣️ **You said:** *\"{transcribed_text}\"*")
                
                # Process command through core engine
                result = process_command(transcribed_text, weather_api_key=weather_key)
                
                # Generate spoken audio
                with st.spinner("🔊 Generating voice response..."):
                    audio_bytes = generate_speech_audio(result["speech_response"], tld=selected_tld)

                # Append to history
                st.session_state.history.insert(0, {
                    "timestamp": datetime.datetime.now().strftime("%I:%M %p"),
                    "command": transcribed_text,
                    "speech_response": result["speech_response"],
                    "action_type": result.get("action_type"),
                    "icon": result.get("icon", "🤖"),
                    "url": result.get("url")
                })

                # Display Action Card
                st.markdown(f"""
                <div class='action-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span style='font-size: 1.5rem;'>{result.get('icon', '🤖')}</span>
                        <span class='status-badge'>{result.get('action_type', 'command').upper()}</span>
                    </div>
                    <h3 style='margin-top: 10px; color: #f8fafc;'>{result['speech_response']}</h3>
                </div>
                """, unsafe_allow_html=True)

                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)

                if result.get("url"):
                    st.link_button(
                        f"👉 Launch {result.get('action_label', 'Website')} Now ↗",
                        result["url"],
                        type="primary",
                        use_container_width=True
                    )
            else:
                st.warning(transcribed_text)

    with col_info:
        st.markdown("#### 💡 Quick Action Triggers")
        st.markdown("Test instant voice commands directly:")
        
        qc1, qc2 = st.columns(2)
        with qc1:
            if st.button("💬 Open WhatsApp Web", use_container_width=True):
                res = process_command("open whatsapp")
                st.session_state.history.insert(0, {
                    "timestamp": datetime.datetime.now().strftime("%I:%M %p"),
                    "command": "open whatsapp",
                    "speech_response": res["speech_response"],
                    "action_type": "open_url",
                    "icon": "💬",
                    "url": res["url"]
                })
                st.rerun()

            if st.button("⏰ What is the time?", use_container_width=True):
                res = process_command("what is the time")
                st.session_state.history.insert(0, {
                    "timestamp": datetime.datetime.now().strftime("%I:%M %p"),
                    "command": "what is the time",
                    "speech_response": res["speech_response"],
                    "action_type": "time",
                    "icon": "⏰",
                    "url": None
                })
                st.rerun()

        with qc2:
            if st.button("▶️ Open YouTube", use_container_width=True):
                res = process_command("open youtube")
                st.session_state.history.insert(0, {
                    "timestamp": datetime.datetime.now().strftime("%I:%M %p"),
                    "command": "open youtube",
                    "speech_response": res["speech_response"],
                    "action_type": "open_url",
                    "icon": "▶️",
                    "url": res["url"]
                })
                st.rerun()

            if st.button("🌤️ Weather in Mumbai", use_container_width=True):
                res = process_command("weather in Mumbai", weather_api_key=weather_key)
                st.session_state.history.insert(0, {
                    "timestamp": datetime.datetime.now().strftime("%I:%M %p"),
                    "command": "weather in Mumbai",
                    "speech_response": res["speech_response"],
                    "action_type": "weather",
                    "icon": "🌤️",
                    "url": None
                })
                st.rerun()

# ----------------- TAB 3: TEXT COMMAND CONSOLE -----------------
with tab3:
    st.markdown("### 💬 Type Command to Suzzy")
    text_col1, text_col2 = st.columns([4, 1])
    
    with text_col1:
        text_input = st.text_input("Type your command (e.g. 'open whatsapp', 'play coldplay on youtube', 'what time is it'):", key="text_cmd_input")
    
    with text_col2:
        st.write("")
        st.write("")
        send_btn = st.button("🚀 Execute", use_container_width=True)

    if (send_btn or text_input) and text_input.strip():
        with st.spinner("Processing..."):
            res = process_command(text_input, weather_api_key=weather_key)
            audio_bytes = generate_speech_audio(res["speech_response"], tld=selected_tld)

            st.session_state.history.insert(0, {
                "timestamp": datetime.datetime.now().strftime("%I:%M %p"),
                "command": text_input,
                "speech_response": res["speech_response"],
                "action_type": res.get("action_type"),
                "icon": res.get("icon", "🤖"),
                "url": res.get("url")
            })

            st.markdown(f"""
            <div class='action-card'>
                <span style='font-size: 1.5rem;'>{res.get('icon', '🤖')}</span>
                <span class='status-badge'>{res.get('action_type', 'command').upper()}</span>
                <h3 style='margin-top: 10px; color: #f8fafc;'>{res['speech_response']}</h3>
            </div>
            """, unsafe_allow_html=True)

            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)

            if res.get("url"):
                st.link_button(
                    f"👉 Open {res.get('action_label', 'Website')} ↗",
                    res["url"],
                    type="primary"
                )

# ----------------- TAB 4: DEPLOYMENT GUIDE -----------------
with tab4:
    st.markdown("""
    ## 🚀 How to Deploy This Project on Streamlit Cloud (Free & Easy)

    Deploying **Suzzy Voice Assistant** to Streamlit Community Cloud allows anyone in the world to access your AI voice assistant from their laptop, iPhone, or Android phone!

    ### 📋 Step-by-Step Instructions:

    #### 1. Push code to your GitHub Repository
    Open your terminal in the project directory and run:
    ```bash
    git add .
    git commit -m "Add full Streamlit Voice Assistant with WhatsApp, YouTube, and Time support"
    git push origin main
    ```

    #### 2. Open Streamlit Community Cloud
    - Go to **[share.streamlit.io](https://share.streamlit.io)**
    - Sign in with your GitHub account.

    #### 3. Create a New App
    - Click **"Create app"**
    - Select your repository: `Saieshwar-web/suzzy-voice-assistant`
    - Branch: `main`
    - Main file path: `app.py`
    - App URL: Choose a custom sub-domain (e.g. `suzzy-voice-assistant.streamlit.app`)
    - Click **"Deploy!"**

    #### 4. Requirements File (`requirements.txt`)
    Ensure your `requirements.txt` includes:
    ```text
    streamlit>=1.35.0
    gTTS>=2.5.0
    SpeechRecognition>=3.10.0
    requests>=2.28.0
    ```

    #### 5. Mobile & Desktop Browser Mic Permissions
    - When accessing the deployed web app, your browser will prompt:
      `"Allow suzzy-voice-assistant.streamlit.app to use your microphone?"`
    - Click **"Allow"** to enable real-time speech recognition and voice feedback!
    """)

# ----------------- ACTIVITY & CONVERSATION LOG -----------------
st.markdown("---")
st.markdown("### 📜 **Activity & Speech History**")

if st.session_state.history:
    for item in st.session_state.history:
        with st.container():
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"""
                <div class='history-card'>
                    <div style='display: flex; justify-content: space-between;'>
                        <b>You said:</b> <i>"{item['command']}"</i>
                        <span style='color: #94a3b8; font-size: 0.8rem;'>{item['timestamp']}</span>
                    </div>
                    <div style='margin-top: 6px; color: #e2e8f0;'>
                        <b>{item.get('icon', '🤖')} Suzzy:</b> {item['speech_response']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                if item.get("url"):
                    st.link_button("Launch ↗", item["url"], use_container_width=True)
else:
    st.info("No conversation history yet. Speak or type a command above!")
